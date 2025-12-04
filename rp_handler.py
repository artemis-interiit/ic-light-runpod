"""
RunPod Serverless Handler for IC-Light Model
Handles relighting requests with foreground and background conditioning
"""

import os
import math
import base64
import io
import runpod
import numpy as np
import torch
import safetensors.torch as sf
from PIL import Image
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from diffusers import AutoencoderKL, UNet2DConditionModel, DDIMScheduler, EulerAncestralDiscreteScheduler, DPMSolverMultistepScheduler
from diffusers.models.attention_processor import AttnProcessor2_0
from transformers import CLIPTextModel, CLIPTokenizer
from briarmbg import BriaRMBG
from torch.hub import download_url_to_file

# Global variables for model components
device = None
tokenizer = None
text_encoder = None
vae = None
unet = None
rmbg = None
t2i_pipe = None
i2i_pipe = None

def download_models():
    """Download required model files"""
    model_path = './models/iclight_sd15_fbc.safetensors'
    os.makedirs('./models', exist_ok=True)
    
    if not os.path.exists(model_path):
        print("Downloading IC-Light model...")
        download_url_to_file(
            url='https://huggingface.co/lllyasviel/ic-light/resolve/main/iclight_sd15_fbc.safetensors',
            dst=model_path
        )
        print("Model downloaded successfully!")
    return model_path

def initialize_models():
    """Initialize all models and pipelines"""
    global device, tokenizer, text_encoder, vae, unet, rmbg, t2i_pipe, i2i_pipe
    
    print("Initializing models...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load base model
    sd15_name = 'stablediffusionapi/realistic-vision-v51'
    
    print("Loading tokenizer and text encoder...")
    tokenizer = CLIPTokenizer.from_pretrained(sd15_name, subfolder="tokenizer")
    text_encoder = CLIPTextModel.from_pretrained(sd15_name, subfolder="text_encoder")
    
    print("Loading VAE...")
    vae = AutoencoderKL.from_pretrained(sd15_name, subfolder="vae")
    
    print("Loading UNet...")
    unet = UNet2DConditionModel.from_pretrained(sd15_name, subfolder="unet")
    
    print("Loading background removal model...")
    rmbg = BriaRMBG.from_pretrained("briaai/RMBG-1.4")
    
    # Modify UNet for IC-Light
    print("Modifying UNet for IC-Light...")
    with torch.no_grad():
        new_conv_in = torch.nn.Conv2d(12, unet.conv_in.out_channels, 
                                      unet.conv_in.kernel_size, 
                                      unet.conv_in.stride, 
                                      unet.conv_in.padding)
        new_conv_in.weight.zero_()
        new_conv_in.weight[:, :4, :, :].copy_(unet.conv_in.weight)
        new_conv_in.bias = unet.conv_in.bias
        unet.conv_in = new_conv_in
    
    # Hook UNet forward
    unet_original_forward = unet.forward
    
    def hooked_unet_forward(sample, timestep, encoder_hidden_states, **kwargs):
        c_concat = kwargs['cross_attention_kwargs']['concat_conds'].to(sample)
        c_concat = torch.cat([c_concat] * (sample.shape[0] // c_concat.shape[0]), dim=0)
        new_sample = torch.cat([sample, c_concat], dim=1)
        kwargs['cross_attention_kwargs'] = {}
        return unet_original_forward(new_sample, timestep, encoder_hidden_states, **kwargs)
    
    unet.forward = hooked_unet_forward
    
    # Load IC-Light weights
    print("Loading IC-Light weights...")
    model_path = download_models()
    sd_offset = sf.load_file(model_path)
    sd_origin = unet.state_dict()
    sd_merged = {k: sd_origin[k] + sd_offset[k] for k in sd_origin.keys()}
    unet.load_state_dict(sd_merged, strict=True)
    del sd_offset, sd_origin, sd_merged
    
    # Move models to device
    print("Moving models to device...")
    text_encoder = text_encoder.to(device=device, dtype=torch.float16)
    vae = vae.to(device=device, dtype=torch.bfloat16)
    unet = unet.to(device=device, dtype=torch.float16)
    rmbg = rmbg.to(device=device, dtype=torch.float32)
    
    # Set attention processors
    unet.set_attn_processor(AttnProcessor2_0())
    vae.set_attn_processor(AttnProcessor2_0())
    
    # Create scheduler
    dpmpp_2m_sde_karras_scheduler = DPMSolverMultistepScheduler(
        num_train_timesteps=1000,
        beta_start=0.00085,
        beta_end=0.012,
        algorithm_type="sde-dpmsolver++",
        use_karras_sigmas=True,
        steps_offset=1
    )
    
    # Create pipelines
    print("Creating pipelines...")
    t2i_pipe = StableDiffusionPipeline(
        vae=vae,
        text_encoder=text_encoder,
        tokenizer=tokenizer,
        unet=unet,
        scheduler=dpmpp_2m_sde_karras_scheduler,
        safety_checker=None,
        requires_safety_checker=False,
        feature_extractor=None,
        image_encoder=None
    )
    
    i2i_pipe = StableDiffusionImg2ImgPipeline(
        vae=vae,
        text_encoder=text_encoder,
        tokenizer=tokenizer,
        unet=unet,
        scheduler=dpmpp_2m_sde_karras_scheduler,
        safety_checker=None,
        requires_safety_checker=False,
        feature_extractor=None,
        image_encoder=None
    )
    
    print("Models initialized successfully!")

@torch.inference_mode()
def encode_prompt_inner(txt: str):
    """Encode text prompt"""
    max_length = tokenizer.model_max_length
    chunk_length = tokenizer.model_max_length - 2
    id_start = tokenizer.bos_token_id
    id_end = tokenizer.eos_token_id
    id_pad = id_end

    def pad(x, p, i):
        return x[:i] if len(x) >= i else x + [p] * (i - len(x))

    tokens = tokenizer(txt, truncation=False, add_special_tokens=False)["input_ids"]
    chunks = [[id_start] + tokens[i: i + chunk_length] + [id_end] for i in range(0, len(tokens), chunk_length)]
    chunks = [pad(ck, id_pad, max_length) for ck in chunks]

    token_ids = torch.tensor(chunks).to(device=device, dtype=torch.int64)
    conds = text_encoder(token_ids).last_hidden_state

    return conds

@torch.inference_mode()
def encode_prompt_pair(positive_prompt, negative_prompt):
    """Encode positive and negative prompts"""
    c = encode_prompt_inner(positive_prompt)
    uc = encode_prompt_inner(negative_prompt)

    c_len = float(len(c))
    uc_len = float(len(uc))
    max_count = max(c_len, uc_len)
    c_repeat = int(math.ceil(max_count / c_len))
    uc_repeat = int(math.ceil(max_count / uc_len))
    max_chunk = max(len(c), len(uc))

    c = torch.cat([c] * c_repeat, dim=0)[:max_chunk]
    uc = torch.cat([uc] * uc_repeat, dim=0)[:max_chunk]

    c = torch.cat([p[None, ...] for p in c], dim=1)
    uc = torch.cat([p[None, ...] for p in uc], dim=1)

    return c, uc

@torch.inference_mode()
def pytorch2numpy(imgs, quant=True):
    """Convert PyTorch tensors to numpy arrays"""
    results = []
    for x in imgs:
        y = x.movedim(0, -1)
        if quant:
            y = y * 127.5 + 127.5
            y = y.detach().float().cpu().numpy().clip(0, 255).astype(np.uint8)
        else:
            y = y * 0.5 + 0.5
            y = y.detach().float().cpu().numpy().clip(0, 1).astype(np.float32)
        results.append(y)
    return results

@torch.inference_mode()
def numpy2pytorch(imgs):
    """Convert numpy arrays to PyTorch tensors"""
    h = torch.from_numpy(np.stack(imgs, axis=0)).float() / 127.0 - 1.0
    h = h.movedim(-1, 1)
    return h

def resize_and_center_crop(image, target_width, target_height):
    """Resize and center crop image"""
    pil_image = Image.fromarray(image)
    original_width, original_height = pil_image.size
    scale_factor = max(target_width / original_width, target_height / original_height)
    resized_width = int(round(original_width * scale_factor))
    resized_height = int(round(original_height * scale_factor))
    resized_image = pil_image.resize((resized_width, resized_height), Image.LANCZOS)
    left = (resized_width - target_width) / 2
    top = (resized_height - target_height) / 2
    right = (resized_width + target_width) / 2
    bottom = (resized_height + target_height) / 2
    cropped_image = resized_image.crop((left, top, right, bottom))
    return np.array(cropped_image)

def resize_without_crop(image, target_width, target_height):
    """Resize image without cropping"""
    pil_image = Image.fromarray(image)
    resized_image = pil_image.resize((target_width, target_height), Image.LANCZOS)
    return np.array(resized_image)

@torch.inference_mode()
def run_rmbg(img, sigma=0.0):
    """Run background removal"""
    H, W, C = img.shape
    assert C == 3
    k = (256.0 / float(H * W)) ** 0.5
    feed = resize_without_crop(img, int(64 * round(W * k)), int(64 * round(H * k)))
    feed = numpy2pytorch([feed]).to(device=device, dtype=torch.float32)
    alpha = rmbg(feed)[0][0]
    alpha = torch.nn.functional.interpolate(alpha, size=(H, W), mode="bilinear")
    alpha = alpha.movedim(1, -1)[0]
    alpha = alpha.detach().float().cpu().numpy().clip(0, 1)
    result = 127 + (img.astype(np.float32) - 127 + sigma) * alpha
    return result.clip(0, 255).astype(np.uint8), alpha

def decode_base64_image(base64_string):
    """Decode base64 string to numpy array"""
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    return np.array(image)

def encode_image_to_base64(image_array):
    """Encode numpy array to base64 string"""
    image = Image.fromarray(image_array)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@torch.inference_mode()
def process_relight(input_fg, input_bg, prompt, image_width=512, image_height=640, 
                   num_samples=1, seed=12345, steps=20, 
                   a_prompt='best quality', 
                   n_prompt='lowres, bad anatomy, bad hands, cropped, worst quality',
                   cfg=7.0, highres_scale=1.5, highres_denoise=0.5, 
                   bg_source='grey'):
    """Process relighting with foreground and background"""
    
    # Handle background source
    if bg_source == 'grey':
        input_bg = np.zeros(shape=(image_height, image_width, 3), dtype=np.uint8) + 64
    elif bg_source == 'left':
        gradient = np.linspace(224, 32, image_width)
        image = np.tile(gradient, (image_height, 1))
        input_bg = np.stack((image,) * 3, axis=-1).astype(np.uint8)
    elif bg_source == 'right':
        gradient = np.linspace(32, 224, image_width)
        image = np.tile(gradient, (image_height, 1))
        input_bg = np.stack((image,) * 3, axis=-1).astype(np.uint8)
    elif bg_source == 'top':
        gradient = np.linspace(224, 32, image_height)[:, None]
        image = np.tile(gradient, (1, image_width))
        input_bg = np.stack((image,) * 3, axis=-1).astype(np.uint8)
    elif bg_source == 'bottom':
        gradient = np.linspace(32, 224, image_height)[:, None]
        image = np.tile(gradient, (1, image_width))
        input_bg = np.stack((image,) * 3, axis=-1).astype(np.uint8)
    
    # Remove background from foreground
    input_fg, matting = run_rmbg(input_fg)
    
    rng = torch.Generator(device=device).manual_seed(seed)
    
    fg = resize_and_center_crop(input_fg, image_width, image_height)
    bg = resize_and_center_crop(input_bg, image_width, image_height)
    concat_conds = numpy2pytorch([fg, bg]).to(device=vae.device, dtype=vae.dtype)
    concat_conds = vae.encode(concat_conds).latent_dist.mode() * vae.config.scaling_factor
    concat_conds = torch.cat([c[None, ...] for c in concat_conds], dim=1)
    
    conds, unconds = encode_prompt_pair(positive_prompt=prompt + ', ' + a_prompt, 
                                       negative_prompt=n_prompt)
    
    # First pass
    latents = t2i_pipe(
        prompt_embeds=conds,
        negative_prompt_embeds=unconds,
        width=image_width,
        height=image_height,
        num_inference_steps=steps,
        num_images_per_prompt=num_samples,
        generator=rng,
        output_type='latent',
        guidance_scale=cfg,
        cross_attention_kwargs={'concat_conds': concat_conds},
    ).images.to(vae.dtype) / vae.config.scaling_factor
    
    pixels = vae.decode(latents).sample
    pixels = pytorch2numpy(pixels)
    pixels = [resize_without_crop(
        image=p,
        target_width=int(round(image_width * highres_scale / 64.0) * 64),
        target_height=int(round(image_height * highres_scale / 64.0) * 64))
    for p in pixels]
    
    # Second pass (highres)
    pixels = numpy2pytorch(pixels).to(device=vae.device, dtype=vae.dtype)
    latents = vae.encode(pixels).latent_dist.mode() * vae.config.scaling_factor
    latents = latents.to(device=unet.device, dtype=unet.dtype)
    
    image_height, image_width = latents.shape[2] * 8, latents.shape[3] * 8
    fg = resize_and_center_crop(input_fg, image_width, image_height)
    bg = resize_and_center_crop(input_bg, image_width, image_height)
    concat_conds = numpy2pytorch([fg, bg]).to(device=vae.device, dtype=vae.dtype)
    concat_conds = vae.encode(concat_conds).latent_dist.mode() * vae.config.scaling_factor
    concat_conds = torch.cat([c[None, ...] for c in concat_conds], dim=1)
    
    latents = i2i_pipe(
        image=latents,
        strength=highres_denoise,
        prompt_embeds=conds,
        negative_prompt_embeds=unconds,
        width=image_width,
        height=image_height,
        num_inference_steps=int(round(steps / highres_denoise)),
        num_images_per_prompt=num_samples,
        generator=rng,
        output_type='latent',
        guidance_scale=cfg,
        cross_attention_kwargs={'concat_conds': concat_conds},
    ).images.to(vae.dtype) / vae.config.scaling_factor
    
    pixels = vae.decode(latents).sample
    pixels = pytorch2numpy(pixels, quant=False)
    results = [(x * 255.0).clip(0, 255).astype(np.uint8) for x in pixels]
    
    return results

def handler(event):
    """
    RunPod handler function
    """
    try:
        if 'input' not in event:
            return {"status": "error", "message": "Missing 'input' field in request"}
            
        input_data = event['input']
        
        # Validate required fields
        if 'foreground_image' not in input_data:
            return {"status": "error", "message": "Missing required field: 'foreground_image'"}
        
        # Decode images
        try:
            fg_image = decode_base64_image(input_data['foreground_image'])
        except Exception as e:
            return {"status": "error", "message": f"Failed to decode foreground_image: {str(e)}"}
        
        bg_source = input_data.get('bg_source', 'grey')
        bg_image = None
        
        if bg_source == 'upload':
            if 'background_image' not in input_data:
                return {"status": "error", "message": "bg_source is 'upload' but 'background_image' is missing"}
            try:
                bg_image = decode_base64_image(input_data['background_image'])
            except Exception as e:
                return {"status": "error", "message": f"Failed to decode background_image: {str(e)}"}
        
        # Get parameters
        prompt = input_data.get('prompt', 'beautiful lighting')
        image_width = input_data.get('image_width', 512)
        image_height = input_data.get('image_height', 640)
        num_samples = input_data.get('num_samples', 1)
        seed = input_data.get('seed', 12345)
        steps = input_data.get('steps', 20)
        cfg = input_data.get('cfg_scale', 7.0)
        highres_scale = input_data.get('highres_scale', 1.5)
        highres_denoise = input_data.get('highres_denoise', 0.5)
        a_prompt = input_data.get('added_prompt', 'best quality')
        n_prompt = input_data.get('negative_prompt', 'lowres, bad anatomy, bad hands, cropped, worst quality')
        
        # Process
        results = process_relight(
            fg_image, bg_image, prompt,
            image_width, image_height, num_samples, seed, steps,
            a_prompt, n_prompt, cfg, highres_scale, highres_denoise,
            bg_source
        )
        
        # Encode results
        output_images = [encode_image_to_base64(img) for img in results]
        
        return {
            "status": "success",
            "images": output_images
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Internal processing error: {str(e)}"
        }

if __name__ == "__main__":
    # Initialize models on startup
    initialize_models()
    
    # Start RunPod serverless worker
    runpod.serverless.start({"handler": handler})

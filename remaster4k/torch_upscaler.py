#!/usr/bin/env python3
"""Upscaler PyTorch partage (Real-ESRGAN anime 6B, tiles 4GB-safe, RGBA natif)."""

import sys
from pathlib import Path

sys.path.insert(0, r"D:\Code\supafilm\remaster")

import cv2
import numpy as np

_upsampler = None


import os

# fast (defaut, persos): SRVGG animevideov3 fp16 — ~10x plus rapide, la
# re-quantization palette efface les micro-differences vs RRDB.
# quality (stages): RRDB anime 6B fp32 tile 192.
MODE = os.environ.get("UPSCALER_MODE", "fast")


def get_upsampler():
    global _upsampler
    if _upsampler is None:
        from realesrgan import RealESRGANer
        if MODE == "quality":
            from basicsr.archs.rrdbnet_arch import RRDBNet
            model_path = r"D:\Code\supafilm\remaster\models\RealESRGAN_x4plus_anime_6B.pth"
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                            num_block=6, num_grow_ch=32, scale=4)
            _upsampler = RealESRGANer(
                scale=4, model_path=model_path, model=model,
                tile=192, tile_pad=8, pre_pad=0, half=False, device="cuda")
        else:
            from basicsr.archs.srvgg_arch import SRVGGNetCompact
            model_path = r"D:\Code\supafilm\remaster\models\realesr-animevideov3.pth"
            model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64,
                                    num_conv=16, upscale=4, act_type="prelu")
            _upsampler = RealESRGANer(
                scale=4, model_path=model_path, model=model,
                tile=512, tile_pad=8, pre_pad=0, half=True, device="cuda")
    return _upsampler


def upscale_rgba(arr, outscale=2):
    """arr: np.uint8 HxWx4 (RGBA) -> upscale, retourne HxWx4 a outscale."""
    up = get_upsampler()
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
    out, _ = up.enhance(bgr, outscale=outscale, alpha_upsampler="realesrgan")
    if out.shape[2] == 3:
        out = cv2.cvtColor(out, cv2.COLOR_BGR2RGBA)
    else:
        out = cv2.cvtColor(out, cv2.COLOR_BGRA2RGBA)
    return out


def upscale_rgb(arr, outscale=2):
    """arr: np.uint8 HxWx3 (RGB) -> 1 seul passage modele (pas d'alpha),
    retourne HxWx3 a outscale. 2x plus rapide que upscale_rgba."""
    up = get_upsampler()
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    out, _ = up.enhance(bgr, outscale=outscale)
    return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)

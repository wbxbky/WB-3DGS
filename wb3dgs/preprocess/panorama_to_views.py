from __future__ import annotations

import argparse
import math
from pathlib import Path

import cv2
import numpy as np


def perspective_rays(size: int, hfov_deg: float, yaw_deg: float) -> np.ndarray:
    """Return unit world rays for a square pinhole view from an equirect panorama."""
    f = 0.5 * size / math.tan(math.radians(hfov_deg) / 2)
    xy = np.arange(size, dtype=np.float32) + 0.5
    u, v = np.meshgrid(xy, xy)
    x = (u - size / 2) / f
    y = -(v - size / 2) / f
    z = np.ones_like(x)
    rays = np.stack([x, y, z], axis=-1)
    rays /= np.linalg.norm(rays, axis=-1, keepdims=True)
    yaw = math.radians(yaw_deg)
    rot = np.array([[math.cos(yaw), 0, math.sin(yaw)], [0, 1, 0],
                    [-math.sin(yaw), 0, math.cos(yaw)]], dtype=np.float32)
    return rays @ rot.T


def sample_equirect(panorama_bgr: np.ndarray, rays: np.ndarray) -> np.ndarray:
    x, y, z = np.moveaxis(rays, -1, 0)
    lon = np.arctan2(x, z)
    lat = np.arcsin(np.clip(y, -1, 1))
    h, w = panorama_bgr.shape[:2]
    map_x = ((lon / (2 * np.pi) + 0.5) * w).astype(np.float32)
    map_y = ((0.5 - lat / np.pi) * h).astype(np.float32)
    return cv2.remap(panorama_bgr, map_x, map_y, cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_WRAP)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--size", type=int, default=1536)
    p.add_argument("--fov", type=float, default=90.0)
    p.add_argument("--azimuths", nargs="+", type=float, default=[0, 60, 120, 180, 240, 300])
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    images = sorted([*a.input.glob("*.jpg"), *a.input.glob("*.png")])
    if not images:
        raise SystemExit(f"No panoramas found in {a.input}")
    ray_cache = {az: perspective_rays(a.size, a.fov, az) for az in a.azimuths}
    for src in images:
        pano = cv2.imread(str(src), cv2.IMREAD_COLOR)
        if pano is None:
            raise RuntimeError(f"Cannot read {src}")
        for az, rays in ray_cache.items():
            out_dir = a.output / f"{int(az):03d}"
            out_dir.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_dir / src.name), sample_equirect(pano, rays))


if __name__ == "__main__":
    main()


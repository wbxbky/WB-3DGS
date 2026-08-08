from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree


def load_xyz(path: Path) -> np.ndarray:
    x = np.loadtxt(path, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] < 3:
        raise ValueError("Expected whitespace-delimited XYZ[...]")
    return x[:, :3]


def voxel_centroids(points: np.ndarray, voxel: float) -> np.ndarray:
    keys = np.floor(points / voxel).astype(np.int64)
    unique, inverse = np.unique(keys, axis=0, return_inverse=True)
    sums = np.zeros((len(unique), 3), dtype=np.float64)
    counts = np.bincount(inverse)
    np.add.at(sums, inverse, points)
    return sums / counts[:, None]


def local_gaussian_geometry(points: np.ndarray, k: int, min_scale: float):
    if len(points) <= k:
        raise ValueError(f"Need > k={k} anchors, got {len(points)}")
    tree = cKDTree(points)
    _, ids = tree.query(points, k=k + 1)
    rotations, scales = [], []
    for p, nn in zip(points, ids):
        q = points[nn[1:]]
        d = q - q.mean(axis=0)
        cov = (d.T @ d) / max(len(q) - 1, 1)
        vals, vecs = np.linalg.eigh(cov)
        order = np.argsort(vals)[::-1]
        vals, vecs = vals[order], vecs[:, order]
        if np.linalg.det(vecs) < 0:
            vecs[:, -1] *= -1
        rotations.append(vecs)
        scales.append(np.maximum(np.sqrt(np.clip(vals, 0, None)), min_scale))
    return np.stack(rotations), np.stack(scales)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--points", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--voxel", type=float, default=0.05)
    p.add_argument("--knn", type=int, default=12)
    p.add_argument("--min-scale", type=float, default=0.01)
    a = p.parse_args()
    centers = voxel_centroids(load_xyz(a.points), a.voxel)
    rotations, scales = local_gaussian_geometry(centers, a.knn, a.min_scale)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.output, centers=centers, rotations=rotations, scales=scales,
                        opacity=np.full(len(centers), 0.1, dtype=np.float32))


if __name__ == "__main__":
    main()


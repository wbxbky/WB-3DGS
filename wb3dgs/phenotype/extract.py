from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def confidence(opacity: np.ndarray, semantic_probability: np.ndarray, n_vis: np.ndarray) -> np.ndarray:
    return np.asarray(opacity) * np.asarray(semantic_probability) * (np.asarray(n_vis) > 3)


def pseudostem_height(stem_xyz: np.ndarray, ground_z: float) -> float:
    return float(np.percentile(stem_xyz[:, 2], 99) - ground_z)


def equivalent_diameter(stem_xyz: np.ndarray, weights: np.ndarray, ground_z: float,
                        sample_height_m: float = 0.10, slice_thickness_m: float = 0.05) -> float:
    """Weighted PCA ellipse approximation for the 5-cm stem slice.

    The actual release should replace this PCA approximation with the authors'
    exact weighted ellipse-fitting routine if it differs.
    """
    z0 = ground_z + sample_height_m
    use = np.abs(stem_xyz[:, 2] - z0) <= slice_thickness_m / 2
    xy, w = stem_xyz[use, :2], weights[use]
    if len(xy) < 8 or w.sum() <= 0:
        return float("nan")
    mu = np.average(xy, axis=0, weights=w)
    d = xy - mu
    cov = (d * w[:, None]).T @ d / w.sum()
    vals = np.sort(np.linalg.eigvalsh(cov))[::-1]
    # For boundary-like ellipse samples, covariance eigenvalues are a^2/2,b^2/2.
    a, b = np.sqrt(np.maximum(2 * vals, 0))
    return float(2.0 * np.sqrt(a * b))


def leaf_centerline_and_width(xyz: np.ndarray, segments: int = 10) -> tuple[float, float]:
    xyz = np.asarray(xyz, float)
    d = xyz - xyz.mean(axis=0)
    vals, vecs = np.linalg.eigh(np.cov(d.T))
    main = vecs[:, np.argmax(vals)]
    s = d @ main
    edges = np.linspace(s.min(), s.max(), segments + 1)
    centers = []
    widths = []
    for i in range(segments):
        m = (s >= edges[i]) & (s <= edges[i + 1] if i == segments - 1 else s < edges[i + 1])
        if m.sum() < 3:
            continue
        q = xyz[m]
        centers.append(q.mean(axis=0))
        local = q - q.mean(axis=0)
        lvals, lvecs = np.linalg.eigh(np.cov(local.T))
        normal = lvecs[:, np.argmin(lvals)]
        cross = np.cross(normal, main)
        if np.linalg.norm(cross) == 0:
            continue
        cross /= np.linalg.norm(cross)
        widths.append(np.percentile(local @ cross, 97.5) - np.percentile(local @ cross, 2.5))
    length = float(np.linalg.norm(np.diff(np.asarray(centers), axis=0), axis=1).sum()) if len(centers) >= 2 else float("nan")
    width = float(np.percentile(widths, 95)) if widths else float("nan")
    return length, width


def phenotype_metrics(reference: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    ref, pred = np.asarray(reference, float), np.asarray(prediction, float)
    ss_res = np.sum((ref - pred) ** 2)
    ss_tot = np.sum((ref - ref.mean()) ** 2)
    return {
        "R2": float(1 - ss_res / ss_tot),
        "RMSE": float(np.sqrt(np.mean((pred - ref) ** 2))),
        "MAPE_percent": float(np.mean(np.abs(pred - ref) / ref) * 100),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Extract stem traits from canonical Gaussian NPZ.")
    p.add_argument("--gaussians", type=Path, required=True,
                   help="NPZ: centers,opacity,p_sem,n_vis,class_id,instance_id")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--ground-z", type=float, required=True,
                   help="Ground plane z at plant; exact release should derive this from the RANSAC ground-plane step")
    p.add_argument("--stem-slice-cm", type=float, default=5.0)
    p.add_argument("--leaf-segments", type=int, default=10)
    p.add_argument("--grid-mm", type=float, default=2.0)
    a = p.parse_args()
    g = np.load(a.gaussians)
    xyz = g["centers"]
    w = confidence(g["opacity"], g["p_sem"], g["n_vis"])
    cls = g["class_id"]
    stem = cls == 1
    rows = [{
        "trait": "pseudostem_height_m",
        "value": pseudostem_height(xyz[stem], a.ground_z),
    }, {
        "trait": "pseudostem_equivalent_diameter_m",
        "value": equivalent_diameter(xyz[stem], w[stem], a.ground_z, 0.10, a.stem_slice_cm / 100),
    }]
    for instance in sorted(set(g["instance_id"][cls == 2].astype(int)) - {-1}):
        leaf = (cls == 2) & (g["instance_id"] == instance) & (w > 0)
        length, width = leaf_centerline_and_width(xyz[leaf], a.leaf_segments)
        rows.extend([
            {"trait": f"leaf_{instance}_length_m", "value": length},
            {"trait": f"leaf_{instance}_width_m", "value": width},
        ])
    a.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(a.output, index=False)
    print("NOTE: exact probabilistic 2D Gaussian leaf-area integration requires the private renderer covariance projection; see RELEASE_AUDIT.md")


if __name__ == "__main__":
    main()


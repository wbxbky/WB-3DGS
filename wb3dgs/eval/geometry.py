from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from wb3dgs.preprocess.anchors import load_xyz, voxel_centroids


def geometry_metrics(recon: np.ndarray, reference: np.ndarray, threshold_m: float) -> dict[str, float]:
    if not len(recon) or not len(reference):
        raise ValueError("Point sets must be non-empty")
    rtree, gtree = cKDTree(reference), cKDTree(recon)
    d_r2ref, _ = rtree.query(recon, k=1)
    d_ref2r, _ = gtree.query(reference, k=1)
    symmetric_cd_m = 0.5 * (d_r2ref.mean() + d_ref2r.mean())
    precision = float(np.mean(d_r2ref <= threshold_m))
    recall = float(np.mean(d_ref2r <= threshold_m))
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "symmetric_chamfer_cm": float(symmetric_cd_m * 100),
        "precision_at_threshold": precision,
        "recall_at_threshold": recall,
        "f1_at_threshold": f1,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--recon", type=Path, required=True)
    p.add_argument("--reference", type=Path, required=True)
    p.add_argument("--voxel", type=float, default=0.05,
                   help="Fixed evaluation-stage voxel, distinct from anchor voxel sensitivity")
    p.add_argument("--threshold-cm", type=float, default=5.0)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    recon = voxel_centroids(load_xyz(a.recon), a.voxel)
    ref = voxel_centroids(load_xyz(a.reference), a.voxel)
    result = geometry_metrics(recon, ref, a.threshold_cm / 100.0)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()


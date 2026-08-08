from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def zero_intercept_k(length: np.ndarray, width: np.ndarray, area: np.ndarray) -> float:
    x = np.asarray(length, float) * np.asarray(width, float)
    y = np.asarray(area, float)
    return float(np.dot(x, y) / np.dot(x, x))


def plant_cluster_ci(df: pd.DataFrame, resamples: int = 2000, seed: int = 42):
    plants = df["plant_id"].drop_duplicates().to_numpy()
    rng = np.random.default_rng(seed)
    ks = []
    for _ in range(resamples):
        sampled = rng.choice(plants, size=len(plants), replace=True)
        pieces = [df[df.plant_id == p] for p in sampled]
        boot = pd.concat(pieces, ignore_index=True)
        ks.append(zero_intercept_k(boot.length_m, boot.width_m, boot.area_scan_m2))
    return np.percentile(ks, [2.5, 97.5])


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True,
                   help="CSV: plant_id,length_m,width_m,area_scan_m2,subset")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--resamples", type=int, default=2000)
    a = p.parse_args()
    df = pd.read_csv(a.input)
    cal = df[df.subset == "calibration"].copy()
    val = df[df.subset == "heldout_validation"].copy()
    k = zero_intercept_k(cal.length_m, cal.width_m, cal.area_scan_m2)
    lo, hi = plant_cluster_ci(cal, a.resamples, a.seed)
    pred = k * val.length_m.to_numpy(float) * val.width_m.to_numpy(float)
    ref = val.area_scan_m2.to_numpy(float)
    rmse = float(np.sqrt(np.mean((pred - ref) ** 2)))
    mape = float(np.mean(np.abs(pred - ref) / ref) * 100)
    print(f"k={k:.6f} plant-bootstrap-95CI=[{lo:.6f},{hi:.6f}] heldout_RMSE={rmse:.6f} m2 heldout_MAPE={mape:.3f}%")


if __name__ == "__main__":
    main()


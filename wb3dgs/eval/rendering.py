from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd


def psnr_from_mse(mse: float, data_range: float = 1.0) -> float:
    return float("inf") if mse == 0 else 10.0 * math.log10(data_range * data_range / mse)


def hierarchical_summary(df: pd.DataFrame, metric_columns: list[str]) -> pd.DataFrame:
    """Average view -> plant -> sequence, then mean/sample-SD over sequences."""
    need = {"wind_regime", "sequence_id", "plant_id", *metric_columns}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    plant = df.groupby(["wind_regime", "sequence_id", "plant_id"], as_index=False)[metric_columns].mean()
    sequence = plant.groupby(["wind_regime", "sequence_id"], as_index=False)[metric_columns].mean()
    rows = []
    for regime, g in sequence.groupby("wind_regime"):
        row = {"wind_regime": regime, "n_sequences": len(g)}
        for m in metric_columns:
            row[f"{m}_mean"] = g[m].mean()
            row[f"{m}_sd"] = g[m].std(ddof=1)
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description="Aggregate already-computed per-view rendering metrics.")
    p.add_argument("--pred", type=Path, required=True,
                   help="CSV with wind_regime,sequence_id,plant_id,PSNR,SSIM,LPIPS")
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    out = hierarchical_summary(pd.read_csv(a.pred), ["PSNR", "SSIM", "LPIPS"])
    a.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.output, index=False)


if __name__ == "__main__":
    main()


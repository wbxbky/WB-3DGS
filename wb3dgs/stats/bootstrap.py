from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def cluster_bootstrap(values: pd.DataFrame, cluster: str, metric: str,
                      resamples: int = 10_000, seed: int = 42) -> tuple[float, float, float]:
    """Percentile bootstrap resampling clusters, never child observations."""
    grouped = values.groupby(cluster)[metric].mean()
    x = grouped.to_numpy(float)
    if len(x) < 2:
        raise ValueError("Need at least two independent clusters")
    rng = np.random.default_rng(seed)
    draws = rng.choice(x, size=(resamples, len(x)), replace=True).mean(axis=1)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return float(x.mean()), float(lo), float(hi)


def paired_cluster_bootstrap(df: pd.DataFrame, cluster: str, a: str, b: str,
                             resamples: int = 10_000, seed: int = 42):
    pair = df.groupby(cluster)[[a, b]].mean().dropna()
    d = (pair[b] - pair[a]).to_numpy(float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(d, size=(resamples, len(d)), replace=True).mean(axis=1)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--cluster", default="sequence_id")
    p.add_argument("--metric", required=True)
    p.add_argument("--resamples", type=int, default=10000)
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    mean, lo, hi = cluster_bootstrap(pd.read_csv(a.input), a.cluster, a.metric,
                                     a.resamples, a.seed)
    print(f"mean={mean:.6g} 95%CI=[{lo:.6g}, {hi:.6g}]")


if __name__ == "__main__":
    main()

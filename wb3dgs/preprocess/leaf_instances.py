from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--points", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--eps", type=float, default=0.08)
    p.add_argument("--min-samples", type=int, default=20)
    a = p.parse_args()
    xyz = np.loadtxt(a.points, dtype=float)[:, :3]
    label = DBSCAN(eps=a.eps, min_samples=a.min_samples).fit_predict(xyz)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"point_index": np.arange(len(xyz)), "cluster_id": label}).to_csv(a.output, index=False)


if __name__ == "__main__":
    main()

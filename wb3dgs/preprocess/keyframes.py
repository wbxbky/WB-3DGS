from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def quat_angle_deg(q1: np.ndarray, q2: np.ndarray) -> float:
    q1 = q1 / np.linalg.norm(q1)
    q2 = q2 / np.linalg.norm(q2)
    dot = np.clip(abs(float(np.dot(q1, q2))), 0.0, 1.0)
    return float(np.degrees(2.0 * np.arccos(dot)))


def select(df: pd.DataFrame, translation_m: float, rotation_deg: float,
           blur_threshold: float, replace_window: int) -> pd.DataFrame:
    """Apply the paper's pose gate then blur replacement.

    Input must contain tx/ty/tz, qx/qy/qz/qw and `blur_score` computed as
    Laplacian variance on the source panorama. Replacements are selected before
    any train/held-out partitioning, as required by the manuscript.
    """
    required = {"tx", "ty", "tz", "qx", "qy", "qz", "qw", "blur_score"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df = df.reset_index(drop=True).copy()
    chosen = [0]
    for i in range(1, len(df)):
        prev = chosen[-1]
        dp = np.linalg.norm(df.loc[i, ["tx", "ty", "tz"]].to_numpy(float) -
                            df.loc[prev, ["tx", "ty", "tz"]].to_numpy(float))
        qa = df.loc[i, ["qx", "qy", "qz", "qw"]].to_numpy(float)
        qb = df.loc[prev, ["qx", "qy", "qz", "qw"]].to_numpy(float)
        if dp > translation_m or quat_angle_deg(qa, qb) > rotation_deg:
            chosen.append(i)
    replaced = []
    for i in chosen:
        if float(df.loc[i, "blur_score"]) >= blur_threshold:
            replaced.append(i)
            continue
        lo, hi = max(0, i - replace_window), min(len(df), i + replace_window + 1)
        j = int(df.loc[lo:hi - 1, "blur_score"].astype(float).idxmax())
        replaced.append(j)
    return df.loc[sorted(set(replaced))].reset_index(drop=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--frames", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--translation-m", type=float, default=0.20)
    p.add_argument("--rotation-deg", type=float, default=5.0)
    p.add_argument("--blur-threshold", type=float, default=100.0)
    p.add_argument("--replace-window", type=int, default=2)
    a = p.parse_args()
    out = select(pd.read_csv(a.frames), a.translation_m, a.rotation_deg,
                 a.blur_threshold, a.replace_window)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.output, index=False)


if __name__ == "__main__":
    main()


from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


def numeric_id(value: str) -> int:
    m = re.search(r"(\d+)$", str(value))
    if not m:
        raise ValueError(f"ID must end in an integer: {value}")
    return int(m.group(1))


def make_blocks(n: int) -> list[np.ndarray]:
    q, r = divmod(n, 8)
    sizes = [q + 1] * r + [q] * (8 - r)
    blocks, start = [], 0
    for size in sizes:
        blocks.append(np.arange(start, start + size, dtype=int))
        start += size
    return blocks


def heldout_block(global_plant_index_1based: int) -> int:
    """Return paper block number (1-based), always one of 3,4,5,6."""
    return 3 + ((global_plant_index_1based - 1) % 4)


def viewing_angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    return float(np.degrees(np.arccos(np.clip(np.dot(a, b), -1, 1))))


def quat_xyzw_to_rot(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, float)
    q /= np.linalg.norm(q)
    x, y, z, w = q
    return np.array([
        [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
        [2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y],
    ])


def six_view_directions(q_xyzw: np.ndarray) -> np.ndarray:
    """Six world-space virtual-camera forward directions for one panorama."""
    r_wc = quat_xyzw_to_rot(q_xyzw)
    dirs = []
    for az in (0, 60, 120, 180, 240, 300):
        a = math.radians(az)
        local = np.array([math.sin(a), 0.0, math.cos(a)])
        dirs.append(r_wc @ local)
    return np.stack(dirs)


def assign(df: pd.DataFrame) -> pd.DataFrame:
    """Build mutually-exclusive panorama-level inner partitions.

    Required columns: sequence_id, plant_id, panorama_id, timestamp_s, tx,ty,tz,
    qx,qy,qz,qw. Quaternion represents camera-to-world rotation. Pose guarding
    checks the six paper azimuths for every remaining/held-out panorama.
    """
    keys = [(s, p) for s, p in df[["sequence_id", "plant_id"]].drop_duplicates().itertuples(index=False, name=None)]
    keys.sort(key=lambda x: (numeric_id(x[0]), numeric_id(x[1])))
    index = {k: i + 1 for i, k in enumerate(keys)}
    outputs = []
    required = {"sequence_id", "plant_id", "panorama_id", "timestamp_s", "tx", "ty", "tz",
                "qx", "qy", "qz", "qw"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    for key, g in df.groupby(["sequence_id", "plant_id"], sort=False):
        g = g.sort_values("timestamp_s").drop_duplicates("panorama_id").reset_index(drop=True).copy()
        blocks = make_blocks(len(g))
        block_num = heldout_block(index[key])
        held_idx = set(blocks[block_num - 1].tolist())
        labels = np.full(len(g), "scene_optimization", dtype=object)
        for i in held_idx:
            labels[i] = "heldout"
        if held_idx:
            lo, hi = min(held_idx), max(held_idx)
            for i in range(max(0, lo - 2), lo):
                labels[i] = "temporal_guard"
            for i in range(hi + 1, min(len(g), hi + 3)):
                labels[i] = "temporal_guard"
        held = g.iloc[sorted(held_idx)]
        for i in range(len(g)):
            if labels[i] != "scene_optimization":
                continue
            p = g.loc[i, ["tx", "ty", "tz"]].to_numpy(float)
            q = g.loc[i, ["qx", "qy", "qz", "qw"]].to_numpy(float)
            candidate_dirs = six_view_directions(q)
            guarded = False
            for _, h in held.iterrows():
                hp = h[["tx", "ty", "tz"]].to_numpy(float)
                if np.linalg.norm(p - hp) >= 0.40:
                    continue
                hq = h[["qx", "qy", "qz", "qw"]].to_numpy(float)
                held_dirs = six_view_directions(hq)
                if any(viewing_angle_deg(a, b) < 10.0 for a in candidate_dirs for b in held_dirs):
                    labels[i] = "pose_guard"
                    guarded = True
                    break
            if guarded:
                continue
        g["subset"] = labels
        g["block_id"] = 0
        for j, b in enumerate(blocks, start=1):
            g.loc[b, "block_id"] = j
        outputs.append(g)
    return pd.concat(outputs, ignore_index=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--frames", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    out = assign(pd.read_csv(a.frames))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.output, index=False)


if __name__ == "__main__":
    main()

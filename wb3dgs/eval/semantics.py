from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def iou_dice(pred: np.ndarray, ref: np.ndarray, classes=(0, 1, 2)) -> dict[str, float]:
    out, ious, dices = {}, [], []
    for c in classes:
        p, r = pred == c, ref == c
        inter = np.logical_and(p, r).sum()
        union = np.logical_or(p, r).sum()
        denom = p.sum() + r.sum()
        iou = 1.0 if union == 0 else inter / union
        dice = 1.0 if denom == 0 else 2 * inter / denom
        out[f"iou_class_{c}"] = float(iou)
        out[f"dice_class_{c}"] = float(dice)
        ious.append(iou); dices.append(dice)
    out["miou"] = float(np.mean(ious))
    out["macro_dice"] = float(np.mean(dices))
    out["propagation_failure"] = bool(out["miou"] < 0.75 or
                                      not np.any(pred == 1) or not np.any(pred == 2))
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pred", type=Path, required=True)
    p.add_argument("--reference", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    pred_files = sorted(a.pred.glob("*.png"))
    rows = []
    for pf in pred_files:
        rf = a.reference / pf.name
        pred, ref = cv2.imread(str(pf), 0), cv2.imread(str(rf), 0)
        if pred is None or ref is None:
            raise FileNotFoundError(f"Missing pair for {pf.name}")
        rows.append(iou_dice(pred, ref))
    if not rows:
        raise SystemExit("No PNG mask pairs found")
    keys = [k for k in rows[0] if k != "propagation_failure"]
    result = {k: float(np.mean([r[k] for r in rows])) for k in keys}
    result["failures"] = int(sum(r["propagation_failure"] for r in rows))
    result["n"] = len(rows)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()


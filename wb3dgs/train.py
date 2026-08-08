from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from wb3dgs.utils.seed import seed_everything


REQUIRED = (
    "training.seed",
    "loss.lambda_ssim", "loss.lambda_sem", "loss.lambda_rigid", "loss.lambda_root",
    "loss.lambda_smooth", "loss.lambda_geo", "loss.lambda_reg",
    "deformation.instance_mlp", "deformation.hashgrid", "deformation.residual_decoder",
    "training.adam_betas", "training.adam_eps", "training.densification",
)


def get_nested(d: dict, path: str):
    cur = d
    for key in path.split("."):
        cur = cur[key]
    return cur


def validate_release_config(cfg: dict) -> list[str]:
    missing = []
    for path in REQUIRED:
        try:
            value = get_nested(cfg, path)
        except KeyError:
            missing.append(path)
            continue
        if value == "REQUIRED_FROM_AUTHORS" or value is None:
            missing.append(path)
    return missing


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--split", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--seed", type=int, default=None,
                   help="Must match the actual experiment log; omitted uses training.seed from YAML")
    a = p.parse_args()
    cfg = yaml.safe_load(a.config.read_text(encoding="utf-8"))
    missing = validate_release_config(cfg)
    if missing:
        raise SystemExit(
            "Exact paper training cannot be claimed until these values are recovered from the original source/logs:\n  - "
            + "\n  - ".join(missing)
        )
    seed = int(a.seed if a.seed is not None else cfg["training"]["seed"])
    seed_everything(seed)
    raise SystemExit(
        "Configuration is complete, but the private WB-3DGS rasterizer/optimizer has not been "
        "connected to this release adapter. Replace this stop with the authors' original training "
        "entry point while preserving the split manifest and 30,000-iteration checkpoint rule."
    )


if __name__ == "__main__":
    main()

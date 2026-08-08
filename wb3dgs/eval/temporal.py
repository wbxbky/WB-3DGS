from __future__ import annotations

import numpy as np


def forward_backward_validity(forward: np.ndarray, backward_warped: np.ndarray,
                              threshold_px: float = 1.0) -> np.ndarray:
    """Paper validity gate for RAFT temporal evaluation.

    Flow estimation/warping remains tied to the official RAFT implementation.
    This function makes the paper's 1-pixel criterion explicit and testable.
    """
    if forward.shape != backward_warped.shape or forward.shape[-1] != 2:
        raise ValueError("Flow tensors must have identical HxWx2 shapes")
    return np.linalg.norm(forward + backward_warped, axis=-1) <= threshold_px


def warping_error(render_t_warped: np.ndarray, reference_t1: np.ndarray,
                  valid: np.ndarray) -> float:
    if render_t_warped.shape != reference_t1.shape:
        raise ValueError("Image shapes differ")
    if valid.shape != render_t_warped.shape[:2]:
        raise ValueError("Validity mask shape differs")
    if not np.any(valid):
        return float("nan")
    diff = np.abs(render_t_warped.astype(np.float64) - reference_t1.astype(np.float64))
    return float(diff[valid].mean())


RAFT_RELEASE_PROTOCOL = {
    "checkpoint": "raft-things.pth",
    "updates": 24,
    "mixed_precision": True,
    "rgb_scale": "0-255",
    "forward_backward_threshold_px": 1.0,
}


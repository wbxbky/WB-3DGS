import numpy as np
import pandas as pd

from wb3dgs.eval.geometry import geometry_metrics
from wb3dgs.preprocess.blocked_split import heldout_block, make_blocks
from wb3dgs.stats.bootstrap import cluster_bootstrap


def test_heldout_blocks_cycle_3_to_6():
    assert [heldout_block(i) for i in range(1, 9)] == [3, 4, 5, 6, 3, 4, 5, 6]


def test_eight_blocks_cover_all_frames_once():
    blocks = make_blocks(47)
    merged = np.concatenate(blocks)
    assert len(blocks) == 8
    assert np.array_equal(merged, np.arange(47))


def test_geometry_identity_is_zero():
    p = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    m = geometry_metrics(p, p.copy(), 0.05)
    assert m["symmetric_chamfer_cm"] == 0
    assert m["f1_at_threshold"] == 1


def test_cluster_bootstrap_is_seeded():
    df = pd.DataFrame({"sequence_id": ["a", "b", "c"], "x": [1.0, 2.0, 3.0]})
    x = cluster_bootstrap(df, "sequence_id", "x", resamples=100, seed=42)
    y = cluster_bootstrap(df, "sequence_id", "x", resamples=100, seed=42)
    assert x == y


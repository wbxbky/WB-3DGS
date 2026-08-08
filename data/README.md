# Dataset layout and metadata contract

The public code uses explicit manifests. Do not infer train/test membership from
directory names.

## Sequence identifiers

The current paper contains 18 mutually exclusive acquisition sequences. The
fold structure in Supplementary Table S3 implies Seq-01..06 are L1,
Seq-07..12 are L2, and Seq-13..18 are L3. Verify this mapping against the raw
acquisition log before publication; `sequence_metadata.csv` marks that check.

Each sequence contains 20 unique plants. No plant is shared between sequences.

## `poses.csv`

Required columns:

```text
sequence_id,plant_id,panorama_id,timestamp_s,tx,ty,tz,qx,qy,qz,qw
```

Pose is `T_WC(t)`: camera-to-world under the paper convention
`p_A = T_AB p_B`.

## `split.csv`

Required columns:

```text
sequence_id,plant_id,panorama_id,virtual_azimuth_deg,subset,block_id
```

`subset` must be one of `scene_optimization`, `heldout`, `temporal_guard`, or
`pose_guard`. All six virtual views from one panorama must share the same
subset. Held-out and guard RGB/semantic/LiDAR observations must never enter
training losses, Gaussian initialization, anchor construction, or geometric
supervision.

## Calibration

See `calibration/extrinsics.example.yaml`. Do not publish made-up matrices. The
manuscript reports fixed `T_LI` and `T_LC`, but not their numeric entries.

## Public subset

The recommended minimum subset is specified in `sample_subset/manifest.csv`.
It uses the three representative cases already reported in Supplementary
Table S7 so that the released examples are traceable to the manuscript.


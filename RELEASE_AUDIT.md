# Release audit: values that must come from the original experiment archive

The current manuscript is sufficient to reconstruct the experimental protocol,
but not every code-level hyperparameter. Fill the items below from the actual
source tree/logs before a public release. A reproducibility repository must not
replace unknown historical values with plausible defaults.

## Paper-reported and safe to publish now

- Seed for cluster-bootstrap analysis: 42.
- Keyframe thresholds: translation 0.20 m; rotation 5 deg; blur score 100;
  replacement window +/-2 frames.
- Panorama conversion: six views, 1536x1536, azimuth 0:60:300 deg, HFOV 90 deg.
- Inner split: 8 contiguous blocks; held-out block 3-6 via
  `3 + ((i_p - 1) mod 4)`; temporal guard two panoramas on each side; pose guard
  <0.40 m and <10 deg.
- Rigidity weights: stem 1.0, leaf 0.3, background 0.
- Anchor voxel 0.05 m; KNN 12; depth residual 0.10 m in >=3 views; minimum
  Gaussian scale 0.01 m; initial opacity 0.1.
- DBSCAN eps 0.08 m; MinPts 20.
- Maximum residual displacement <0.05 m.
- Semantic softmax temperature 0.1; petiole root neighborhood 0.10 m.
- 30k iterations; stages 0-3k, 3k-10k, 10k-25k, 25k-30k.
- Position LR 1.6e-4; instance MLP LR 5e-4; residual feature-grid LR 1e-4.
- Phenotyping: visibility count >3; stem diameter at 0.10 m; 5-cm slice;
  10 leaf segments; 2-mm grid.
- RAFT: raft-things.pth, 24 updates, mixed precision, 1-pixel FB gate.
- Geometry evaluation: common 3m cube ROI, evaluation voxel 0.05 m,
  Precision/Recall/F1 threshold 5 cm, no post-hoc rigid registration.

## REQUIRED_FROM_AUTHORS before exact-reproduction claim

| Missing item | Why it matters | Where to copy it |
|---|---|---|
| Exact Python/PyTorch/CUDA/cuDNN versions | binary/numerical reproducibility | original workstation env lock |
| Commit hashes of Gaussian rasterizer and hash-grid CUDA extension | changes numerical output | private source/submodule history |
| `lambda_ssim` | Eq. 7 training objective | training config/log |
| `lambda_sem` | Eq. 11 | training config/log |
| `lambda_rigid` | Eq. 11 | training config/log |
| `lambda_root` | Eq. 11 | training config/log |
| `lambda_smooth` | Eq. 11 | training config/log |
| `lambda_geo` | Eq. 11 | training config/log |
| `lambda_reg` | Eq. 11 | training config/log |
| Adam betas/epsilon/weight decay | optimizer trajectory | optimizer construction |
| Gaussian position LR schedule after initialization | training trajectory | scheduler config |
| Densification/pruning schedule and thresholds | Gaussian count/output | renderer training config |
| Spherical-harmonic degree and schedule | color model | model config |
| `Phi_inst` layer count/width/Fourier frequencies | hierarchical motion capacity | model source |
| HashGrid levels/features/table size/base & max resolution | residual capacity | model source |
| `Phi_res` decoder architecture | residual capacity | model source |
| Exact SAM model/checkpoint and prompting cadence | Table S9 reproducibility | preprocessing log |
| Exact XMem revision/checkpoint and morphology kernel | Table S9 reproducibility | preprocessing log |
| FAST-LIO2 revision and modified parameters | pose reproducibility | LIO source/config |
| Numeric `T_LI`, `T_LC`, `T_BL` calibration matrices | coordinate reproducibility | calibration file |
| Actual per-frame inner split manifest | audit against leakage | experiment archive |
| Actual manual DBSCAN correction records | phenotype traceability | annotation/audit archive |
| Exact per-sequence wind means | regime verification | acquisition metadata |
| Raw per-sequence metric values behind mean+SD | table regeneration | evaluation outputs |
| Checkpoint SHA256 and source commit | artifact provenance | released checkpoint |

## Manuscript-to-code consistency issue to resolve

The current manuscript has a known duplicate-configuration inconsistency:
`w/o Physics` in Table 5 reports symmetric CD `1.24 +/- 0.10 cm`, whereas
`Base + LA + HM + SC` in Table 6 reports `1.21 +/- 0.14 cm`. If these rows are
the same configuration and same six L1 sequences, recover the unrounded source
results and use one value in both the manuscript and repository.

Do not encode either value as a unit-test target until this is resolved.


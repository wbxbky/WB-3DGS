# WB-3DGS: Wind-Aware Banana 3D Gaussian Splatting

Reproducibility release scaffold accompanying the manuscript **WB-3DGS**. The
repository mirrors the experimental protocol in the current manuscript:

- 18 acquisition sequences (6 each for L1/L2/L3 wind regimes), 360 unique
  plants, and 1,080 marked leaves;
- LiDAR-inertial poses from FAST-LIO2, 8K Insta360 X5 panoramas, and RoboSense
  RS-32 LiDAR;
- six 1536 x 1536 perspective views per panorama at azimuths 0, 60, ..., 300
  degrees and 90-degree horizontal FOV;
- LiDAR-anchor initialization (`voxel=0.05 m`, `KNN k=12`), semantic priors,
  DBSCAN leaf instances (`eps=0.08 m`, `MinPts=20`), hierarchical deformation,
  and semantic/physical regularization;
- a fixed 30,000-iteration four-stage curriculum;
- sequence-grouped outer folds and blocked inner held-out views;
- rendering, temporal, LiDAR consistency, semantic pseudo-label, and phenotype
  evaluation matching Tables 1-9 and Supplementary Tables S3-S9.

## Important release status

The preprocessing, split-generation, metric, bootstrap, calibration, and
phenotype utilities in this scaffold are executable. 

## Repository layout

```text
WB-3DGS/
├── README.md
├── RELEASE_AUDIT.md
├── DATA_AVAILABILITY.md
├── environment.yml
├── requirements.txt
├── configs/
│   ├── paper_defaults.yaml
│   └── experiments/              # one config per reported experiment
├── data/
│   ├── README.md
│   ├── calibration/extrinsics.example.yaml
│   ├── splits/outer_folds.csv
│   ├── splits/sequence_metadata.csv
│   └── sample_subset/manifest.csv
├── checkpoints/README.md
├── third_party/README.md
├── wb3dgs/
│   ├── preprocess/               # panorama, keyframe, split, anchor utilities
│   ├── eval/                     # rendering, geometry, temporal, semantics
│   ├── phenotype/                # stem/leaf traits and leaf-area calibration
│   ├── stats/                    # sequence-cluster bootstrap
│   ├── utils/seed.py
│   └── train.py
└── tests/
```

## Data directory expected by the code

```text
data_root/
├── raw/
│   └── Seq-01/
│       ├── camera/panoramas/*.jpg
│       ├── lidar/*.pcd
│       ├── imu/imu.csv
│       └── timestamps.csv
├── calibration/
│   ├── extrinsics.yaml
│   └── virtual_camera.yaml
├── processed/
│   └── Seq-01/
│       └── Plant-01/
│           ├── panoramas/
│           ├── views/{000,060,120,180,240,300}/
│           ├── poses.csv
│           ├── lidar/
│           ├── semantic/
│           ├── anchors.npz
│           └── split.csv
└── phenotype/
    ├── manual_measurements.csv
    └── leaf_area_calibration.csv
```

Raw data are never searched recursively by the training code. A split manifest
is mandatory, so held-out/guard observations cannot enter optimization by
accident.

## Installation

The manuscript reports PyTorch, custom CUDA rasterization/hash-grid operators,
and an RTX 3090 (24 GB).

```bash
conda env create -f environment.yml
conda activate wb3dgs
python -m pip install -e .
```

For the exact historical environment, run on the original workstation and
commit the outputs:

```bash
python -V
nvidia-smi
nvcc --version
conda env export --from-history > environment-history.yml
python -m pip freeze > requirements-lock.txt
```

## Reproduction workflow

### 1. Generate the six virtual cameras

```bash
python -m wb3dgs.preprocess.panorama_to_views \
  --input data/raw/Seq-01/camera/panoramas \
  --output data/processed/Seq-01/views \
  --size 1536 --fov 90 --azimuths 0 60 120 180 240 300
```

### 2. Select quality-controlled keyframes

Paper settings are translation >0.20 m or rotation >5 degrees, blur threshold
100, with a +/-2-frame replacement window.

```bash
python -m wb3dgs.preprocess.keyframes \
  --frames metadata/Seq-01_frames.csv \
  --output data/processed/Seq-01/keyframes.csv \
  --translation-m 0.20 --rotation-deg 5 --blur-threshold 100 --replace-window 2
```

### 3. Build blocked train/guard/held-out manifests

```bash
python -m wb3dgs.preprocess.blocked_split \
  --frames data/processed/all_keyframes.csv \
  --output data/splits/inner_manifest.csv
```

The deterministic held-out block is `b_p = 3 + ((i_p - 1) mod 4)`, after
sorting plant models by numerical Sequence ID and Plant ID. Each plant's
panoramas are divided into eight contiguous blocks; only blocks 3-6 can be held
out. The two panoramas immediately before and after that block are temporal
guards. A remaining panorama becomes a pose guard if one of its six views is
within 0.40 m and 10 degrees of a held-out view.

### 4. Construct LiDAR anchors

```bash
python -m wb3dgs.preprocess.anchors \
  --points plant_scene_optimization.xyz \
  --output anchors.npz --voxel 0.05 --knn 12 --min-scale 0.01
```

Multi-view visibility filtering additionally uses depth residual <0.10 m in at
least three views. The public utility implements the voxel/KNN manifold
initialization; connect the project-specific visibility inputs when exporting
the private preprocessing pipeline.

### 5. Semantic pseudo-labels and leaf instances

The paper uses sparse point prompts to obtain SAM seed masks, XMem propagation
within each contiguous scene-optimization segment, and fixed morphological
denoising. Propagation never crosses subset boundaries. There is no confidence
gate, explicit occlusion detector, forward-backward propagation gate, or
failure-triggered SAM reinitialization in the evaluated implementation.

```bash
python -m wb3dgs.preprocess.leaf_instances \
  --points leaf_gaussians.xyz --output leaf_clusters.csv \
  --eps 0.08 --min-samples 20
```

The 1,080 ribbon-linked target leaves were audited before final trait
calculation. The paper reports 36 target leaves involved in merge errors and 18
fragmented target leaves at the selected DBSCAN setting; corrections must be
kept as an explicit audit file, never silently overwritten.

### 6. Train WB-3DGS

```bash
python -m wb3dgs.train --config configs/paper_defaults.yaml \
  --data data/processed/Seq-15/Plant-01 --split data/splits/inner_manifest.csv \
  --output outputs/Seq-15/Plant-01 --seed <ACTUAL_TRAINING_SEED>
```

The fixed paper checkpoint is iteration 30,000. See `RELEASE_AUDIT.md` before
claiming exact numerical reproduction.

### 7. Evaluate

```bash
python -m wb3dgs.eval.rendering --pred predictions.csv --output metrics_render.csv
python -m wb3dgs.eval.geometry --recon recon.xyz --reference heldout_lidar.xyz \
  --voxel 0.05 --threshold-cm 5 --output metrics_geometry.json
python -m wb3dgs.eval.semantics --pred pred_masks --reference manual_masks \
  --output metrics_semantic.json
```

RAFT temporal evaluation must use `raft-things.pth`, 24 recurrent updates,
mixed precision, and the 1.0-pixel forward-backward consistency threshold used
in the manuscript. Add the upstream checkpoint to `checkpoints/external/` and
record its SHA256.

### 8. Extract phenotypes

```bash
python -m wb3dgs.phenotype.extract \
  --gaussians canonical_gaussians.npz --output phenotypes.csv \
  --stem-slice-cm 5 --leaf-segments 10 --grid-mm 2
```

The paper uses pseudostem diameter at 0.10 m above ground, a 5-cm slice,
10 leaf centerline segments, a 2-mm leaf-area grid, and visibility count >3.
The destructive leaf-area calibration is `A_scan = k L W` with zero intercept;
the reported coefficient is `k=0.825` (60 calibration leaves from 20 plants),
with 30 independent validation leaves from 10 plants.

## Experiment configs

Each reported experiment has a dedicated YAML under `configs/experiments/`:

| Manuscript result | Config |
|---|---|
| Table 1 rendering comparison | `table1_rendering.yaml` |
| Table 2 LiDAR-constrained consistency | `table2_geometry.yaml` |
| Table 3 optimization-held-out LiDAR | `table3_heldout_geometry.yaml` |
| Tables 4-5 leave-one-out ablation | `table4_5_ablation.yaml` |
| Table 6 module combinations | `table6_combinations.yaml` |
| Table 7 phenotype accuracy | `table7_phenotype.yaml` |
| Table 8 mesh vs mesh-free | `table8_measurement_strategy.yaml` |
| Table 9 efficiency | `table9_efficiency.yaml` |
| Table S4 voxel/KNN sensitivity | `s4_voxel_knn.yaml` |
| Table S5 DBSCAN sensitivity | `s5_dbscan.yaml` |
| Table S6 partition sensitivity | `s6_partition.yaml` |
| Table S8 bootstrap CIs | `s8_bootstrap.yaml` |
| Table S9 semantic pseudo-labels | `s9_semantics.yaml` |

## Randomness and statistical unit

- Bootstrap seed: **42** (paper-reported).
- Neural-optimization seed: **recover from the original training log before release**;
- Bootstrap: sequence-cluster percentile bootstrap, **10,000** resamples for
  rendering/statistical comparisons, seed 42.
- Leaf-area coefficient CI: plant-cluster bootstrap, **2,000** resamples.
- The independent unit for reconstruction metrics is the acquisition sequence;
  individual plants, panoramas, or virtual views are not treated as independent
  bootstrap units.

## Hardware and timing reported in the manuscript

| Item | Reported value |
|---|---|
| CPU | Intel Core i9-10900K |
| GPU | NVIDIA RTX 3090 |
| GPU memory | 24 GB |
| WB-3DGS training | 52.4 min/plant |
| WB-3DGS inference | 85 FPS at 1080p |
| WB-3DGS peak VRAM | 15.2 GB |
| WB-3DGS iterations | 30,000 |

## Checkpoints



## Citation



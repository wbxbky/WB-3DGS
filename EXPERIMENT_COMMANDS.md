# Commands corresponding to manuscript experiments

The YAML files are the source of truth. Commands below show the intended public
CLI mapping; baseline repositories retain their upstream training entry points.

## Table 1

Train every method from initialization using the same outer fold and inner
manifest. Schedules: 30k for 3DGS/K-Planes/Spacetime/Dynamic3DGS/4DGS/WB-3DGS,
40k for Deformable-GS. Aggregate held-out view metrics:

```bash
python -m wb3dgs.eval.rendering --pred outputs/table1/per_view_metrics.csv --output outputs/table1/summary.csv
```

## Tables 2-3

```bash
python -m wb3dgs.eval.geometry --recon recon.xyz --reference lidar_reference.xyz --voxel 0.05 --threshold-cm 5 --output geometry.json
```

For Table 3, use only optimization-held-out LiDAR sweeps and query the dynamic
model at the median LiDAR timestamp within the plant ROI. Do not post-register
reconstruction to the reference.

## Tables 4-6

Run the variants defined in `table4_5_ablation.yaml` and
`table6_combinations.yaml` with the same split/training schedule. Rendering
ablations use six L3 sequences; geometric ablations use six L1 sequences.

## Tables 7-8

```bash
python -m wb3dgs.phenotype.extract --gaussians canonical_gaussians.npz \
  --ground-z <RANSAC_GROUND_Z> --output phenotypes.csv \
  --stem-slice-cm 5 --leaf-segments 10 --grid-mm 2
```

Use the same WB-3DGS canonical reconstruction/instance assignment for both
Table 8 measurement strategies.

## Table 9

Measure training wall time per plant, peak allocated GPU memory, and 1080p
single-view rendering FPS on the same RTX 3090. Synchronize CUDA before timing.

## Supplementary S4

Run exactly five configurations:

```text
(voxel=0.02,k=12), (0.05,6), (0.05,12), (0.05,24), (0.10,12)
```

Use fixed 0.05-m **evaluation** voxelization for all configurations.

## Supplementary S5

Run DBSCAN before manual correction at:

```text
(eps=0.05,MinPts=20), (0.08,10), (0.08,20), (0.08,40), (0.12,20)
```

Count affected target leaves, not cluster-level merge/split events.

## Supplementary S6/S8

```bash
python -m wb3dgs.stats.bootstrap --input sequence_metrics.csv \
  --cluster sequence_id --metric PSNR --resamples 10000 --seed 42
```

S6 requires paired resampling of the same sequence indices across protocols.

## Supplementary S9

Score the same 90 manual reference views (five per sequence), with no manual
correction before scoring. Propagation failure is `mIoU < 0.75` or complete loss
of either foreground class. The evaluated SAM+XMem pipeline has no confidence
gate, no explicit occlusion detector, and no failure-triggered SAM restart.


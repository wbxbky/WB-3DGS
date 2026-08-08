# Checkpoint release protocol

The manuscript evaluates WB-3DGS at the fixed **30,000-iteration** checkpoint.
At least one representative minimal checkpoint should be released. Recommended
choice: one of the Table S7 plants (preferably the L3 case Seq-14/Plant-18),
plus the config and split manifest needed to render its held-out views.

For every checkpoint publish:

```text
checkpoint: wb3dgs_seq14_plant18_iter30000.pth
iteration: 30000
sequence_id: Seq-14
plant_id: Plant-18
source_commit: <git SHA>
config_sha256: <SHA256>
split_manifest_sha256: <SHA256>
checkpoint_sha256: <SHA256>
training_seed: <actual training seed from log>
license: <confirmed redistribution license>
```




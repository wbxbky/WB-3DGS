# Data availability and representative subset

The current manuscript states that raw image datasets and phenotypic
measurement data are available from the corresponding author upon reasonable
request. For a stronger reproducibility release, publish the de-identified
representative subset described in `data/sample_subset/manifest.csv` together
with annotations, calibration metadata that may legally be shared, split
manifests, and all processing scripts.

## Recommended public-release statement

Use the paragraph below **only after the corresponding author/institution has
confirmed the restriction in brackets**:

> The complete raw multimodal dataset is not distributed as an unrestricted
> public download because [INSERT CONFIRMED LEGAL / PRIVACY / COMMERCIAL OR
> INSTITUTIONAL RESTRICTION]. To support reproducibility, we release a
> representative de-identified subset spanning the three evaluated wind
> regimes, together with calibration format definitions, acquisition metadata,
> manual reference annotations, deterministic split manifests, preprocessing
> scripts, evaluation code, and a minimal reproducibility checkpoint. Access to
> the remaining data may be requested from the corresponding author, subject to
> the applicable institutional/data-use conditions.

Do not claim privacy, commercial confidentiality, consent limitations, or a
contractual restriction unless it is actually documented.

## Minimum representative subset

The paper already identifies three traceable representative cases:

- L1: Seq-02 / Plant-15 (Fig. S1, Table S7)
- L2: Seq-08 / Plant-05 (Fig. S2, Table S7)
- L3: Seq-14 / Plant-18 (Fig. S3, Table S7)

For each case, release scene-optimization and held-out/guard manifests, RGB
virtual views, shareable LiDAR, LIO poses, semantic reference/pseudo-labels,
leaf-instance audit metadata, manual trait reference values, and processed
anchors. The held-out/guard role must be preserved in the public manifest.


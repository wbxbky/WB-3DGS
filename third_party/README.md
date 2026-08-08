# Third-party components

Record an exact upstream URL and immutable commit/tag for each component before
release. The manuscript identifies the algorithms but does not provide all
software revisions.

| Component | Paper usage | Release metadata required |
|---|---|---|
| 3D Gaussian Splatting rasterizer | differentiable rendering | repo URL + commit + license |
| FAST-LIO2 | LiDAR-inertial trajectory | repo URL + commit + local modifications |
| SAM | sparse-prompt seed masks | model variant + checkpoint + hash |
| XMem | temporal mask propagation | repo commit + checkpoint + hash |
| RAFT | temporal evaluation | `raft-things.pth`, upstream commit + hash |
| K-Planes | Table 1 baseline | repo commit + config |
| Deformable-GS | Tables 1/7 baseline | repo commit + 40k schedule |
| Spacetime Gaussians | Table 1 baseline | repo commit + 30k schedule |
| Dynamic 3D Gaussians | Table 1 baseline | repo commit + 30k schedule |
| 4DGS | Tables 1/9 baseline | repo commit + 30k schedule |

Keep third-party licenses intact. Do not copy code into this repository merely
to make installation easier unless redistribution is permitted.

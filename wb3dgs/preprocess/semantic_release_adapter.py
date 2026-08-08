from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description="Guarded adapter for the paper's SAM + XMem pseudo-label stage.")
    p.add_argument("--segment-frames", type=Path, required=True)
    p.add_argument("--point-prompts", type=Path, required=True)
    p.add_argument("--sam-checkpoint", type=Path, required=True)
    p.add_argument("--xmem-checkpoint", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    raise SystemExit(
        "Adapter intentionally stops: the manuscript does not identify the exact SAM variant, "
        "XMem revision/checkpoint, prompt cadence, or morphology kernel. Wire this CLI to the "
        "authors' original semantic preprocessing code before release; do not substitute guessed "
        "settings. Propagation must remain inside one scene-optimization segment and must not "
        "cross held-out/guard boundaries."
    )


if __name__ == "__main__":
    main()


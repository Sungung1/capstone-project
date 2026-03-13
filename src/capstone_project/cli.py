from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run_script(relative_path: str) -> None:
    runpy.run_path(str(ROOT / relative_path), run_name="__main__")


def train_main() -> None:
    """Launch the original capstone data-collection workflow."""
    _run_script("examples/capstone/script.py")


def inference_main() -> None:
    """Launch the original sensor-visualization workflow."""
    _run_script("examples/capstone/graph.py")

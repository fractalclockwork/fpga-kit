"""Write a headless ISE project into a run directory."""

import os
import shutil
from pathlib import Path

from boards import ROOT, load_board


def prepare_run(board_id, run_dir):
    board = load_board(board_id)
    run = Path(run_dir)
    run.mkdir(parents=True, exist_ok=True)
    prj = []
    # Paths are relative to the run directory. The container mounts the repo
    # at /work, so a host absolute path would not exist there.
    for source in board["sources"]:
        rel = Path(os.path.relpath((ROOT / source).resolve(), run.resolve()))
        prj.append(f'verilog work "{rel.as_posix()}"')
    (run / "project.prj").write_text("\n".join(prj) + "\n")
    xst = "\n".join(
        [
            "run",
            "-ifn project.prj",
            "-ofn project",
            f"-p {board['fpga']}",
            f"-top {board['top']}",
            "",
        ]
    )
    (run / "project.xst").write_text(xst)
    shutil.copy(ROOT / board["ucf"], run / "project.ucf")
    (run / "part.txt").write_text(board["fpga"] + "\n")
    return run

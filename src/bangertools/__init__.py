from typing import Annotated

from typer import Argument, Option

FilePath = Annotated[str, Argument(help="Path to the file")]
OutputPath = Annotated[
    str, Option(..., "--out", "--o", "--output", help="Optional file name to save the histogram to.")]
SnapshotPath = Annotated[str, Argument(help="The path to the snapshot file")]
AHFPath = Annotated[str, Argument(help="The path to the snapshot halo file")]
PathList = Annotated[list[str], Argument(help="A list of snapshot files or paths containing snapshots")]

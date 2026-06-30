from typing import Annotated

from typer import Argument

FilePath = Annotated[str, Argument(help="Path to the file")]
SnapshotPath = Annotated[str, Argument(help="The path to the snapshot file")]
AHFPath = Annotated[str, Argument(help="The path to the snapshot halo file")]
PathList = Annotated[list[str] | str, Argument(help="A list of snapshot files or paths containing snapshots")]

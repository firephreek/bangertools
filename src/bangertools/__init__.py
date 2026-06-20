from typing import Annotated
from typer import Argument

FilePath = Annotated[str, Argument(help="Path to the file")]
SnapshotPath = Annotated[str, Argument(help="The path to the snapshot file")]
AHFPath = Annotated[str, Argument(help="The path to the snapshot halo file")]
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pynbody
from typer import Typer

from bangertools import PathList
from bangertools.common import util
from bangertools.common.util import appstate

app = Typer()


def save_data_to_parq_file(file_paths: PathList, out: str, cols: str, exclude_source: bool, ignore_missing_cols: bool):
    """
    Extract a set of columns from all snapshots found in the provided paths and write them
    to a Pandas-compatible Parquet file.
    """

    snapshot_paths = util.get_snapshots(file_paths)
    cols = cols.split(",")
    writer = None

    try:
        util.verbose(f"Loading snapshots from '{[path.as_posix() for path in snapshot_paths]}'")
        for path in snapshot_paths:
            util.verbose(f"Loading {path}")
            sim = pynbody.load(path)

            util.verbose(f"Checking for missing columns")
            missing = [c for c in cols if
                       c not in sim.loadable_keys() and c not in sim.keys()]  # TODO: is there a reason we're not using `all_keys()` here? --snc

            if missing:
                if not ignore_missing_cols:
                    raise KeyError(f"Snapshot is missing fields: {missing}")
                else:
                    util.warn(f"Ignoring missing cols '{cols}' in {path}'")

            util.verbose(f"Creating table schema")

            cols_schema = {col: np.asarray(sim[col]) for col in cols}

            table = pa.table(cols_schema)

            if exclude_source:
                table = table.append_column(
                    "source",
                    pa.array([path.name] * table.num_rows)
                )

            if writer is None:
                if appstate.verbose:
                    util.verbose(f"Initializing Writer to {out}")
                    util.panel(f"Schema:", table.schema.to_string())

                writer = pq.ParquetWriter(out, table.schema, compression="zstd")

            util.verbose(f"Writing data to {out}")
            writer.write_table(table)
        # Final stats message
        if writer:
            writer.close()
        pf = pq.ParquetFile(out)
        print(pf.metadata)
    except Exception as e:
        util.err(e)


if __name__ == '__main__':
    app()

from pathlib import Path
from typing import Annotated

import matplotlib.pyplot as plt
import pynbody
import typer

from bangertools.common import util

OutputPath = Annotated[str, typer.Option(help="Optional file name to save the histogram to.")]
COLORS = ["blue", "green", "red", "cyan", "yellow", "black", "orange",
          "purple", "brown", "gray", "olive", "lime", "teal", "navy", "maroon",
          "gold", "turquoise", "indigo", "violet", "khaki", "crimson"]


class HistogramBase:
    def __init__(self,
                 key_field,
                 title=None,
                 xlabel=None,
                 ylabel=None,
                 bins=None,
                 edgecolor='black',
                 figsize=(8, 6)):
        self.facecolors = []
        self._color_idx = 0
        self._bins = bins
        self.figsize = figsize
        self.data = []
        self.labels = []
        self.transforms = []
        self.filters = []
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.snapshot_paths = []
        self.key = key_field
        self.edgecolor = edgecolor
        self.fig, self.ax = plt.subplots()

    def get_next_color(self):
        color = COLORS[self._color_idx]  # Get the next color from the collection
        self._color_idx += 1  # don't forget to increment the list index
        return color

    def add_collection(self, snapshot_path, label=None, filter=None, transform=None, color=None, edgecolor="black",
                       filled=True):
        snapshot_paths = util.get_snapshots(snapshot_path)

        snapshot_data = []
        for path in snapshot_paths:
            try:
                util.verbose(f"Loading {path}")
                sim = pynbody.load(path)

                if self.key not in sim.s.loadable_keys():
                    util.err(f"{self.key} not found in {path}. File not loaded.")
                    continue
                elif len(sim.s) == 0:
                    util.verbose(f"No stars found in {path}")
                    continue

                sim.physical_units()
                if not filter:
                    values = sim.stars[self.key]
                else:
                    values = sim.stars[filter][self.key]

                snapshot_data.extend(values)

            except Exception as e:
                util.err(f"Unexpected error: {e}")

        if transform:
            snapshot_data = transform(snapshot_data)

        if not label:  # No explict label, we'll have to build one...
            label = Path(snapshot_path).name
        self.labels.append(label)
        self.facecolors.append(self.get_next_color())
        self.data.append(snapshot_data)

    def generate(self, output_file=None):
        raise NotImplementedError("This method must be implemented in a derived class")


class LayeredHistogram(HistogramBase):
    def generate(self, output_file=None):
        import numpy as np

        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection="3d")

        # Use common bins across all snapshots
        bins = np.histogram_bin_edges(np.concatenate(self.data), bins=self._bins)

        # Plot each histogram on a separate y-plane
        z = zip(self.data, self.labels, self.facecolors)

        for i, (data, label, color) in enumerate(z):
            counts, edges = np.histogram(data, bins=bins)

            # histogram bar positions
            xpos = edges[:-1]
            dx = np.diff(edges)

            # y position is the "snapshot depth"
            ypos = np.full_like(xpos, i, dtype=float)
            dy = np.ones_like(xpos) * 0.3

            # z is the histogram height
            zpos = np.zeros_like(xpos)
            dz = counts

            ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=color, alpha=0.7, shade=True)

        ax.set_xlabel(self.xlabel)
        ax.set_ylabel("Snapshot")
        ax.set_zlabel("Count")
        ax.set_title(self.title)

        ax.set_yticks(range(len(self.labels)))
        ax.set_yticklabels(self.labels)

        # Good 3/4 viewing angle
        ax.view_init(elev=25, azim=-60)

        if output_file:
            plt.savefig(output_file, bbox_inches="tight")
        else:
            plt.show()

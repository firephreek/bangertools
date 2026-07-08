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
                util.print_verbose(f"Loading {path}")
                sim = pynbody.load(path)

                if self.key not in sim.s.loadable_keys():
                    util.print_error(f"{self.key} not found in {path}. File not loaded.")
                    continue
                elif len(sim.s) == 0:
                    util.print_verbose(f"No stars found in {path}")
                    continue

                sim.physical_units()
                if not filter:
                    values = sim.stars[self.key]
                else:
                    values = sim.stars[filter][self.key]

                snapshot_data.extend(values)

            except Exception as e:
                util.print_error(f"Unexpected error: {e}")

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

    def generate(self, output_file: OutputPath = ""):
        # self.ax.hist(self.data, self.bins, alpha=0.5, label=self.labels, histtype="bar", facecolor=self.facecolors)
        # data = self.ax.containers

        # max_len = max([len(c) for c in self.ax.containers])
        # for idx in range(max_len):
        #     cur_set = []
        #     for c in self.ax.containers:
        #         cur_set.append([c.tops[idx]])
        #         cur_set.sort()

        result = self.ax.hist(self.data, self._bins, label=self.labels, facecolor=self.facecolors)

        self.ax.legend()
        self.ax.set_title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()
        plt.show()

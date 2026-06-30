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


class StackedHistogram:
    color_idx = 0
    data = []

    def __init__(self,
                 key,
                 title="Histogram of Star Particles with tform < 1",
                 xlabel="tform",
                 ylabel="Number of Star Particles",
                 legend=list,
                 bins=20
                 ):
        self.key = key
        self.bins = bins
        self.facecolors = []
        self.legend = legend
        self.labels = []
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

        self.fig, self.ax = plt.subplots()

    def add_snapshots(self, path, label=None, filter=None, transform=None, color=None, edgecolor="black", filled=True):
        keys = []
        if not color:  # If a color isn't specified, pick the next one from the list...
            self.facecolors.append(COLORS[self.color_idx])
            self.color_idx += 1  # ...and don't forget to increment the list index

        if not label:  # No explict label, we'll have to build one...
            label = Path(path).name
        self.labels.append(label)
        snapshot_paths = util.get_snapshots(path)
        for path in snapshot_paths:
            try:
                sim = pynbody.load(path)
                sim.physical_units()
                if len(sim.s) == 0 or self.key not in sim.s.loadable_keys():
                    continue

                if filter:
                    values = sim.stars[filter][self.key]
                else:
                    values = sim.stars[self.key]
                keys.extend(values)
            except Exception as e:
                # TODO: Handle this better
                pass
        if transform:
            keys = transform(keys)

        self.data.append(keys)

    def generate(self, output_file: OutputPath = None):
        self.ax.hist(self.data, self.bins, label=self.labels, histtype="barstacked", facecolor=self.facecolors)
        self.ax.legend()
        self.ax.set_title(self.title)

        if not output_file:
            plt.show()
        else:
            plt.savefig(output_file)
        plt.show()

class Histogram:
    def __init__(self,
                 snapshot_paths,
                 key_field,
                 title=None,
                 xlabel=None,
                 ylabel=None,
                 bins=None,
                 edgecolor='black',
                 figsize=(8, 6)):
        self.figsize = figsize
        self.transforms = []
        self.filters = []
        self.bins = bins
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.snapshot_paths = snapshot_paths
        self.key = key_field
        self.edgecolor = edgecolor

    def add_transform(self, transform):
        self.transforms.append(transform)

    def add_filter(self, filter):
        self.filters.append(filter)

    def generate(self, output_file=None):
        """
        Generate a histogram of tform values less than 1 from all Tipsy
        snapshots in a directory.
        """

        keys = []

        for path in self.snapshot_paths:

            try:
                sim = pynbody.load(path)
                sim.physical_units()

                if len(sim.s) == 0 or self.key not in sim.s.loadable_keys():
                    continue

                values = None
                if self.filters:
                    for filter in self.filters:
                        values = sim.stars[filter][self.key]
                else:
                    values = sim.stars[self.key]

                keys.extend(values)

            except Exception as e:
                pass

        for transform in self.transforms:
            keys = transform(keys)

        plt.figure(figsize=self.figsize)
        plt.hist(keys, self.bins, edgecolor=self.edgecolor)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        plt.tight_layout()

        if not output_file:
            plt.show()
        else:
            plt.savefig(output_file)

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pynbody

from bangertools.common import util

COLORS = ["blue", "green", "red", "cyan", "yellow", "black", "orange",
          "purple", "brown", "gray", "olive", "lime", "teal", "navy", "maroon",
          "gold", "turquoise", "indigo", "violet", "khaki", "crimson"]


class HistogramBase:
    def __init__(self,
                 key_field,
                 title=None,
                 xlabel=None,
                 ylabel=None,
                 bins=10,
                 edgecolor='black',
                 figsize=(8, 6)):
        self.facecolors = []
        self._color_idx = 0
        self.bins = bins
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

    def add_data(self, data, label=None, color=None):

        self.facecolors.append(color or self.get_next_color())
        self.labels.append(label)
        self.data.append(data)

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
        self.facecolors.append(color or self.get_next_color())
        self.data.append(snapshot_data)

    def generate(self, output_file=None):
        raise NotImplementedError("This method must be implemented in a derived class")


class LayeredHistogram(HistogramBase):
    def __init__(self, key_field, alpha=None, z_sort=False, **kwargs):
        super().__init__(key_field, **kwargs)
        self.alpha = alpha
        self.sort = z_sort

    def generate(self, output_file: str = ""):
        datasets = list(zip(self.data, self.labels, self.facecolors))

        # Legend order is always insertion order.
        legend_labels = [label for _, label, _ in datasets]

        # Determine drawing order.
        if self.sort:
            draw_datasets = sorted(
                datasets,
                key=lambda x: max(np.histogram(x[0], bins=self.bins)[0])
            )
        else:
            draw_datasets = datasets

        # Plot back-to-front.
        for data, label, color in reversed(draw_datasets):
            self.ax.hist(
                data,
                self.bins,
                label=label,
                color=color,
                alpha=self.alpha
            )

        # Reorder legend to insertion order.
        handles, labels = self.ax.get_legend_handles_labels()
        handle_map = dict(zip(labels, handles))
        self.ax.legend([handle_map[l] for l in legend_labels], legend_labels)
        self.data = self.data[::-1]
        self.labels = self.labels[::-1]
        self.facecolors = self.facecolors[::-1]

        self.ax.set_title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()


class BarHistogram(HistogramBase):
    def generate(self, output_file: str = ""):
        self.ax.hist(self.data, self.bins, label=self.labels, histtype="bar", facecolor=self.facecolors)
        self.ax.legend()
        self.ax.set_title(self.title)

        if not output_file:
            plt.show()
        else:
            plt.savefig(output_file)
        plt.show()


class StackedHistogram(HistogramBase):
    def generate(self, output_file: str = ""):
        self.ax.hist(self.data, self.bins, label=self.labels, histtype="barstacked", facecolor=self.facecolors)
        self.ax.legend()
        self.ax.set_title(self.title)

        if not output_file:
            plt.show()
        else:
            plt.savefig(output_file)
        plt.show()


class Histogram(HistogramBase):
    def generate(self, output_file: str = ""):
        """
        Generate a histogram of tform values less than 1 from all Tipsy
        snapshots in a directory.
        """

        plt.figure(figsize=self.figsize)
        plt.hist(self.data, self.bins, edgecolor=self.edgecolor)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        plt.tight_layout()

        if not output_file:
            plt.show()
        else:
            plt.savefig(output_file)

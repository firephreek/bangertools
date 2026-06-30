import matplotlib.pyplot as plt
import pynbody


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
        self.filters = []
        self.bins = bins
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.snapshot_paths = snapshot_paths
        self.key = key_field
        self.edgecolor = edgecolor

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

    def add_filter(self, filter):
        self.filters.append(filter)

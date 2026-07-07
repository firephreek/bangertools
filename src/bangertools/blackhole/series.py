import matplotlib.pyplot as plt
import numpy as np
import pynbody


class TimeSeries:
    def __init__(self,
                 snapshot_paths,
                 key_field,
                 title=None,
                 xlabel="Time",
                 ylabel=None,
                 figsize=(8, 6),
                 marker='o',
                 linestyle='-'):
        self.figsize = figsize
        self.transforms = []
        self.filters = []
        self.snapshot_paths = snapshot_paths
        self.key = key_field

        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel if ylabel else f"Average {key_field}"

        self.marker = marker
        self.linestyle = linestyle

    def add_transform(self, transform):
        self.transforms.append(transform)

    def add_filter(self, filter):
        self.filters.append(filter)

    def generate(self, output_file=None):
        """
        Generate a time series of the average value of `key_field`
        across all Tipsy snapshots.
        """

        times = []
        averages = []

        for path in self.snapshot_paths:

            try:
                sim = pynbody.load(path)
                sim.physical_units()

                # if len(sim.s) == 0 or self.key not in sim.s.loadable_keys():
                #     continue
                #
                # # Get particle values
                # if self.filters:
                #     values = sim.stars[self.key]
                #     for filt in self.filters:
                #         values = sim.stars[filt][self.key]
                # else:
                values = sim.gas[self.key]

                # Apply transforms
                for transform in self.transforms:
                    values = transform(values)

                # if len(values) == 0:
                #     continue

                # Get simulation time
                time = float(sim.properties["time"])

                times.append(time)
                averages.append(values)

            except Exception as e:
                print(e)
                pass

        if len(times) == 0:
            raise RuntimeError("No valid snapshots found.")

        # Sort by time
        order = np.argsort(times)
        times = np.array(times)[order]
        averages = np.array(averages)[order]

        plt.figure(figsize=self.figsize)
        plt.plot(times,
                 averages,
                 marker=self.marker,
                 linestyle=self.linestyle)

        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        plt.tight_layout()

        if output_file is None:
            plt.show()
        else:
            plt.savefig(output_file)

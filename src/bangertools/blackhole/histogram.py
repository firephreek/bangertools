import matplotlib.pyplot as plt
import pynbody


def generate_hist(snapshot_paths):
    """
    Generate a histogram of tform values less than 1 from all Tipsy
    snapshots in a directory.
    """

    tforms = []

    for snapshot_path in snapshot_paths:
        try:
            sim = pynbody.load(snapshot_path)
            sim.physical_units()

            if len(sim.s) == 0 or 'tform' not in sim.s.loadable_keys():
                continue

            values = sim.s['tform']
            values = values[values < 1]

            tforms.extend(values)

        except Exception as e:
            print(f"Skipping {snapshot_path}: {e}")

    if len(tforms) == 0:
        print("No tform values less than 1 were found.")
        return

    plt.figure(figsize=(8, 6))
    plt.hist(tforms, bins=50, edgecolor='black')
    plt.xlabel("tform")
    plt.ylabel("Number of Star Particles")
    plt.title("Histogram of Star Particles with tform < 1")
    plt.tight_layout()
    plt.show()

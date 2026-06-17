import os
from collections import Counter
from typing import Annotated

import matplotlib.pyplot as plt
import numpy as np
import pynbody as pn
from pandas import Series, read_csv, DataFrame
from typer import Argument, Typer

# setup typer. This gives us a nice cli framework to call commands with
app = Typer()

# constants
HUBBLE_CONST = 0.67  # Hubble param to convert M_sun/h to M_sun
HI_RES_CUT = 0.0  # fMhires threshold
G_CGS = 6.674e-8
MSOL_CGS = 1.989e33
KPC_CGS = 3.086e21
M_UNIT = 1.84793e16
R_UNIT = 50000.0

# helper types for the cli
SnapshotPath = Annotated[str, Argument(help="The path to the snapshot file")]
AHFPath = Annotated[str, Argument(help="The path to the snapshot file")]


def load_snapshot(file_path: str, convert_units: bool = True):
    snapshot = pn.load(file_path)
    if convert_units:
        snapshot.physical_units()  # converting code units to physical units
    return snapshot


def load_AHF(csv_file: str):
    AHF = read_csv(csv_file, sep='\t', header=0)
    return AHF

# This is a decorator that turns the function into a cli command (https://typer.tiangolo.com/tutorial/commands/arguments/)
# The Annotation is a type hint that typer can use to automatically populate the help menu.
@app.command(name="keys")
def snap_keys(file_path: Annotated[str, Argument(help="Path to the file")]):
    """
    List all the keys in the AHF halo catalog or snapshot file
    """
    try:
        snapshot = load_snapshot(file_path)
        print(f"keys inside the snapshot are: {snapshot.loadable_keys()}")
    except OSError:  # Invalid snap file, must be an AHF...
        AHF = load_AHF(file_path)
        print(f"keys inside the AHF are: {AHF.columns.tolist()}")
    except:
        print(f"Unrecognized file {file_path}")


# The SnapshotPath defined here is an Annotated class, just the one we defined earlier.
@app.command(name="minmax")
def dm_minmax(snapshot_path: SnapshotPath):
    """
    Print min/max DM particle mass and their ratio
    """
    snapshot = load_snapshot(snapshot_path)

    print(f" minimum DM particle mass: {snapshot.dm['mass'].min(): .3e}")
    print(f" max DM particle mass: {snapshot.dm['mass'].max(): .3e}")
    print(f" ratio: {snapshot.dm['mass'].max() / snapshot.dm['mass'].min(): .3e}")


@app.command(name="info")
def AHF_halo_info(ahf_path: AHFPath):
    """
    Print total number of halos in AHF
    """

    AHF = load_AHF(ahf_path)
    print(f"total number of halos: {len(AHF)}")


@app.command(name="mass")
def AHF_halo_mass(ahf_path: AHFPath):
    """
    Print halo masses and most/least massive halo
    """
    AHF = load_AHF(ahf_path)

    unique_vals = sorted(AHF['fMhires(38)'].unique())
    AHF = AHF[(AHF['#ID(1)'] != 0) & (AHF['fMhires(38)'] >= HI_RES_CUT)].copy()
    if AHF.empty:
        print(f"No halos matched hi_res_cut = {HI_RES_CUT} (fMhires >= {HI_RES_CUT}).")
        print(f"fMhires range in catalog: {unique_vals[0]:.3f} – {unique_vals[-1]:.3f}")
        return
    AHF['Mhalo(4)'] = AHF['Mhalo(4)'] / HUBBLE_CONST

    ids = AHF['#ID(1)']
    masses = AHF['Mhalo(4)']

    print(AHF[['#ID(1)', 'Mhalo(4)']].to_string(index=False, formatters={'Mhalo(4)': '{:.3e} M_sun'.format}))
    print(f"most massive: halo {ids[masses.idxmax()]} with {masses.max():.3e} M_sun")
    print(f"least massive: halo {ids[masses.idxmin()]} with {masses.min():.3e} M_sun")


@app.command(name="count")
def BH_count(snapshot_path: SnapshotPath):
    """
    Counts BHs in the snapshot
    """

    snapshot = load_snapshot(snapshot_path)
    bhs = snapshot.star[snapshot.star['tform'] < 0]
    print(f'total number of BHs: {len(bhs)}')


@app.command("halos")
def BH_halos(snapshot_path: SnapshotPath, ahf_path: AHFPath):
    """
    Print which halos contain BHs and their masses
    """

    snapshot = load_snapshot(snapshot_path)
    AHF = load_AHF(ahf_path)
    bhs = snapshot.star[snapshot.star['tform'] < 0]
    bh_grp = bhs['amiga.grp']  # halo ID each BH belongs to
    counts = Counter(bh_grp)  # number of BHs per halo [halo_id: count]

    for halo_id, n in sorted(counts.items()):  # unpacking the dictionary into halo ID and count (key, value)
        if halo_id == 0:
            continue  # skip halo 0
        mass = AHF.loc[AHF['#ID(1)'] == halo_id, 'Mhalo(4)'].values[
                   0] / HUBBLE_CONST  # selecting data by location, true/fals mask, true for halo ID matches the loop
        print(f"halo {halo_id} has {n} BH(s) with {mass:.3e} M_sun")


@app.command(name="halo-masses")
def mass_range(file_path="halo_masses.csv"):
    """
    Print min/max halo mass from the saved CSV
    """
    df = read_csv(file_path)
    masses: Series = df['Mhalo(4)'] / HUBBLE_CONST
    print(f"mass range of clean halos in halo_masses.csv:")
    print(f"min mass: {masses.min():.3e} M_sun")
    print(f"max mass: {masses.max():.3e} M_sun")


@app.command(name="write-csv")
def write_csvs(snapshot_path: SnapshotPath, ahf_path: AHFPath):
    """
    Write halo_masses.csv and BH_masses.csv to be used for the occupation fraction plot
    """

    ahf = load_AHF(ahf_path)
    snapshot = load_snapshot(snapshot_path)
    correct_masses = ahf[(ahf['#ID(1)'] != 0) & (ahf['fMhires(38)'] >= HI_RES_CUT)][['#ID(1)', 'Mhalo(4)']].copy()
    mass_of_halo_1 = ahf['Mhalo(4)'][1]
    print(f" mass of halo 1 is: {mass_of_halo_1}")
    correct_masses = correct_masses[correct_masses <= mass_of_halo_1]
    correct_masses.to_csv('halo_masses.csv', index=False)
    # s['amiga.grp']  # pre loading group array
    bhs = snapshot.star[snapshot.star['tform'] < 0]
    counts = Counter(bhs['amiga.grp'])  # counting how many BHs are in each halo, returns a dictionary {halo_id: count}
    print(f" the val of counts is: {counts}")

    BH_halo_id, BH_halo_masses = [], []
    # for halo_id, n in sorted(counts.items()):
    #   if halo_id == 0:
    #      continue

    # need to print the counts
    #  row = ahf.loc[ahf['#ID(1)'] == halo_id] # select the row in AHF catalog where halo ID matches current halo ID in loop
    # print(f" the val of row is {row}") # print the row to check if it's selecting the correct halo
    # if row.empty or row['fMhires(38)'].values[0] < hi_res_cut:
    #     continue
    BHhalos = bhs['amiga.grp']
    print(f" the val of BHhalos is {BHhalos}")
    halos = np.unique(BHhalos)
    halos = halos[halos != 0]
    print(f" the val of halos is {halos}")

    # getting halo masses
    for halo_id in halos:
        row = ahf.loc[ahf['#ID(1)'] == halo_id]

        mass = row['Mhalo(4)'].values[0]  # take out halo mass from that row
        BH_halo_id.append(halo_id)  # add the halo ID and mass to the BH halo lists
        BH_halo_masses.append(mass)

    dfBH = DataFrame({'halo_id': BH_halo_id, 'Mhalo(4)': BH_halo_masses})
    dfBH.to_csv('BH_masses.csv', index=False)
    print("saved halo_masses.csv and BH_masses.csv")


@app.command(name="plot")
def plot_of_pretty(n: Annotated[int, Argument(help="Seed value")]):
    """
    Plot with bin counts annotated and color coding
    """

    halo_mass = read_csv('halo_masses.csv')['Mhalo(4)'] / HUBBLE_CONST
    BH_halo_mass = read_csv('BH_masses.csv')['Mhalo(4)'] / HUBBLE_CONST

    log_min = np.floor(
        np.log10(halo_mass.min()))  # find log 10 of the least massive halo, round down to nearest integer for min edge
    log_max = np.ceil(
        np.log10(halo_mass.max()))  # find log 10 of the most massive halo, round up to nearest integer for max edge
    bin_edges = np.logspace(log_min, log_max, n + 1)

    def count_in_bins(m, e, label=''):
        counts = []
        for lo, hi in zip(e[:-1], e[1:]):  # loop through the bin edges, take the lower and upper edge of each bin
            c = np.count_nonzero((m > lo) & (m <= hi))  # count # of halos in that bin using boolean mask
            print(f"  {label} bin [{lo:.3e}, {hi:.3e}]: {c}")  # print the count for that bin with the bin edges
            counts.append(c)
        return np.array(counts)

    print("ALL halos per bin:")
    count_all = count_in_bins(halo_mass, bin_edges, label='ALL')
    print("BH halos per bin:")
    count_BH = count_in_bins(BH_halo_mass, bin_edges, label='BH')

    occ_frac = np.where(count_all > 0, count_BH / count_all,
                        0.0)  # where condition is true, calc the fraction, where false, == 0
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])  # geometric mean for log bins

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.plot(bin_centers, occ_frac, lw=2, zorder=2)
    ax.scatter(bin_centers, occ_frac, s=80, zorder=3)

    for x, y, n_all, n_bh in zip(bin_centers, occ_frac, count_all, count_BH):
        ax.annotate(
            f'{n_bh}/{n_all}',
            xy=(x, y),
            xytext=(0, 10),
            textcoords='offset points',
            ha='center',
            fontsize=9
        )

    ax.set_xscale('log')
    #    ax.set_yscale('log')
    ax.set_xlabel(r'$M_\mathrm{halo}\ [M_\odot]$', fontsize=13)
    ax.set_ylabel('BH occupation fraction', fontsize=13)
    ax.set_title(f'BH occupation fraction vs halo mass ({n} bins)', fontsize=13)
    ax.set_ylim(-0.05, 1.15)

    plt.tight_layout()
    plt.show()


@app.command(name="vkick")
def conv_vkick(value: Annotated[float, Argument(help="The floating point value of the kick")]):
    """
    Convert a kick velocity from code units to km/s
    """

    dKmPerSecUnit = (1.0 / 1e5) * np.sqrt(G_CGS * M_UNIT * MSOL_CGS / (R_UNIT * KPC_CGS))
    print(f"{value} code units = {value * dKmPerSecUnit:.4f} km/s")


@app.command(name="fMhires")
def check_fMhires(ahf_path: AHFPath):
    """
    Prints fMhires values for the first few halos to verify their values
    """
    AHF = load_AHF(ahf_path)
    print(AHF[['#ID(1)', 'Mhalo(4)', 'fMhires(38)']].head(10).to_string())


@app.command(name="zeros")
def check_snapshot_zeros(snapshot_path: SnapshotPath):
    """
    Check for zero mass particles in the snapshot
    """
    snapshot = load_snapshot(snapshot_path)

    print(f"Checking snapshot: {snapshot.filename}")
    # checking for 0 mass particles
    zero_dm = np.sum(snapshot.dm['mass'] == 0)
    zero_gas = np.sum(snapshot.gas['mass'] == 0)
    zero_star = np.sum(snapshot.star['mass'] == 0)
    nan_mass = np.sum(np.isnan(snapshot.dm['mass'])) + np.sum(np.isnan(snapshot.gas['mass'])) + np.sum(
        np.isnan(snapshot.star['mass']))

    print(f"Number of zero mass DM particles: {zero_dm}")
    print(f"Number of zero mass gas particles: {zero_gas}")
    print(f"Number of zero mass star particles: {zero_star}")
    print(f"Number of NaN mass particles:{nan_mass}")

    if zero_dm > 0:
        print(f"  WARNING: {zero_dm} zero mass DM particles found")
    else:
        print("  OK: No zero mass DM particles found.")
    if zero_gas > 0:
        print(f"  WARNING: {zero_gas} zero mass gas particles found")
    else:
        print("  OK: No zero mass gas particles found.")
    if zero_star > 0:
        print(f"  WARNING: {zero_star} zero mass star particles found")
    else:
        print("  OK: No zero mass star particles found.")
    if nan_mass > 0:
        print(f"  WARNING: {nan_mass} NaN mass particles found")
    else:
        print("  OK: No NaN mass particles found.")


@app.command(name="fix-zeros")
def fix_zeros(snapshot_path: SnapshotPath):
    """
    Create a clean snapshot without zero mass particles and update startruns.txt to use it
    """

    snapshot = load_snapshot(snapshot_path)
    snapshot_path = snapshot.filename

    if snapshot_path.endswith('.original'):
        print("Snapshot is already a backup (.original), skipping.")
        return

    step = snapshot_path.split('.')[-1]  # split by . and take the last part (the 6 digits)
    startrun_path = f"{step}.startrun"
    original_path = snapshot_path + ".original"

    # rename the original snapshot to .original
    os.rename(snapshot_path, original_path)
    print(f"Original snapshot backed up to: {original_path}")

    # load the backup and strip zero-mass particles
    s_raw = pn.load(original_path)
    print(f"Fixing snapshot: {snapshot_path}")
    clean = s_raw[s_raw['mass'] != 0]

    # write clean snapshot back to the original name
    clean.write(filename=snapshot_path, fmt=pn.tipsy.TipsySnap)
    print(f"Cleaned snapshot saved to: {snapshot_path}")

    # update startrun — the name stays the same so this is mostly a no-op,
    with open(startrun_path, 'r') as f:
        content = f.read()
    content = content.replace(
        f"ic_filename = {original_path}",
        f"ic_filename = {snapshot_path}"
    )
    # also catch the case where it previously pointed to a .clean path
    content = content.replace(
        f"ic_filename = {snapshot_path}.clean",
        f"ic_filename = {snapshot_path}"
    )
    with open(startrun_path, 'w') as f:
        f.write(content)
    print(f"Updated startrun: {startrun_path}")


if __name__ == '__main__':
    app()

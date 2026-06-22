#!/usr/bin/env python3

"""
extract_core_history.py

Find particles that end up in the final collapsed core and
track them backward through all snapshots.

Outputs:
    core_particle_ids.npy
    core_trajectories.npz

Trajectory shape:
    (n_particles, n_snapshots, 3)
"""

from pathlib import Path
import re

import numpy as np
import pynbody


# =====================================================
# CONFIG
# =====================================================

FINAL_CORE_PARTICLES = 1000
SNAP_PATTERN = r"o9M_1\.\d+"


# =====================================================
# FIND SNAPSHOTS
# =====================================================

snapshots = sorted(
    str(f)
    for f in Path(".").glob("o9M_1.*")
    if re.fullmatch(SNAP_PATTERN, f.name)
)

if not snapshots:
    raise RuntimeError("No snapshots found")

print(f"Found {len(snapshots)} snapshots")


# =====================================================
# FINAL SNAPSHOT
# =====================================================

final_snap = snapshots[-1]

print(f"Loading final snapshot: {final_snap}")

s = pynbody.load(final_snap)

pos = np.asarray(s["pos"])
phi = np.asarray(s["phi"])
iord = np.asarray(s["iord"])

# deepest potential particle
core_idx = np.argmin(phi)

core_center = pos[core_idx]

print("Core center particle:")
print(f"  ID  = {iord[core_idx]}")
print(f"  phi = {phi[core_idx]}")

# distance from core center
r = np.linalg.norm(pos - core_center, axis=1)

# nearest N particles
nearest = np.argsort(r)[:FINAL_CORE_PARTICLES]

core_ids = iord[nearest]

print()
print(f"Selected {len(core_ids)} final-core particles")

np.save("core_particle_ids.npy", core_ids)


# =====================================================
# BUILD TRAJECTORIES
# =====================================================

core_set = set(map(int, core_ids))

traj = []

for snap_index, snapfile in enumerate(snapshots):

    print(
        f"[{snap_index + 1}/{len(snapshots)}] "
        f"{Path(snapfile).name}"
    )

    s = pynbody.load(snapfile)

    ids = np.asarray(s["iord"])
    pos = np.asarray(s["pos"])

    # map particle ID -> index for only core particles
    id_to_idx = {
        int(pid): idx
        for idx, pid in enumerate(ids)
        if int(pid) in core_set
    }

    frame_positions = np.full(
        (len(core_ids), 3),
        np.nan,
        dtype=np.float32,
    )

    for j, pid in enumerate(core_ids):

        idx = id_to_idx.get(int(pid))

        if idx is not None:
            frame_positions[j] = pos[idx]

    traj.append(frame_positions)

traj = np.stack(traj, axis=1)

print()
print("Trajectory array shape:", traj.shape)
print("(particles, snapshots, xyz)")


# =====================================================
# SAVE
# =====================================================

np.savez_compressed(
    "core_trajectories.npz",
    particle_ids=core_ids,
    trajectories=traj,
    snapshots=np.array(snapshots),
)

print()
print("Saved:")
print("  core_particle_ids.npy")
print("  core_trajectories.npz")
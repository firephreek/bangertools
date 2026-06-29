def load_snapshot(file_path: str, convert_units: bool = True):
    import pynbody as pn
    snapshot = pn.load(file_path)
    if convert_units:
        snapshot.physical_units()  # converting code units to physical units
    return snapshot

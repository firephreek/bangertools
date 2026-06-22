import numpy as np
from matplotlib import cm


def color_from_temperature(temp):
    temp = np.nan_to_num(temp)
    logt = np.log10(np.clip(temp, 1.0, None))
    tmin = np.percentile(logt, 5)
    tmax = np.percentile(logt, 95)

    x = np.clip((logt - tmin) / (tmax - tmin + 1e-12), 0, 1)

    return cm.plasma(x).astype(np.float32)

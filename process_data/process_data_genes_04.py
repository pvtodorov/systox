import pandas as pd
import numpy as np
import os

# transform all values from medianmax to log2 space
# also filters values outside [0.5, 2] as 0
# also drop any columns where all values are 0


def safe_log2(x):
    n2 = 1
    if np.isfinite(x):
        if (x >= 2) or (x <= 0.5):
            n2 = x
    return np.log2(n2)


infolder = '../data/processed_data/01/LISS/03/'
outfolder = '../data/processed_data/01/LISS/04/'

if not os.path.exists(outfolder):
    os.makedirs(outfolder)

safe_log2_v = np.vectorize(safe_log2, otypes=[np.float])

files = os.listdir(infolder)
for i in files:
    df0 = pd.read_csv(infolder + i)
    columns = df0.columns.tolist()
    columns.remove('COMPOUND')
    compounds = df0['COMPOUND'].tolist()
    a = df0.as_matrix(columns=columns)
    b = safe_log2_v(a)
    df1 = pd.DataFrame(data=b, index=compounds, columns=columns)
    df1 = df1.reset_index().rename(columns={'index': 'COMPOUND'})
    df1 = df1.T[df1.any()].T # drop zero-only columns
    df1.to_csv(outfolder + 'log_' + i, index=False)

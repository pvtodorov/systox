import pandas as pd
import os

infolder = '../data/processed_data/01/Imaging/01/'
infile = 'AZ_img_wide.csv'
outfolder = '../data/processed_data/01/Imaging/02/'

if not os.path.exists(outfolder):
    os.makedirs(outfolder)


df = pd.read_csv(infolder + infile)
cols = [x for x in df.columns if x != 'COMPOUND']
# filter all values to be outside range of +- 1 Zscore
df[cols] = df[cols][(df > 1) | (df < -1)]
df = df.fillna(value=0)
df = df.T[df.any()].T
df.to_csv(outfolder + infile, index=False)

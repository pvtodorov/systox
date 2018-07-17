import pandas as pd
import numpy as np
from pathlib import Path


# this log2 function cuts off values between [0.5, 2] FC
# it sets them to 1 before converting to log2
def log2_medthr(n):
    "threshold values then log2 transform"
    n2 = 1
    if (n >= 2) or (n <= 0.5):
        n2 = n
    if np.isfinite(np.log2(n2)) is False:
        print(n, n2)
    return np.log2(n2)


df_genes = pd.read_excel('../data/original_data/PCR/AZcompounds_HMOX1_SQSTM1_24h.xlsx')
id_vars = ['Replicate', 'Compound', 'concentration (µM)']
features = ['HMOX1 (fold to control)', 'SQSTM1 (fold to control)']
df_genes = df_genes.melt(id_vars=id_vars, value_vars=features)
df_genes = df_genes[np.isfinite(df_genes['value'])]
df = df_genes
df = df.groupby(['Compound', 'concentration (µM)', 'variable'])
df = df['value'].apply(np.median).to_frame().reset_index()
df = df.rename(columns={'value': 'median'})
log2t = lambda x: log2_medthr(x)
df['median'] = df['median'].map(log2t)
df = df.groupby(['Compound', 'variable'])
df = df[['median']].apply(np.max).reset_index()
df = df.rename(columns={'median': 'medianmax'})
pivoted = df.pivot_table(index=['Compound'],
                         columns='variable',
                         values='medianmax')
pivoted = pivoted.rename_axis(None, axis=1)
pivoted = pivoted.reset_index()
pivoted.rename(columns={'Compound': 'COMPOUND',
                        'HMOX1 (fold to control)': 'HMOX1_24h',
                        'SQSTM1 (fold to control)': 'SQSTM1_24h'},
               inplace=True)
pivoted['COMPOUND'] = ['AZ10119007',
                       'AZ10847725',
                       'AZ10886103',
                       'AZ12484631',
                       'AZ12585624',
                       'AZD7507',
                       'Antipyrine',
                       'Atorvastatin',
                       'Candesartan',
                       'Dizocilpine',
                       'Nadolol',
                       'Ramatroban',
                       'DMSO']
sorted_cmp = ['DMSO',
              'Antipyrine',
              'Atorvastatin',
              'Candesartan',
              'Dizocilpine',
              'Ketoprofen',
              'Nadolol',
              'Ramatroban',
              'AZ10119007',
              'AZ10847725',
              'AZ10886103',
              'AZ12484631',
              'AZ12585624',
              'AZD7507']
pivoted['COMPOUND'] = pivoted['COMPOUND'].astype('category',
                                                 categories=sorted_cmp,
                                                 ordered=True)
pivoted = pivoted.sort_values('COMPOUND')
outfile = 'AZ_genes_wide'
outfolder = '../data/processed_data/01/PCR/00/'
path = Path(outfolder)
path.mkdir(parents=True, exist_ok=True)
pivoted.to_csv(outfolder + outfile + '.csv', index=False)

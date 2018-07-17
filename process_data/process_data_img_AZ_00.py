import pandas as pd
import numpy as np

def magnitude_max(data):
    return max(max(data), min(data), key=abs)

df_img = pd.read_excel('../data/original_data/Imaging/AZ/AZcompounds_Imaging_0-24h.xlsx')
cols = df_img.columns.tolist()
meta_cols = cols[0:8]
data_cols = [x for x in cols if x not in meta_cols]
id_vars = meta_cols
features = data_cols
df_img = df_img.melt(id_vars=id_vars, value_vars=features)
df = df_img
df = df.groupby(['Time point (h)', 'pert_iname',
                 'concentration (µM)', 'variable'])
df = df['value'].apply(np.median).to_frame().reset_index()
df = df.rename(columns={'value': 'median'})
df = df.groupby(['Time point (h)', 'pert_iname', 'variable'])
df = df['median'].apply(magnitude_max).reset_index()
df = df.rename(columns={'median': 'medianmax'})
pivoted = df.pivot_table(index=['Time point (h)', 'pert_iname'],
                         columns='variable',
                         values='medianmax')
pivoted = pivoted.rename_axis(None, axis=1)
pivoted = pivoted.reset_index()
pivoted = pivoted.pivot_table(index='pert_iname', columns='Time point (h)')
pivoted = pivoted.reset_index()
col_vals = pivoted.columns.values
new_cols = []
for v in col_vals:
    a = v[0]
    b = v[1]
    if type(b) != str:
        b = str(b)
    if len(b) > 0:
        c = a + '_' + b
    else:
        c = a
    new_cols.append(c)
pivoted.columns = new_cols
pivoted['pert_iname'] = ['DMSO',
                         'AZ10886103',
                         'AZ10119007',
                         'AZ12585624',
                         'AZ12484631',
                         'AZD7507',
                         'AZ10847725',
                         'Antipyrine',
                         'Atorvastatin',
                         'Nadolol',
                         'Ketoprofen',
                         'Candesartan',
                         'Dizocilpine',
                         'Ramatroban']
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
pivoted['pert_iname'] = pivoted['pert_iname'].astype('category',
                                                     categories=sorted_cmp,
                                                     ordered=True)
pivoted = pivoted.sort_values('pert_iname')
pivoted = pivoted.rename(columns={'pert_iname': 'COMPOUND'})
outfile = 'AZ_img_wide'
outfolder = '../data/processed_data/01/Imaging/01/'
pivoted.to_csv(outfolder + outfile + '.csv', index=False)

import pandas as pd
import os

# use FC and csv to get mean, median, stdev, metas and merged csvs
# in this case, mean/std and median refer to statistics done on replicates

geneList = pd.read_csv('../data/lists/gene_list.csv')
genes = geneList['Gene'].tolist()

infolder = '../data/processed_data/01/LISS/00/'
outfolder = '../data/processed_data/01/LISS/01/'

if not os.path.exists(outfolder):
    os.makedirs(outfolder)

raw_data = pd.read_csv(infolder + 'FC.csv')

df0 = raw_data
meta_columns = ['ID', 'CMP', 'DOSE', 'TIME', 'SampleIDs']
newMetas = pd.DataFrame(columns=meta_columns)
columns = ['ID'] + genes
meanData = pd.DataFrame(columns=columns)
stdevData = pd.DataFrame(columns=columns)
medianData = pd.DataFrame(columns=columns)
ID = 0


compounds = df0['pert_mfc_desc'].unique().tolist()

for i in compounds:
    df1 = df0[df0['pert_mfc_desc'] == i]
    doses = df1['pert_dose'].unique().tolist()
    for j in doses:
        df2 = df1[df1['pert_dose'] == j]
        times = df2['pert_time'].unique().tolist()
        for k in times:
            df3 = df2[df2['pert_time'] == k]
            SampleIDs = df3['index'].tolist()
            dmso_pct = df3['x_dmso_pct'].unique().tolist()
            for m in dmso_pct:
                df3a = df3[df3['x_dmso_pct'] == m]
                cmp = i
                if i == 'DMSO':
                    cmp = 'DMSO_' + str(m) + 'pct'
                if i == 'UnTrt':
                    cmp = 'Medium'
                df3a = df3a[genes]
                # df.mean returns long Series. turn to df. transpose to wide
                df4 = df3a.mean(axis=0, skipna=True).to_frame().transpose()
                df4['ID'] = str(ID)
                meanData = meanData.append(df4)
                meanData = meanData[columns]
                # again, long series -> long frame -transpose-> wide
                df5 = df3a.std(axis=0, skipna=True).to_frame().transpose()
                df5['ID'] = [ID]
                stdevData = stdevData.append(df5)
                stdevData = stdevData[columns]
                df6 = pd.DataFrame(columns=['ID', 'CMP', 'DOSE',
                                            'TIME', 'SampleIDs'])
                df6['ID'] = [ID]
                df6['CMP'] = [cmp]
                df6['DOSE'] = [j]
                df6['TIME'] = [k]
                df6['SampleIDs'] = [SampleIDs]
                newMetas = newMetas.append(df6)
                df7 = df3a.median(axis=0, skipna=True).to_frame().transpose()
                df7['ID'] = [ID]
                medianData = medianData.append(df7)
                medianData = medianData[columns]
                ID = ID + 1


newMetas.to_csv(outfolder + 'gene_metadata.csv', index=False)
meanData.to_csv(outfolder + 'gene_mean_data.csv', index=False)
stdevData.to_csv(outfolder + 'gene_stdev_data.csv', index=False)
medianData.to_csv(outfolder + 'gene_median_data.csv', index=False)

merged_medianData = medianData.merge(newMetas, on='ID', how='outer')
merged_medianData = merged_medianData[meta_columns + genes]
merged_medianData.to_csv(outfolder + 'merged_medianData.csv', index=False)

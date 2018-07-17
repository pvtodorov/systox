import pandas as pd
import numpy as np
import os

infolder = '../data/original_data/Imaging/Zscores/01/'
outfolder = '../data/processed_data/01/Imaging/00/'
outfile = 'img_medianmax_AC_RENORM'

if not os.path.exists(outfolder):
    os.makedirs(outfolder)

df_compounds = pd.read_csv('../data/lists/allCmp_class_ID_list.csv')
img_cmp = df_compounds['imaging'].tolist()
gene_cmp = df_compounds['genes'].tolist()
classes = df_compounds['class'].tolist()
datasets = df_compounds['SET'].tolist()
compoundsCADict = {}
for a, b, c, d in zip(img_cmp, gene_cmp, classes, datasets):
    if (a != 'none') & (b != 'none') & (c in ['A', 'C']) & (d in [1, 2]):
        compoundsCADict[a] = c
compoundsCA = [k for k in compoundsCADict]
drop_compounds = ['DMSO']
compoundsCA = [x for x in compoundsCA if x not in drop_compounds]

img_long = pd.read_csv(infolder + 'new_renormalized_long.csv')
features = img_long['feature'].unique().tolist()
genes = features

times = [4, 24]
cols = ['COMPOUND'] + genes
for i in times:
    medianmax = pd.DataFrame(columns = cols)
    df0 = img_long[img_long['TIME'] == i]
    for j in compoundsCA:
        df1 = df0[df0['drug'] == j]          
        temp = pd.DataFrame(columns = cols)
        temp['COMPOUND'] = [j]
        for k in genes:
            df2 = df1[df1['feature'] == k]  
            val_list = df2['zscore'].tolist()
            tempmax = max(max(val_list), min(val_list), key=abs)
            temp[k] = [tempmax]
        medianmax = medianmax.append(temp)
    medianmax = medianmax.reset_index(drop = True)
    medianmax.to_csv(outfolder + outfile + '_' + str(i) + '.csv', index = False)

dfList = []
suffixes = []
for i in times:
    dfList.append(pd.read_csv(outfolder + outfile + '_' + str(i) + '.csv'))
    suffixes.append(('_' + str(i))) 
wide = dfList[0].merge(dfList[1], how = 'outer', on = 'COMPOUND', suffixes = suffixes)
wide.to_csv(outfolder + outfile + '_wide' + '.csv', index = False)
import pandas as pd
import os

# using dose-response files, take the max of for each compound at any dose
# generates medianmax files

infolder = '../data/processed_data/01/LISS/02/'
outfolder = '../data/processed_data/01/LISS/03/'
outfile = 'medianmax_AC'

if not os.path.exists(outfolder):
    os.makedirs(outfolder)

df_compounds = pd.read_csv('../data/lists/allCmp_class_ID_list.csv')
img_cmp = df_compounds['imaging'].tolist()
gene_cmp = df_compounds['genes'].tolist()
classes = df_compounds['class'].tolist()
compoundsCADict = {}
for a, b, c, in zip(img_cmp, gene_cmp, classes):
    if(a != 'none') & (b != 'none'):
        compoundsCADict[b] = c
compoundsCA = [k for k in compoundsCADict if compoundsCADict[k] in ['A', 'C']]
drop_compounds = ['DMSO']
compoundsCA = [x for x in compoundsCA if x not in drop_compounds]

times = ['6h', '24h']
geneList = pd.read_csv('../data/lists/gene_list.csv')
genes = geneList['Gene'].tolist()
cols = ['COMPOUND'] + genes

for i in times:
    medianmax = pd.DataFrame(columns=cols)
    for j in compoundsCA:
        filepath = infolder + j + '_' + i + '.csv'
        if os.path.exists(filepath):
            df0 = pd.read_csv(filepath)
            df0 = df0.set_index('GENE').transpose()
            temp = pd.DataFrame(columns=cols)
            temp['COMPOUND'] = [j]
            for k in genes:
                tempmax = max(df0[k].tolist())
                temp[k] = [tempmax]
            medianmax = medianmax.append(temp)
    medianmax = medianmax.reset_index(drop=True)
    medianmax.to_csv(outfolder + outfile + '_' + i + '.csv', index=False)

dfList = []
suffixes = []
for i in times:
    dfList.append(pd.read_csv(outfolder + outfile + '_' + i + '.csv'))
    suffixes.append(('_' + i))

wide = dfList[0].merge(dfList[1], how='outer',
                       on='COMPOUND', suffixes=suffixes)
wide.to_csv(outfolder + outfile + '_wide' + '.csv', index=False)

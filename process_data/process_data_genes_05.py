import pandas as pd
import os

# order all compounds by ID, then rename to common nomenclature
# this makes names the same in all datasets

infolder = '../data/processed_data/01/LISS/04/'
outfolder = '../data/processed_data/01/LISS/05/'
cmps = pd.read_csv('../data/lists/allCmp_class_ID_list.csv')

if not os.path.exists(outfolder):
    os.makedirs(outfolder)

files = os.listdir(infolder)
for i in files:
    df = pd.read_csv(infolder + i)
    label_col = 'genes'
    cmps = cmps[cmps[label_col] != 'none']
    labels = cmps[label_col]
    ids = cmps['ID'].tolist()
    cmp_label_id_dict = dict(zip(labels, ids))
    df['COMPOUND'] = [cmp_label_id_dict[x] for x in df['COMPOUND'].tolist()]
    df.sort_values(by='COMPOUND', axis='index', inplace=True)
    names = cmps['name'].tolist()
    cmp_id_name_dict = dict(zip(ids, names))
    df['COMPOUND'] = [cmp_id_name_dict[x] for x in df['COMPOUND'].tolist()]
    df.to_csv(outfolder + i, index=False)

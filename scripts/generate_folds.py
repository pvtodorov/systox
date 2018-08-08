import pandas as pd
import numpy as np
import os
from sklearn.model_selection import StratifiedKFold
import json

# order all compounds by ID, then rename to common nomenclature
# this makes names the same in all datasets


def load_classification(path):
    '''takes the classification dataframe.
    returns cmp dict with names and classes'''
    df0 = pd.read_csv(path)
    compounds = df0['name'].tolist()
    classes = df0['class'].tolist()
    cmpDict = dict(zip(compounds, classes))
    return cmpDict


def load_dataset(path, cmpDict, posClass):
    'takes a path and cmpDict. loads dataset. return rowdata, features, X, y'
    df0 = pd.read_csv(path)
    rowdata = df0['COMPOUND'].unique().tolist()
    features = df0.columns.tolist()
    features.remove('COMPOUND')
    X = df0.as_matrix(columns=features)
    y = []
    for i in rowdata:
        if cmpDict[i] == posClass[0]:
            y.append(1)
        if cmpDict[i] != posClass[0]:
            y.append(0)
    dataset = {'rowdata': rowdata,
               'features': features,
               'X': X,
               'y': np.asarray(y)}
    return dataset


infolder = 'data/processed_data/01/LISS/05/'
infile = 'log_medianmax_AC_wide.csv'
outfolder = 'data/processed_data/folds/'
cmp_path = 'data/lists/allCmp_class_ID_list.csv'


if not os.path.exists(outfolder):
    os.makedirs(outfolder)


cmpDict = load_classification(cmp_path)
dataset = load_dataset(infolder + infile, cmpDict, ['C'])
X = dataset['X']
y = dataset['y']

skf = StratifiedKFold(n_splits=9, shuffle=True)
all_folds = []
while len(all_folds)<100:
    skfolds = []
    for train, test in skf.split(X,y):
        skfolds.append([(train).tolist(), (test).tolist()])
    all_folds.append(skfolds)

for i, f in enumerate(all_folds):
    settings_dict = {}
    settings_dict['name'] = str(i)
    settings_dict['folds'] = f
    with open(outfolder + settings_dict['name'] + '.json', 'w') as fp:
        json.dump(settings_dict, fp, indent=None)

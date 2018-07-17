import pandas as pd
import numpy as np
from sklearn.utils import shuffle
from copy import deepcopy
from imblearn.over_sampling import SMOTE, ADASYN
import logging
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime


def print_to_log(s):
    """ Needed because dask workers do not touch the log. Will print to stdout
        as well as the log file. Stdout will appear in emails from the cluster.
    """
    logging.info(s)
    print(s)


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


def shuffle_dataset_features(dataset, seed):
    'Shuffle feature names and dataset features in a consistent way'
    print_to_log('shuffle feature names')
    d = deepcopy(dataset)
    features, X = shuffle(d['features'], np.transpose(d['X']),
                          random_state=seed)
    d['features'] = features
    d['X'] = np.transpose(X)
    return d


def scramble_dataset_labels(dataset, seed):
    'Scramble the classifications'
    print_to_log('scramble classifications')
    d = deepcopy(dataset)
    y = shuffle(d['y'], random_state=seed)
    d['y'] = y
    return d


def fit_RF(X, y, train_ids, rf_params, imbal=None):
    print_to_log('fit_RF')
    rf = RandomForestClassifier(**rf_params)
    X_t = X[train_ids]
    y_t = y[train_ids]
    rf.fit(X_t, y_t)
    return rf


def predict_RF(RF, X, test_ids):
    print_to_log('predict_RF')
    X_test = X[test_ids]
    predicted = RF.predict_proba(X_test)
    id_predictions = {a: b for a, b in zip(test_ids, predicted)}
    return id_predictions


def fit_and_predict(X, y_a, train_ids, test_ids, rf_params, imbal=None):
    print_to_log('fit_and_predict')
    rf = fit_RF(X, y_a, train_ids, rf_params, imbal)
    id_predictions = predict_RF(rf, X, test_ids)
    return id_predictions


def build_rank_list(ranked_features_df):
    '''rank_list
    [ {feature : rank}, ...,  ]
    each dict in list corresponds to a fold
    '''
    print_to_log('build_rank_list')
    m = ranked_features_df.as_matrix()
    rank_list = []
    for i in range(0, 9):
        rank_list.append({a: b for a, b in zip(m[:, 0], m[:, i + 1])})
    return rank_list


def filter_dataset_features(X, rank_list, cutoff, features):
    '''return deepcopy of X with features cutoff
    '''
    print_to_log('filter_dataset_features')
    filtered_Xs = []
    for d in rank_list:
        filtered_feats = [x for x in d if d[x] <= cutoff]
        for i_x, x in enumerate(filtered_feats):
            try:
                features.index(x)
            except:
                print(str(i_x), str(x))
                print('--------')
                print(filtered_feats)
        feat_idxs = [features.index(x) for x in filtered_feats]
        X_f = deepcopy(X)
        X_f = X[:, feat_idxs]
        filtered_Xs.append(X_f)
    return filtered_Xs


def filtered_oversampled(oversampled, i_f, rank_list, n_feats, features):
    print_to_log('filtered_oversampled')
    X_a = oversampled[i_f][0]
    y_a = oversampled[i_f][1]
    f_Xs = filter_dataset_features(X_a, rank_list, n_feats, features)
    return X_a, y_a, f_Xs


def apply_SMOTE(X, y, smote_dict):
    print_to_log('apply_SMOTE')
    sm = SMOTE(**smote_dict)
    X_resampled, y_resampled = sm.fit_sample(X, y)
    return X_resampled, y_resampled


def apply_ADASYN(X, y, adasyn_dict):
    print_to_log('apply_ADASYN')
    ada = ADASYN(**adasyn_dict)
    X_resampled, y_resampled = ada.fit_sample(X, y)
    return X_resampled, y_resampled


def gen_balancing_data(X, y, imbal):
    print_to_log('gen_balancing_data')
    if imbal:
        if imbal['algorithm'] == 'SMOTE':
            p = imbal['params']
            X_r, y_r = apply_SMOTE(X, y, p)
            print_to_log('generating SMOTE samples')
        elif imbal['algorithm'] == 'ADASYN':
            p = imbal['params']
            X_r, y_r = apply_ADASYN(X, y, p)
            print_to_log('generating ADASYN samples')
        else:
            print_to_log('Unknown imbal parameters, using as-is')
            return None
        X_new = X_r[(len(X)):]
        y_new = y_r[(len(y)):]
        return [X_new, y_new]
    else:
        print_to_log('No imbal corr specified, using as-is')
        return None


def gen_oversampled_data(X, y, folds, imbal):
    """
    Used with predict
    """
    print_to_log('gen_oversampled_data')
    oversampled = []
    for i_f, f in enumerate(folds):
        X_t = X[f[0]]
        y_t = y[f[0]]
        print_to_log('generating training data for fold ' + str(i_f))
        balancing_data = gen_balancing_data(X_t, y_t, imbal)
        if balancing_data:
            X_new = balancing_data[0]
            y_new = balancing_data[1]
            X_r = np.concatenate((X, X_new), 0)
            y_r = np.concatenate((y, y_new), 0)
            oversampled.append([X_r, y_r])
        else:
            oversampled.append([X, y])
    return oversampled


def get_current_time_str():
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    return current_time

import argparse
import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
from dask import delayed
from dask.distributed import Client
import os
from fit_and_select import *
import logging
from datetime import datetime


def fit_RFE(X, y, train_ids, rf_params, imbal=None):
    RF = RandomForestClassifier(**rf_params)
    rfe = RFE(estimator=RF, n_features_to_select=1, step=1)
    X_t = X[train_ids]
    y_t = y[train_ids]
    if imbal:
        if imbal['algorithm'] == 'SMOTE':
            p = imbal['params']
            X_t, y_t = apply_SMOTE(X_t, y_t, p)
            print_to_log('generating SMOTE samples')
        elif imbal['algorithm'] == 'ADASYN':
            p = imbal['params']
            X_t, y_t = apply_ADASYN(X_t, y_t, p)
            print_to_log('generating ADASYN samples')
        else:
            print_to_log('Unknown imbal parameters, using as-is')
    else:
        print_to_log('No imbal corr specified, using as-is')
    rfe.fit(X_t, y_t)
    return rfe


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("settings_path", help="settings and parameters json")
    parser.add_argument("fold_num", help="which fold json to feed in")
    args = parser.parse_args()
    settings_path = args.settings_path
    fold_num = args.fold_num

    with open(settings_path) as f:
        settings = json.load(f)
    output_dir = settings['run_path'] + settings['run_name'] + '/' \
        + fold_num + '/output/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    logname = output_dir + datetime.now().strftime("%Y%m%d_%H%M%S") + '.log'
    logging.basicConfig(filename=logname, level=logging.DEBUG)
    print_to_log('Started run.')
    with open(settings['fold_path'] + fold_num + '.json') as f:
        fold_file = json.load(f)
    folds = fold_file['folds']

    cmpDict = load_classification(settings['label_path'])
    dataset = load_dataset(settings['data_path'], cmpDict, ['C'])
    if settings.get('shuffle_dataset_features', False) is True:
        dataset = shuffle_dataset_features(dataset, int(fold_num))
    if settings.get('scramble_dataset_labels', False) is True:
        dataset = scramble_dataset_labels(dataset, int(fold_num))
    X = dataset['X']
    y = dataset['y']
    client = Client(n_workers=3, threads_per_worker=1)
    delayed_rfes = []
    for f in folds:
        print_to_log('------------------------------------')
        print_to_log(get_current_time_str() + '   '
                     'RFE selection running on fold : ' + str(f))
        train_ids = f[0]
        delayed_RFE = delayed(fit_RFE)(X, y, train_ids, settings['rf_params'],
                                       imbal=settings.get('imbal', None))
        delayed_rfes.append(delayed_RFE)
    rfes = []
    rfes = delayed(delayed_rfes).compute()

    feature_rankings = {}
    for index, r in enumerate(rfes):
        feature_rankings[index] = r.ranking_
    features = dataset['features']
    pd_ranked = pd.DataFrame(feature_rankings, index=features)
    pd_ranked.to_csv(output_dir + 'ranked_features.csv')

    client.cluster.close()
    client.shutdown()

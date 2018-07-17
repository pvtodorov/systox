import argparse
import json
import pandas as pd
from dask import delayed
from dask.distributed import Client
from collections import defaultdict
from fit_and_select import *
import logging


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
    logname = output_dir + get_current_time_str() + '.log'
    logging.basicConfig(filename=logname, level=logging.DEBUG)
    print_to_log('Started run.')

    with open(settings['fold_path'] + fold_num + '.json') as f:
        fold_file = json.load(f)
    folds = fold_file['folds']

    print_to_log(str(settings))
    print_to_log('------------------------------------')

    cmpDict = load_classification(settings['label_path'])
    print_to_log('------------------------------------')
    print_to_log(str(cmpDict))
    print_to_log('------------------------------------')
    dataset = load_dataset(settings['data_path'], cmpDict, ['C'])
    ranked_features_df = pd.read_csv(output_dir + 'ranked_features.csv')
    rank_list = build_rank_list(ranked_features_df)
    if settings.get('shuffle_dataset_features', False) is True:
        dataset = shuffle_dataset_features(dataset, int(fold_num))
    if settings.get('scramble_dataset_labels', False) is True:
        dataset = scramble_dataset_labels(dataset, int(fold_num))
    X = dataset['X']
    y = dataset['y']
    features = dataset['features']
    rowdata = dataset['rowdata']
    oversampled = gen_oversampled_data(X, y, folds,
                                       imbal=settings.get('imbal', None))
    client = Client(n_workers=3, threads_per_worker=1)
    print_to_log('dask workers created')
    predictions_dict = defaultdict(lambda: [])
    for n_feats in range(1, len(features) + 1):
        delayed_fps = []
        print_to_log('------------------------------------')
        print_to_log(get_current_time_str() + '   '
                     'Fitting forests for n_features: ' + str(n_feats))
        for i_f, f in enumerate(folds):
            X_a, y_a, f_Xs = filtered_oversampled(oversampled, i_f, rank_list,
                                                  n_feats, features)
            train_ids = f[0]
            test_ids = f[1]
            delayed_fp = fit_and_predict(f_Xs[i_f], y_a, train_ids, test_ids,
                                         settings['rf_params'], imbal=None)
            delayed_fps.append(delayed_fp)
        proba_list = []
        proba_list = delayed(delayed_fps).compute()
        for d in proba_list:
            for t_id, p in d.items():
                # t_id is the test_id (row of the compound) being classified
                # p is the prediction proba, here in an arr of [class0,class1]
                predictions_dict[rowdata[t_id]].append(p[1])

    predictions = pd.DataFrame(predictions_dict)
    predictions = predictions.transpose()
    predictions = predictions.reset_index()
    predictions = predictions.rename(columns={'index': 'COMPOUND'})
    predictions.to_csv(output_dir + 'predictions.csv', index=False)

    client.cluster.close()
    client.shutdown()
    print_to_log('dask shut down')

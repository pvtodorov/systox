import argparse
import json
import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.metrics import roc_auc_score, recall_score
from fit_and_select import *
from tqdm import tqdm
import os


def specificity_score(y_true, y_pred):
    tn = len([x for x in y_true if x == 0])
    fp = len([y_t for y_t, y_p in zip(y_true, y_pred)
              if ((y_t == 0) and (y_p == 1))])
    specificity = (tn / (tn + fp))
    return specificity


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("settings_path", help="settings and parameters json")
    args = parser.parse_args()
    settings_path = args.settings_path

    with open(settings_path) as f:
        settings = json.load(f)

    cmpDict = load_classification(settings['label_path'])
    dataset = load_dataset(settings['data_path'], cmpDict, ['C'])
    n_feats = len(dataset['features'])
    labels = {a: b for a, b in zip(dataset['rowdata'], dataset['y'])}

    auc_scores_dict = defaultdict(lambda: [])
    sens_scores_dict = defaultdict(lambda: [])
    spec_scores_dict = defaultdict(lambda: [])
    path = settings['run_path'] + settings['run_name'] + '/'
    runs = [x for x in os.listdir(path) if os.path.isdir(path + x)]
    runs = [x for x in runs if '.' not in x]
    num_runs = len(runs)
    for i in tqdm(range(0, num_runs)):
        df = pd.read_csv(path + str(i) + '/output/predictions.csv')
        compounds = df['COMPOUND'].tolist()
        y = [labels[x] for x in compounds]
        scores = []
        for j in range(0, n_feats):
            y_predicted = df[str(j)].tolist()
            auc_score = roc_auc_score(y, y_predicted)
            auc_scores_dict[j].append(auc_score)
            sens_score = recall_score(np.round(y), np.round(y_predicted))
            sens_scores_dict[j].append(sens_score)
            spec_score = specificity_score(np.round(y), np.round(y_predicted))
            spec_scores_dict[j].append(spec_score)
        auc_scores_dict['rep'].append(i)
        sens_scores_dict['rep'].append(i)
        spec_scores_dict['rep'].append(i)

    auc_df = pd.DataFrame(auc_scores_dict)
    cols = ['rep'] + list(range(0, n_feats))
    auc_df = auc_df[cols]
    auc_df.to_csv(path + 'auc_score.csv', index=False)

    sens_df = pd.DataFrame(sens_scores_dict)
    cols = ['rep'] + list(range(0, n_feats))
    sens_df = sens_df[cols]
    sens_df.to_csv(path + 'sens_score.csv', index=False)

    spec_df = pd.DataFrame(spec_scores_dict)
    cols = ['rep'] + list(range(0, n_feats))
    spec_df = spec_df[cols]
    spec_df.to_csv(path + 'spec_score.csv', index=False)

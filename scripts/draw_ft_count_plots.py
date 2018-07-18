import os
import json
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def split_features_time(features):
    time_dict = {'4' : 'early',
                 '6h': 'early',
                 '24': 'late',
                 '24h': 'late'}
    space_dict = {'early': ' ', 'late': ''}
    split_times = [time_dict[x.split('_')[-1]] for x in features]
    split_features = ['_'.join(x.split('_')[:-1]) for x in features]
    split_features = [(space_dict[t] + f) for f, t 
                      in zip(split_features, split_times)]
    return split_features, split_times


def get_rankings_df(path):
    df_r = pd.read_csv(path)
    df_r = df_r.astype(float)
    df_r = pd.melt(df_r)
    df_r.loc[:, 'value'] += 1
    return df_r


def get_ranking_counts(df_r, vc):
    df_rc = df_r[df_r['value'] <= vc]
    df_rc = pd.DataFrame(df_rc['variable'].value_counts())
    df_rc = df_rc.reset_index()
    df_rc = df_rc.rename(columns={'variable': 'count', 'index': 'variable'})
    features = df_rc['variable'].tolist()
    split_features, split_times = split_features_time(features)
    df_rc['variable'] = split_features
    df_rc['time'] = split_timesfeatures = df_rc['variable'].tolist()
    split_features, split_times = split_features_time(features)
    df_rc['variable'] = split_features
    df_rc['time'] = split_times
    return df_rc


def dump_lists_of_features(df_rc, vc, output_dir):
    features_dict = {}
    for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 100, 1000]:
        features_dict[i] = df_rc['variable'].unique().tolist()[:i]
    json_path = output_dir + 'rc_vc_' + str(vc) + '.json'
    with open(json_path, 'w') as outfile:
        json.dump(features_dict, outfile, indent=0)  


def plot_rankings(df_rc, vc, output_dir):
    cols_filter = df_rc['variable'].unique().tolist()[:50]
    f, ax = plt.subplots(figsize=(4, 12))
    plt.xticks(rotation=0)
    ax = sns.barplot(x='count', y='variable', hue='time',
                     data=df_rc[df_rc['variable'].isin(cols_filter)],
                     hue_order=['early', 'late'],
                     palette=['#67a9cf', '#ef8a62'],
                     dodge=False)
    # ax.add_legend(label_order = ['early', 'late'])
    save_path = output_dir + 'rc_vc_' + str(vc)
    f.savefig(save_path + '.png', bbox_inches="tight")
    f.savefig(save_path + '.pdf', format='pdf', bbox_inches="tight")
    plt.close('all')


databuilds = ['01']
dataset_types = ['imaging', 'genes']
vc = 20  # variable cutoff

for databuild in databuilds:
    databuild_dir = 'feature_selection/' + databuild + '/'
    dataset_types = get_immediate_subdirectories(databuild_dir)
    for dataset_type in dataset_types:
        base_folder = databuild_dir + dataset_type + '/'
        runs = get_immediate_subdirectories(base_folder)
        runs = sorted([x for x in runs if '_n' not in x])
        #run_names = list(set([x.split('_')[0] for x in runs]))
        run_names = runs
        for n in run_names:
            path = base_folder + n + '/all_rankings.csv'
            df_r = get_rankings_df(path)
            df_rc = get_ranking_counts(df_r, vc)
            output_dir = 'models/' + databuild + '/' + dataset_type + '/' + n + '/'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            dump_lists_of_features(df_rc, vc, output_dir)
            output_dir = 'plots/' + databuild + '/' + dataset_type + '/' + n + '/'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            plot_rankings(df_rc, vc, output_dir)

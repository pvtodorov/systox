import os
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import seaborn as sns


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def draw_boxplots(df, feature_cutoff, name, output_dir):
    df_f = df[df['variable'] <= feature_cutoff]
    f, ax = plt.subplots(figsize=(20, 10))
    plt.ylim(0, 1)
    sns.boxplot(x='variable',
                y='value',
                data=df_f,
                ax=ax,
                palette=['#7fbf7b', '#af8dc3'],
                hue='run',
                whis=0.95,
                notch=True,
                fliersize=0)
    save_path = output_dir + 'b_' + str(feature_cutoff) + '_' + n
    f.savefig(save_path + '.png')
    f.savefig(save_path + '.pdf', format='pdf', bbox_inches="tight")
    plt.close('all')


def draw_band(df, feature_cutoff, name, output_dir):
    df_f = df[df['variable'] <= feature_cutoff]
    f, ax = plt.subplots(figsize=(20, 10))
    plt.ylim(0,1)
    ax = sns.tsplot(time="variable",
                    value="value",
                    unit="rep",
                    condition="run",
                    data=df_f,
                    ci=[95, 99],
                    color=sns.color_palette(['#7fbf7b', '#af8dc3']))
    save_path = output_dir + 'band_' + str(feature_cutoff) + '_' + n
    f.savefig(save_path + '.png')
    f.savefig(save_path + '.pdf', format='pdf', bbox_inches="tight")
    plt.close('all')


def draw_points(df, feature_cutoff, name, output_dir):
    df_f = df[df['variable'] <= feature_cutoff]
    f, ax = plt.subplots(figsize=(20, 10))
    plt.ylim(0,1)
    f, ax = plt.subplots(figsize=(0.2 * 100, 5))
    plt.ylim(-0.1, 1.1)
    plt.xticks(rotation=90)
    ax = sns.stripplot(x="variable", y="value", data=df_f,
                       jitter=True, hue='run',
                       palette=['#7fbf7b', '#af8dc3'], alpha=0.05)
    save_path = output_dir + 'points_' + str(feature_cutoff) + '_' + n
    f.savefig(save_path + '.png')
    f.savefig(save_path + '.pdf', format='pdf', bbox_inches="tight")
    plt.close('all')


databuilds = ['01']

for databuild in databuilds:
    databuild_dir = 'feature_selection/' + databuild + '/'
    dataset_types = get_immediate_subdirectories(databuild_dir)
    for dataset_type in dataset_types:
        base_folder = databuild_dir + dataset_type + '/'
        runs = get_immediate_subdirectories(base_folder)
        runs = sorted([x for x in runs if '_n' not in x])
        run_names = list(set([x.split('_')[0] for x in runs]))
        for n in tqdm(run_names):
            rn = [x for x in runs if n in x]
            run_subnames = [x.split('_')[-1] for x in rn]
            auc_dfs = []
            for s in run_subnames:
                if s != n:
                    full_name = n + '_' + s
                else:
                    full_name = n
                path = base_folder + full_name + '/auc_score.csv'
                df = pd.read_csv(path)
                df = df.astype(float)
                if 'scrambled' in s:
                    df['run'] = 'scrambled'
                else:
                    df['run'] = s
                auc_dfs.append(df)
            df = pd.DataFrame()
            for d in auc_dfs:
                df = df.append(d)
            cols = df.columns.tolist()
            cols.remove('rep')
            cols.remove('run')
            cols_rename = {c: int(c) for c in cols}
            df = df.rename(columns=cols_rename)
            df = pd.melt(df, id_vars=['rep', 'run'])
            df.loc[:,'variable'] += 1
            df = df.astype({'variable': int, 'rep': int, 'value': float})
            output_dir = 'plots/' + databuild + '/' +  dataset_type + '/' + n + '/'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            draw_boxplots(df, 50, output_dir + n, output_dir)
            draw_boxplots(df, df['variable'].max(), output_dir + n, output_dir)
            # draw_band(df, 50, output_dir + n, output_dir)
            # draw_band(df, df['variable'].max(), n, output_dir)
            # draw_points(df, 50, n, output_dir)
            # draw_points(df, df['variable'].max(), n, output_dir)

import pandas as pd
import argparse
import json
from tqdm import tqdm
import os

parser = argparse.ArgumentParser()
parser.add_argument("settings_path", help="settings and parameters json")
args = parser.parse_args()
settings_path = args.settings_path
with open(settings_path) as f:
    settings = json.load(f)
path = settings['run_path'] + settings['run_name'] + '/'

df = pd.DataFrame()
runs = [x for x in os.listdir(path) if os.path.isdir(path + x)]
runs = [x for x in runs if '.' not in x]
num_runs = len(runs)
for i in tqdm(range(0, num_runs)):
    df_r = pd.read_csv(path + str(i) + '/output/ranked_features.csv')
    df_r = df_r.set_index('Unnamed: 0')
    df_r = df_r.transpose()
    if len(df) == 0:
        df = df_r
    else:
        df = df.append(df_r)
df.to_csv(path + 'all_rankings.csv', index=False)

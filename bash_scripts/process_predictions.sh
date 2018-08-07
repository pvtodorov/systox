#!/bin/sh
declare -a settings_arr=("run_settings/01_genes_NORMAL_settings.json"
                         "run_settings/01_genes_NORMAL_scrambled_settings.json"
                         "run_settings/01_imaging_NORMAL_settings.json"
                         "run_settings/01_imaging_NORMAL_scrambled_settings.json")
for settings in "${settings_arr[@]}"
do
echo "Score and aggregate predictions $settings"
python scripts/performance_score.py $settings
echo "Aggregating feature rankings $settings"
python scripts/aggregate_rankings.py $settings
done

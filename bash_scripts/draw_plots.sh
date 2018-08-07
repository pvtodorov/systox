#!/bin/sh
declare -a settings_arr=("run_settings/01_genes_NORMAL_settings.json"
                         "run_settings/01_genes_NORMAL_scrambled_settings.json"
                         "run_settings/01_imaging_NORMAL_settings.json"
                         "run_settings/01_imaging_NORMAL_scrambled_settings.json")
for settings in "${settings_arr[@]}"
do
echo "Plotting feature counts for: $settings"
python scripts/draw_ft_count_plots.py $settings
echo "Plotting run performance for: $settings"
python scripts/draw_ft_select_performance_plots.py $settings
done

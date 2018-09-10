#!/bin/bash
declare -a run_arr=("run_settings/01_genes_NORMAL_settings.json"
                    "run_settings/01_genes_NORMAL_scrambled_settings.json"
                    "run_settings/01_imaging_NORMAL_settings.json"
                    "run_settings/01_imaging_NORMAL_scrambled_settings.json")
## now loop through the above arrays
for run in "${run_arr[@]}"
do
sbatch <<EOT
#!/bin/bash
#SBATCH -c 4
#SBATCH -N 1
#SBATCH -t 6:00:00
#SBATCH -p short
#SBATCH --mem=32000
#SBATCH -o logs/hostname_%j.out
#SBATCH -e logs/hostname_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=petar_todorov@hms.harvard.edu
#SBATCH --array=0-99
export OMP_NUM_THREADS=4
start=$SECONDS
echo $run
echo
cat $run
echo
uptime
echo
python scripts/feature_select.py $run \$SLURM_ARRAY_TASK_ID
python scripts/predict.py $run \$SLURM_ARRAY_TASK_ID
echo
uptime
echo
end=$SECONDS
duration=$(( end - start ))
echo "stuff took $duration seconds to complete"
EOT
done

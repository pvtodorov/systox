# SysTox feature selection

## About
This repo contains the code and instructions for regenerating the feature
selection and AUC performance plots in the manuscript "A Systems Toxicology
Approach for Mechanistic De-Risking and Prediction of Kidney Toxicity In Vitro".

All necessary data is housed within this repository.

By following the instructions listed here a user can run through the whole
process or parts of it.



## Requirements
* A *NIX based system for running bash scripts
* Python 3.6+ [(link)](https://www.python.org/downloads/)

Optional:
* High performance comuting environment for running all of the analyses



## Description of Directories
The main directory contains five subdirectories:

* `bash_scripts` are used by the user to run the entire analysis.
* `scripts` are called by each particular bash script to process data, perform
  computations, draw plots, etc.
* `process_data` contains scripts specifically used in the intial data
  processing steps required for training models.
* `data` contains several subdirectories as follows
    ```
    data/
    ├── lists
    │   ├── allCmp_class_ID_list.csv
    │   └── gene_list.csv
    ├── original_data
    │   ├── CellNumber
    │   ├── CellTiterGlo
    │   ├── Imaging
    │   ├── LISS
    │   └── PCR
    └── processed_data
        └── folds
    ```
    * `lists` contains lookups for compound classes (kidney toxic vs not) and a
      gene list used by the microarray
    * `original_data` contains the origianl data files, separated by type in
      different directories
    * `processed_data` contains `folds` which are the cross validation splits
      used in the 100 runs of the computational pipeline
* `feature_selection` contains the outputs of the feature selection pipeline,
  its predictions, and aggregated scores
    ```
    feature_selection/
    └── 01
        ├── genes
        │   ├── NORMAL
        │   │   ├── 0
        │   │   ├── 1
        │   │   ├── 2
        │   │   ├── ...
        │   └── NORMAL_scrambled
        └── imaging
            ├── NORMAL
            └── NORMAL_scrambled
    ```
    * the folders within feature selection are split into `genes` and `imaging`
    * both of these have 100 runs performed with either true or scrambled
      classes, named `NORMAL` or `NORMAL_scrambled`, respectively.



## 1. Set up a virtual environment
This will help keep your system python packages separate from the ones used to
run this code.

```
pip install virtualenv
virtualenv systox_env --no-site-packages
```

Activate the virtual environment
```
source systox_env/bin/activate
```

Install the required Python packages to run the code.
These are listed in the repo's`requirements.txt` file.
```
pip install -r systox/requirements.txt
```

If at any point you'd like to go back to your system's default python
environment, type `deactivate` in your terminal.



## 2. Make the bash scripts executable
We use a number of bash scripts to automate fetching data from synapse,
processing data, and completing a number of tasks. These are located in the
`bash_scripts` directory. After cloning it's likely that they need to be made
executable to run.
```
chmod 700 bash_scripts/*
```



## 3. Process the data into a vector for analysis
The original data must be processed in order to produce 2d vectors for both
genes and imaging that can be fed into the Random Forest for feature selection.
This can be done by
```
./bash_scripts/make_vectors.sh
```



## 4. Feature selection
Feature selection was run over 100 randomized sets of folds in which data was
split randomly into train and test segments in a way that the entire dataset
is covered.

The folds we used for cross validation are already present in this repo.

You can get a new set of folds by running the `generate_folds.sh` script. Note
that generating new folds may slightly change the outcome of the analysis as the
original set of folds was generated without a specific seed and this is why we
supply them directly.
```
./bash_scripts/generate_folds.sh
```



### 5. Recursive Feature Elimination & Predictions
We launched recursive feature elimination and prediction jobs for each of these
100 sets of folds on the Harvard Medical School Orchestra cluster. If you would
like to run this on your own cluster, follow the section below to adapt it to
your own scheduler (we used SLURM) and system. To use our precomputed results,
skip this section and proceed with the files provided.

#### settings files
```
run_settings/01_genes_NORMAL_settings.json
run_settings/01_genes_NORMAL_scrambled_settings.json
run_settings/01_imaging_NORMAL_settings.json
run_settings/01_imaging_NORMAL_scrambled_settings.json
```

#### Running the analysis
##### feature selection Python script
```
python scripts/feature_select.py <settings file> <fold number>
```

##### predictions Python script
```
python scripts/predict.py <settings file> <fold number>
```

* The fold numbers must be an array from 0-99

* An example SLURM scheduler script is provided in
  `bash_scripts/submit_many_backgrounds_predict.sh`.



### 6. Processing the predictions
Once feature rankings and predictions are present for each settings
configuration, they are processed further before plotting. Predictions are
scored, reportin the area under the receiver operating characteristic (AUC-ROC)
curve and stored in a single file. Feature rankings are aggregated in another
file.

To execute this
```
./bash_scripts/process_predictions.sh
```



### 7. Creating the plots in Figure 3
The plots from figure 3 can be created by executing the following
```
./bash_scripts/draw_plots.sh
```

This will generate a `plots/` directory. The directory will have the same folder
structure as the `feature_selection/` directory. In each run's subdirectory
where the plots contained in figure 3 as `.png` and `.pdf` files.

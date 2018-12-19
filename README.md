# SysTox feature selection

## About
This repo contains the code and instructions for regenerating the feature selection and AUC performance plots in the manuscript *"A Systems Toxicology Approach for Mechanistic De-Risking and Prediction of Kidney Toxicity In Vitro"*.

This repository does not contain any of the data, which is instead housed on Synapse at `syn11697964`.

By following the instructions listed here a user can run through the whole process or parts of it.

## Requirements

* A *NIX based system for running bash scripts
* git [(link)](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* Python 3.6+ [(link)](https://www.python.org/downloads/)
* A Synapse account [(link)](http://docs.synapse.org/articles/getting_started.html)

Optional:
* High performance comuting environment (optional)

## Create a directory
Make a directory to hold this repo and other things we'll need

```
mkdir systox
```

Enter the directory
```
cd systox
```

## Clone this repo

Go to your working directory of choice and execute the following commands to clone the code from github.

```
git clone https://github.com/pvtodorov/systox.git
```

## Set up a virtual environment
This will help keep your system python packages separate from the ones used to run this code.

```
pip install virtualenv
virtualenv systox_env --no-site-packages
```

Activate the virtual environment
```
source systox_env/bin/activate
```
Install the required packages to run the code. These are listed in the repo's `requirements.txt` file.
```
pip install -r systox/requirements.txt
```

If at any point you'd like to go back to your system's default python environment, type `deactivate` in your terminal.


## Set up Synapse
Go to Synapse and make an account. If you already have an account and have already logged into the command line client, you can skip this step.

Use the following command to login and store your credentials for Synapse.
```
synapse login -u USER -p PASS --rememberMe
```
You are now logged in and can pull data from the Synapse project [syn11697964](https://www.synapse.org/#!Synapse:syn11697964). This is all automated via bash scripts and should require no additional configuration or direct intreaction with Synapse.


## Make the bash scripts executable
We use a number of bash scripts to automate fetching data from synapse, processing data, and completing a number of tasks. These are located in the `bash_scripts` directory. After cloning it's likely that they need to be made executable to run.
```
chmod 700 bash_scripts/*
```


## Get the original data
The original data execute the following script
```
./bash_scripts/get_original_data.sh
```

## Process the data into a vector for analysis
The original data must be processed in order to produce 2d vectors for both genes and imaging that can be fed into the Random Forest for feature selection. This can be done by
```
./bash_scripts/make_vectors.sh
```

## Feature selection
Feature selection was run over 100 randomized sets of folds in which data was split randomly into train and test segments in a way that the entire dataset is covered.

You can retreive the same folds we used from synapse
```
./bash_scripts/get_folds.sh
```

You can get a new set of folds by running. Note that generating new folds may change the outcome of the analysis as the original set of folds was generated used without a specific seeding.
```
./bash_scripts/generate_folds.sh
```

### Recursive Feature Elimination & Predictions

We launched recursive feature elimination and prediction jobs for each of these 100 sets of folds on the Harvard Medical School Orchestra cluster. If you would like to run this on your own cluster, expand the section below. Otherwise you may follow the instructions to fetch our files from synapse.

#### get the settings files
Fetch the files from synapse by:
```
./bash_scripts/get_settings.sh
```
###### list of settings files
```
run_settings/01_genes_NORMAL_settings.json
run_settings/01_genes_NORMAL_scrambled_settings.json
run_settings/01_imaging_NORMAL_settings.json
run_settings/01_imaging_NORMAL_scrambled_settings.json
```

#### Getting the results from Synapse
To fetch pre-computed results from Synapse 
```
./bash_scripts/get_feature_selection.sh
```

#### Running the analysis
<details>
<summary>
click to expand
</summary>


##### feature selection Python script
```
python scripts/feature_select.py <settings file> <fold number>
```
##### predictions Python script
```
python scripts/predict.py <settings file> <fold number>
```

* The fold numbers must be an array from 0-99

* An example SLURM scheduler script is provided in `bash_scripts/submit_many_backgrounds_predict.sh`.
</details>

### Processing the predictions

Once feature rankings and predictions are present for each settings configuration, they are processed further before plotting. Predictions are scored, reportin the area under the receiver operating characteristic (AUC-ROC) curve and stored in a single file. Feature rankings are aggregated in another file.

To execute this
```
./bash_scripts/process_predictions.sh
```


### Creating the plots in Figure 3
The plots from figure 3 can be created by executing the following
```
./bash_scripts/draw_plots.sh
```
This will generate a `plots/` directory. The directory will have the same folder structure as the `feature_selection/` directory. In each run's subdirectory where the plots contained in figure 3 as `.png` and `.pdf` files.

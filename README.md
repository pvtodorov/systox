# SysTox feature selection

## About
This repo contains the code and instructions for regenerating the feature selection and AUC performance plots in the manuscript *"A Systems Toxicology Approach for Mechanistic De-Risking and Prediction of Kidney Toxicity In Vitro"*.

This repository does not contain any of the data, which is instead housed on Synapse at `synid`.

By following the instructions listed here a user can run through the whole process or parts of it.

## Requirements

* A *NIX based system for running bash scripts
* git [(link)](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* Python 3.4+ [(link)](https://www.python.org/downloads/)
* A Synapse account
* 

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
synapse login -u USER - p PASS --rememberMe
```
You are now logged in and can pull data from the Synapse project [syn11697964](https://www.synapse.org/#!Synapse:syn11697964). This is all automated via bash scripts and should require no additional configuration or direct intreaction with Synapse.

## Get the original data
The original data execute the following script
```
./get_original_data.sh
```

## Process the data into a vector for analysis
The original data must be processed in order to produce a 2d vector that can be fed into the Random Forest for feature selection. This can be done by
```
./make_vector.sh
```

## Feature selection
Feature selection was run over 100 randomized sets of folds in which data was split randomly into train and test segments in a way that the entire dataset is covered.

You can retreive the same folds we used from synapse
```
PLACE FETCH FOLD SCRIPT HERE
```

You can get a new set of folds by running. Note that this may change the outcome of the analysis.
```
PLACE FOLD SCRIPT HERE
```

### Recursive Feature Elimination & Predictions

We launched recursive feature elimination and prediction jobs for each of these 100 sets of folds on the Harvard Medical School Orchestra cluster. If you would like to run this on your own cluster, expand the section below. Otherwise you may follow the instructions to fetch our files from synapse.

#### Getting the results from Synapse
To fetch pre-computed results from Synapse 
```
./get_feature_selection.sh
```

#### Running the analysis
<details>
<summary>
click to expand
</summary>

##### get the settings files
```
./get_settings.sh
```
###### list of settings files
```
feature_selection/01/genes/NORMAL/settings.json
feature_selection/01/genes/NORMAL_scrambled/settings.json
feature_selection/01/imaging/NORMAL/settings.json
feature_selection/01/imaging/NORMAL_scrambled/settings.json
```  
##### feature selection Python script
```
python scripts/feature_select.py <settings file> <fold number>
```
##### predictions Python script
```
python scripts/predict.py <settings file> <fold number>
```

* The fold numbers must be an array from 0-99
</details>

### Creating the plots in Figure 3
Expand on this
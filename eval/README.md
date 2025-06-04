## Introduction

This eval/ subdirectory contains tools designed to **evaluate the performance of the Jira Agent**. Jira Agent has two evaluation metrics
1. Trajectory Evaluation
2. Correctness

### How It Works
#TODO


## Prerequisites for the eval tool

1. Install [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation) and install Python 3.12.9
   ```bash
   brew update && brew install pyenv &&
   pyenv install 3.12.9

2. Create venv and activate
   ```bash
   ~/.pyenv/versions/3.12.9/bin/python3 -m venv .evalvenv &&
   source .evalvenv/bin/activate
   ```
3. Install dependencies of eval using eval_requirements.txt:(TODO)
   
   ```sh
   cd eval
   ```
   ```sh
   pip install -r requirements.txt
   ```

## Steps to Run the Trajectory Evaluation

### 1. Data Generation/Collection

   - The set of input prompts to run needs to be created manually with the following values
     - Example input prompt:
       ```{
       "action":
       "query":
       }

   - Otherwise, generate or collect the required data by running:
     ```sh
     python generateReferenceTrajectory.py --config_file configs/generate_trajectory_config.yaml
     ```
   - This will create the necessary dataset and metadata files in the appropriate directory.

### 2. Trajectory Evaluation
   - Replay the generated or collected data to prepare it for evaluation. (Note: the repository used for replay must have the pr-review app installed as described in [TUTORIAL: Setup Installation](../TUTORIAL.md)):
     ```sh
     python runstrictMatch.py --config_file ../configs/strict_match_config.yaml
     ```

## Steps to Run the Correctness #TODO: SreeGowri
### 1. Data Generation/Collection
### 2. Evaluation

## Additional Notes

## Troubleshooting

- If you encounter issues, ensure all dependencies are installed and the environment variables are correctly set.


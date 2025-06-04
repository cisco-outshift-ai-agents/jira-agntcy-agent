## Introduction:

This eval/ subdirectory contains tools designed to **evaluate the performance of the Jira Agent**. Jira Agent has two evaluation techniques:

1. Trajectory Evaluation
2. Correctness Evaluation

## Prerequisites for the eval tool:

To use the these evaluation scripts:

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
   pip install -r eval_requirements.txt
   ```

## Steps to Run the Trajectory Evaluation
Please refer to this documentation to learn more about [Trajectory Evaluation](trajectory_evaluation_README.md)

## Steps to Run the Correctness Evaluation:

 Please refer to this documentation to learn more about [Correctness Evaluation](../readme_jira_correctness_evaluation.md)

## Additional Notes

## Troubleshooting

- If you encounter issues, ensure all dependencies are installed and the environment variables are correctly set.


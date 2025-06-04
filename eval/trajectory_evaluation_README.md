## Trajectory Evaluation:
Trajectory evaluation tries to evaluate the flow of agent calls in JiraAgent. It involves generating possible trajectories and check the similarity with trajectories extracted from Langraph using AgentEval tools

## Prerequisites:
1. Please follow the prerequisites in the eval folder's [readme.md](EVAL_README.md).

## Steps to run Trajectory Evaluation:
1. Generate list of project and issue prompts similar to the sample prompts described here [Dataset](strict_match/Dataset)
2. Run Reference Trajectory script to generate possible reference trajectories for input , by default it will generate one trajectory, the output file will be similar to file [reference_trajectory.yaml](strict_match/Dataset/trajectory_input/generateReferenceTrajectoryResponse.yaml)
3. The output file from previous script as input, run the  runStrictMatch.py to generate trajectory evaluation report which will be similar to the reports here [Sample Reports](strict_match/Dataset/output/)

## The code for Trajectory evaluation can be found in eval/strict_match folder.

```sh the 
   cd eval/strict_match
   ```
### 1. Data Generation/Collection
   - The list of project / Issue related prompts need to be generated/uploaded with format as described in [Issue Mock Prompts](strict_match/Dataset/input/mock_issue_prompts.json) or [Project Mock Prompts](strict_match/Dataset/input/mock_project_prompts.json)

### 2. Generate Reference Trajectory
   - Configure the config file [generate_trajectory_config](strict_match/configs/generate_trajectory_config.yaml)
```sh
   python generateReferenceTrajectory.py --config_file configs/generate_trajectory_config.yaml
```

### 3. Trajectory Evaluation
   - Configure the config file [strict_match_config](strict_match/configs/strict_match_config.yaml)
     ```sh
     python runstrictMatch.py --config_file configs/strict_match_config.yaml
     ```
     

## Additional Notes:
If the queries are infeasible by JiraAgent, the evaluation metric might be low score, try to fix the input query
## Results:

Below are the evaluation results that we got while running issue prompts and project prompts using internal dataset

| Prompt Type     | Count | Accuracy |
|-----------------|-------|----------|
| Issue Prompts   | 19    | 95.34%   |
| Project Prompts | 18    | 100.00%  |

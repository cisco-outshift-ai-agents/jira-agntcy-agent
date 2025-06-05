## Jira Correctness Evaluation:

We try to evaluate the Jira Agent for correctness across it actions project_query, project_creation, project_update, project_assign, project_transition (issue_transition), issue_query, issue_update, issue_assign, issue_creation.

The below steps showcases our end to end pipeline to evaluate jira agent queries that are sent in natural language.

## Prerequisites:

1. Please follow the prerequisites in the eval folder's [readme.md](README.md).
2. We have currently not added our original evaluation dataset built, due to internal privacy data.
3. We have added a sample mock input of queries in the input folder. Please create similar supported queries to create your own dataset.

## Steps to run Correctness Evaluation:

1. The Jira correctness evaluation has three scripts for running the end to end evaluation. 
2. These three scripts are key_generation.py, jira_action_replay.py and correctness_eval.py and they run in the order mentioned.
3. key_generation.py takes in a file of user queries for jira agent as showcased in the mock input of queries which then returns an output file.
4. This output file (FINAL_OUTPUT_QUERIES_FILE) is the input to the next script jira_action_replay.py which then processes these queries based on actions and gives an output (JIRA_ACTION_REPLAY_OUTPUT) which consists of the output of the jira agent along with the ground truth.
5. The output of jira_action_replay.py JIRA_ACTION_REPLAY_OUTPUT is then sent to correctness_eval.py which generates a RATING_FILE_NAME and a REPORT_FILE_NAME.
6. You can configure various LLMs to be used as part of correctness_eval.py where each will generate seperate reports as per LLM configured.

###### The code for Jira correctness evaluation can be found in eval/jira_correctness_evaluation folder.

The below steps showcase the commands to be used to run the following:

```sh
   cd jira_correctness_evaluation
   ```
We are assuming the above because we are already present in the eval folder.


#### Dataset Generation:

```sh
   python code/key_generation.py --config_file configs/key_generation_config.yml
```

#### Jira Action Replay:

```sh
   python code/jira_action_replay.py --config_file configs/jira_action_replay_config.yml
```

While running the Jira Action Replay, please ensure to keep the jira agent server running in one terminal to send the query to the jira agent and get response.

#### LLM as Judge Evaluation:

For running with GPT-4o:

```sh
   python code/correctness_eval.py --config_file configs/correctness_eval_config.yml
```

For running with o1 model:

```sh
   python code/correctness_eval.py --config_file configs/correctness_eval_config_o1.yml
```

## Additional Notes:

Since, we are using LLMs to process most of the queries in key_generation.py, jira_action_replay.py and correctness_eval.py, we can't gaurantee the accuracy and consistency among runs for the same set of queries.

Also, if there are queries that are not supported or are infeasible, the jira_action_replay.py may fail and the queries need to be corrected to run it end to end successfully to give an output. If there are any network issues with the Jira server, Jira Agent, LLM service or any other infrastructure issue, it may fail to run end to end successfully. Please try to rerun to get a complete successful run.

## Results:

Below are the evaluation results that we got while running using GPT-4o and o1 LLM model.

#### GPT-4o LLM [File](jira_correctness_evaluation_reports/report_file_gpt-4o.md):

| Total_Queries: | max_value: | Average Rating: | Percentage: |
| --- | --- | --- | --- |
| 33 | 5 | 3.727272727272727 | 74.54545454545453 |

#### o1 LLM [File](jira_correctness_evaluation_reports/report_file_o1.md):

| Total_Queries: | max_value: | Average Rating: | Percentage: |
| --- | --- | --- | --- |
| 33 | 5 | 4.424242424242424 | 88.48484848484847 |


We are getting a correctness evaluation accuracy around 75% - 85%
# Copyright 2025 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

from agentevals.graph_trajectory.utils import (
    extract_langgraph_trajectory_from_thread,
)
from agentevals.graph_trajectory.strict import graph_trajectory_strict_match_async
from dotenv import load_dotenv
import os
import pprint
import pytest
import asyncio
import uuid
from tabulate import tabulate
from datetime import datetime
import yaml
import argparse
import logging
from jira_agent.graph.graph import JiraGraph

# Initialize logger
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
import fire

# load environment variables from .env file
load_dotenv()


def verify_llm_settings_for_strict_eval():
  """
  Verifies that either OpenAI or Azure settings are set.

  Returns:
      bool: True if either OpenAI or Azure settings are set, False otherwise.
      str: Error message if neither settings are set.
  """
  print("DRYRUN: ", os.getenv("DRYRUN"))
  if not os.getenv("DRYRUN"):
    return False, "DRYRUN environment not set"

  openai_settings = [
    os.getenv("TEST_OPENAI_ENDPOINT"),
    os.getenv("TEST_OPENAI_API_KEY"),
  ]

  azure_settings = [
    os.getenv("TEST_AZURE_OPENAI_ENDPOINT"),
    os.getenv("TEST_AZURE_OPENAI_API_KEY"),
    os.getenv("TEST_AZURE_OPENAI_API_VERSION"),
  ]
  print(azure_settings)

  if all(openai_settings):
    return True, ""
  elif all(azure_settings):
    return True, ""
  else:
    return False, "Either OpenAI or Azure settings must be set."

graph = JiraGraph()

def format_results(results):
    output = "# Evaluation Results\n\n"
    correct = sum(1 for result in results if result.get('score', False))
    total = len(results)
    accuracy = correct / total if total > 0 else 0
    output += f"## Accuracy: {accuracy:.2%}\n\n"
    return output


def print_banner(title, obj):
    print("=" * 80)
    print(title)
    pprint.pprint(obj)
    print("=" * 80)


def read_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        return data


@pytest.mark.langsmith
async def test_eval_strict(input_file_path ,destination_file_path, test_ids=None):
    data = read_yaml(input_file_path)

    # Filter tests by test_ids
    if test_ids:
        test_ids = set(test_ids.split(','))
        data['tests'] = {k: v for k, v in data['tests'].items() if k in test_ids}

    # Extract the prompts, reference trajectories, and notes from the dataset
    action_type = list(data['tests'].keys())
    prompts = [test[0]['input'] for test in data['tests'].values()]

    reference_trajectories = []
    for test in data['tests'].values():
        res  = []
        for sol in test[0]['reference_trajectory']:
            temp = list(sol.values())

            res.append(temp[0].replace('\n', '').split(';'))
        reference_trajectories.append(res)
    # Run the evaluation
    results = []
    print(list(zip(action_type, prompts, reference_trajectories)))
    for action_type, each_prompt, each_reference_trajectories in zip(
      action_type,
      prompts,
      reference_trajectories,
    ):
        print("#" * 80)
        print(f"Action Type:", action_type)
        print(f"Prompt: {each_prompt}")
        print(f"Reference Trajectories: {each_reference_trajectories}")
        print("#" * 80)
        # Generate a unique thread ID
        thread_id = uuid.uuid4().hex
        config = {"configurable": {"thread_id": thread_id,"thread_ts": datetime.now(),}}
        _ = graph.get_graph().invoke({"messages": [{"role": "user","content": each_prompt}],}, config)

        extracted_trajectory = extract_langgraph_trajectory_from_thread(
            graph.get_graph(), {"configurable": {"thread_id": thread_id}}
        )
        print(graph.get_graph())
        final_extracted_trajectory = []
        print_banner("Extracted Trajectory:", extracted_trajectory)
        for e in extracted_trajectory["outputs"]["steps"]:
            final_extracted_trajectory.extend(e)

        score = False
        for each_reference_trajectory in each_reference_trajectories:
            print_banner("Reference Trajectory:", each_reference_trajectory)
            extracted_trajectory["outputs"]["steps"] = [final_extracted_trajectory]
            print(extracted_trajectory)
            print(each_reference_trajectory)
            res = await graph_trajectory_strict_match_async(
                outputs=extracted_trajectory["outputs"],
                reference_outputs={"inputs": [], "results": [], "steps": [each_reference_trajectory]},
            )
            print_banner("Results:", res)
            if res['score']:
                score = True
                break

        results.append({
            "prompt_type": action_type,
            "prompt": each_prompt,
            "score": score,
            "extracted": extracted_trajectory["outputs"]["steps"],
            "reference": each_reference_trajectories,
        })

    ########################################
    #  Write the results to a output file  #
    ########################################

    headers = ["Action Type", "Prompt", "Score", "Extracted Trajectory", "Reference Trajectories"]
    table = [
        [result["prompt_type"], result["prompt"], result["score"], result["extracted"], result["reference"]]
        for result in results
    ]
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(destination_file_path, 'w') as readme_file:
        readme_file.write(f"## Evaluation Date: {current_time}\n\n")
        readme_file.write(format_results(results))
        readme_file.write("\n\n")
        readme_file.write(tabulate(table, headers=headers, tablefmt="github"))
    # Print the accuracy table to stdout
    print(format_results(results))
    print(tabulate(table, headers=headers, tablefmt="github"))

def main(config_file ,test_ids=None , **kwargs):
    is_ok, msg = verify_llm_settings_for_strict_eval()
    config = yaml.safe_load(open(config_file))
    input_file_path = config.get('FILEPATH','strict_match_dataset.yaml')
    destination_file_path = config.get('DESTINATION_FILEPATH','README.md')
    if not is_ok:
        print(f"Error: {msg}")
        exit(1)
    asyncio.run(test_eval_strict(input_file_path , destination_file_path,test_ids=test_ids))

if __name__ == "__main__":
    #python3 runStrictMmatch.py --config_file ../configs/strict_match_config.yaml
    fire.Fire(main)

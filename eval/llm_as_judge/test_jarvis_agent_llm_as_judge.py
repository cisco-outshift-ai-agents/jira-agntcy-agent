from agentevals.graph_trajectory.utils import (
    extract_langgraph_trajectory_from_thread,
)
from agentevals.graph_trajectory.llm import create_graph_trajectory_llm_as_judge

from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

from jarvis_agent import JarvisAgent
from llm_factory import JarvisLLMFactory

import pprint
import pytest
import asyncio
import pandas as pd

store = InMemoryStore()
checkpointer = None
checkpointer = MemorySaver()
jarvis_agent = JarvisAgent(checkpointer, store)
graph = jarvis_agent.get_graph()

@pytest.mark.langsmith
async def test_llm_as_judge(query: str, use_custom_prompt: bool = True):
  await graph.ainvoke(
    {"messages": [{"role": "user", "content": query}]},
    config={"configurable": {"thread_id": "1"}},
  )
  # Extract the trajectory from the first two thread runs
  extracted_trajectory = extract_langgraph_trajectory_from_thread(
    graph, {"configurable": {"thread_id": "1"}}
  )

  pprint.pp(extracted_trajectory)

  CUSTOM_PROMPT = """You are an expert data labeler.
  Your task is to grade the accuracy of an AI agent's internal steps in resolving a user queries.

  <Rubric>
    An accurate trajectory:
    - Makes logical sense between steps
    - Shows clear progression
    - Is perfectly efficient, with no more than one tool call
    - Is semantically equivalent to the provided reference trajectory, if present
  </Rubric>

  <Instructions>
    Grade the following thread, evaluating whether the agent's overall steps are logical and relatively efficient.
    For the trajectory, "__start__" denotes an initial entrypoint to the agent, and "__interrupt__" corresponds to the agent
    interrupting to await additional data from another source ("human-in-the-loop"):
  </Instructions>

  <thread>
  {thread}
  </thread>

  {reference_outputs}
  """

  if use_custom_prompt:
    graph_trajectory_evaluator = create_graph_trajectory_llm_as_judge(
        prompt=CUSTOM_PROMPT,
        judge=JarvisLLMFactory("gpt-4o-mini").get_llm_connection(),
    )
  else:
    graph_trajectory_evaluator = create_graph_trajectory_llm_as_judge(
        judge=JarvisLLMFactory("gpt-4o-mini").get_llm_connection(),
    )

  res = graph_trajectory_evaluator(
      inputs=extracted_trajectory["inputs"],
      outputs=extracted_trajectory["outputs"],
  )
  return res

if __name__ == "__main__":
  def run_test(query: str):
    asyncio.run(test_llm_as_judge(query))

  df = pd.read_csv("./eval/llm_as_judge/prompt_dataset.csv", sep=';')

  results = []
  for _, row in df.iterrows():
    query = row['prompt']
    test_id = row['id']
    print("="*80)
    print(f"Running test for: {query} (ID: {test_id})")
    try:
      res = asyncio.run(test_llm_as_judge(query, use_custom_prompt=False))
      score = res['score']
      comment = "\n".join([f"{line}" for line in res['comment'].split('\n')])
      results.append({'id': test_id, 'query': query, 'score': score, 'comment': comment})
      print(f"Score: {score}")
      print(f"Comment: {comment}")
    except Exception as e:
      print(f"Error running test for {query}: {e}")
      results.append({'id': test_id, 'query': query, 'score': None, 'comment': f"Error: {e}"})

  print("="*80)
  print("Final Results:")
  results_df = pd.DataFrame(results)
  print(results_df)

  # Calculate and print accuracy
  successful_tests = results_df[results_df['score'].notna()]
  if not successful_tests.empty:
    accuracy = successful_tests['score'].mean() * 100
    print(f"\nOverall Accuracy: {accuracy:.2f}%")
  else:
    print("\nNo successful tests to calculate accuracy.")

  # Convert results to markdown table
  markdown_table = results_df.to_markdown(index=False)
  print("\nMarkdown Table:")
  print(markdown_table)

  # Write results to README.md
  with open("./eval/llm_as_judge/README.md", "w") as f:
    f.write("# Jarvis Agent LLM-as-Judge Evaluation Results\n\n")
    f.write("## Overall Accuracy\n\n")
    if not successful_tests.empty:
      accuracy = successful_tests['score'].mean() * 100
      f.write(f"Overall Accuracy: {accuracy:.2f}%\n\n")
    else:
      f.write("No successful tests to calculate accuracy.\n\n")
    f.write("## Detailed Results\n\n")
    f.write(markdown_table)
    f.write("\n")
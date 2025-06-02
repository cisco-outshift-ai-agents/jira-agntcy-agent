from jira_agent.graph.graph import JiraGraph
from dotenv import load_dotenv
import json
import yaml
from collections import defaultdict

if __name__ == '__main__':
    """
    python3 generateReferenceTrajectory.py --input_file ../Dataset/Trajectory_project.json --count 1
    """
    load_dotenv()
    graph = JiraGraph()
    filename = "../Dataset/project_prompts.json"
    count = 1
    project_tool_calls = ["get_jira_project_by_name", "update_jira_project_lead",
                          "update_jira_project_description", "create_jira_project"]
    issue_tool_calls = ['search_jira_issues_using_jql', 'perform_jira_transition',
                        'get_jira_transitions', 'create_jira_issue', 'assign_jira',
                        'update_issue_reporter', 'add_new_label_to_issue', 'get_jira_issue_details']

    final_output = []
    new_data = defaultdict(list)
    with open(filename, 'r') as file:
        prompts = json.load(file)

    for values in prompts:
        counter = 0
        trajectories = []
        while counter < count:
            prompt_type = values['action']
            user_prompt = values['query']
            result,trajectory_result = graph.serve(user_prompt)
            trajectory = [trajectory.model_dump() for trajectory in trajectory_result['messages']]
            trajectories.append(trajectory)
        for trajectory_info in trajectories:
            reference_trajectories = []
            expected_results = []
            for i,trajectory in enumerate(trajectory_info):
                response = []
                is_first = False
                response.append("__start__")
                for traject in trajectory:
                    if traject['type'] == 'ai':
                        if traject['name'] == 'jira_supervisor':

                            response.append(f"{traject['name']}")
                            response.append(f"{traject['name']}:__start__")
                            response.append(f"{traject['name']}:agent")

                            if traject.get('tool_calls'):
                                response.append(f"{traject['name']}:tools")
                                for tools in traject.get('tool_calls'):
                                    if tools['name'] == 'transfer_to_jira_projects_agent':
                                        response.append(f"jira_projects_agent")
                                        response.append(f"jira_projects_agent:__start__")
                                        response.append(f"jira_projects_agent:agent")
                                    elif tools['name'] == 'transfer_to_jira_issues_agents':
                                        response.append(f"jira_issues_agent")
                                        response.append(f"jira_issues_agent:__start__")
                                        response.append(f"jira_issues_agent:agent")

                        elif traject['name'] == 'jira_issues_agent' or traject['name'] == 'jira_projects_agent':
                            if traject.get('tool_calls') and traject.get('tool_calls')[0]['name'] == "transfer_back_to_jira_supervisor":
                                is_first = True
                                continue
                            if traject.get('tool_calls'):
                                if not is_first:
                                    response.append(f"{traject['name']}:tools")
                                    is_first = True
                                for tool in traject['tool_calls']:
                                    if tool['name'] in project_tool_calls or tool['name'] in issue_tool_calls:
                                        response.append(f"{traject['name']}:agent")
                                        response.append(f"{traject['name']}:tools")
                            else:
                                if not is_first:
                                    response.append(f"{traject['name']}:tools")
                                    is_first = True
                                response.append(f"{traject['name']}:agent")
                                response.append(f"{traject['name']}:generate_structured_response")
                    reference_trajectories.append({f"Solution{i+1}": ";".join(response)})
                    expected_results.append(result)


            visited = set()
            trajectory_selected = []
            if list(trajectory.values())[0] not in visited:
                visited.add(list(trajectory.values())[0])
                trajectory_selected.append(trajectory)
            new_data[item['prompt_type']].append({
                "input": item["input"],
                "reference_trajectory": trajectory_selected,
            })
    #     final_output.append({
    #         "prompt_type": prompt_type,
    #         "input": prompt,
    #         "reference_trajectory": reference_trajectories,
    #         "response": expected_results
    #     })
    #
    #
    # with open("../Dataset/reference_trajectory.json", 'w') as file:
    #     json.dump(final_output, file, indent=2)
    with open('../Dataset/strict_match_dataset.yaml', 'w') as outfile:
        yaml.dump({"tests": new_data}, outfile, default_flow_style=False)

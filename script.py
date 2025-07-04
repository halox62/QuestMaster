import re
import json
from collections import defaultdict


with open("story.txt", "r", encoding="utf-8") as file:
            story = file.read()

node_pattern = re.compile(r'^(\d+)\.\s(.*?)(?=^\d+\.|\Z)', re.DOTALL | re.MULTILINE)
nodes = node_pattern.findall(story)


graph = {}
edges = defaultdict(list)

for node_number, node_content in nodes:
    node_number = node_number.strip()
    description, *choices = re.split(r'\n\s*→ ', node_content.strip())
    description = description.strip()
    choice_pattern = re.compile(r'(.+?)\s*\[go to (\d+)\]')
    outgoing = choice_pattern.findall('\n'.join(choices))
    
    graph[node_number] = {
        "description": description,
        "options": [{"text": text.strip(), "target": target.strip()} for text, target in outgoing]
    }


langgraph_nodes = {
    f"node_{node_id}": {
        "description": node["description"],
        "options": {f"option_{i}": f"node_{opt['target']}" for i, opt in enumerate(node["options"])}
    }
    for node_id, node in graph.items()
}


for node_id, node in langgraph_nodes.items():
    if '❌' in node["description"] or '✅' in node["description"]:
        node["options"] = {}  


graph_json_path = "langgraph_adventure.json"
with open(graph_json_path, "w") as out_file:
    json.dump(langgraph_nodes, out_file, indent=2)

graph_json_path
#from ReflectionAgent import reflectionAgent
from langchain_ollama import ChatOllama
from pydantic import BaseModel, ValidationError
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from typing import List,Dict, Tuple
import subprocess
import os
import json
import sys
import re
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv 
from langgraph.graph import StateGraph, END
from flask import Flask, request, jsonify, render_template_string, redirect
from collections import defaultdict
from flask_cors import CORS
from langgraph.pregel import Pregel
from typing import TypedDict


app = Flask(__name__)

CORS(app) 

load_dotenv()



# Suppress Trio warning
sys.excepthook = sys.__excepthook__

# Pydantic models
class PDDLAction(BaseModel):
    name: str
    parameters: List[str]
    preconditions: List[str]
    effects: List[str]

class PDDLDomain(BaseModel):
    domain_name: str
    requirements: List[str]
    types: List[str]
    predicates: List[str]
    actions: List[PDDLAction]

class PDDLProblem(BaseModel):
    problem_name: str
    domain_name: str
    objects: Dict[str,str]
    init: List[str]
    goal: List[str]

class PlanningState(TypedDict):
    lore_text: str
    story: str
    domain_obj: PDDLDomain
    problem_obj: PDDLProblem
    domain_str: str
    problem_str: str
    plan_success: bool
    stdout: str
    stderr: str

# Carica la narrativa
try:
    with open("lore.txt", "r", encoding="utf-8") as file:
        lore_text = file.read()
except FileNotFoundError:
    print("Errore: Il file 'lore.txt' non è stato trovato.")
    exit(1)


#llm = ChatOllama(model="llama3.2")

#llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)



# Prompt dominio
domain_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert PDDL domain modeler. Your task is to translate a narrative adventure into a well-structured and interdependent PDDL domain, strictly adhering to the narrative graph's nodes and choices to define actions, ensuring actions are executed in the order of the nodes as provided, and preventing "Undefined object" errors by ensuring all objects are consistently defined and referenced.

==============================
OUTPUT FORMAT (JSON ONLY)
==============================

Return ONLY a single **valid JSON object**:
{{
  "domain_name": "brava-island-adventure",
  "requirements": ["strips", "typing"],
  "types": ["player", "location", "item", "trap", "puzzle", "ally"],
  "predicates": [
    "(player-at ?p - player ?l - location)",
    "(has ?p - player ?i - item)",
    "(ally-present ?a - ally ?l - location)",
    ...
  ],
  "actions": [
    {{
      "name": "action-name",
      "parameters": ["?param - type", ...],
      "preconditions": ["(predicate ...)"],
      "effects": ["(predicate ...)", "(not (predicate ...))"]
    }}
  ]
}}

==============================
DESIGN CONSTRAINTS
==============================

1. **Strict Node Adherence**: Actions must correspond directly to the choices in each node of the narrative graph (e.g., node 1 choices lead to nodes 2, 3, or 4). Each action must reflect a specific choice and transition to the corresponding node’s state.
2. **Node Order**: Actions must respect the sequence of nodes, with preconditions and effects aligning with the state changes (e.g., location, items, allies, traps, puzzles) described in each node.
3. **Interconnected Actions**: Preconditions must depend on effects from previous nodes, ensuring progression (discovery → interaction → unlocking → goal).
4. **Mid-Level Predicates**: Use predicates to represent progress (e.g., `(map-deciphered)`, `(altar-solved)`, `(poisoned ?p)`, `(ally-present ?a ?l)`), reflecting narrative states.
5. **Negative Effects**: Include `(not ...)` effects for state transitions (e.g., changing location, removing items, disarming traps) as per the narrative.
6. **Kebab-Case**: Use kebab-case for all identifiers (e.g., `grandfathers-compass`, `dense-jungle`, `altar-solved`).
7. **No Unused Predicates**: Only include predicates used by actions, derived from the narrative’s states and transitions.
8. **Meaningful Conditions**: Preconditions must reflect narrative preconditions (e.g., player location, items held, health status, ally status) at each node.
9. **No Constants**: Use only variables (e.g., `?p - player`, `?l - location`) in predicates, preconditions, and effects, declared in `:parameters`.
10. **No `:init` or `:goal`**: Define only the domain, not the problem file.
11. **Action Mapping**: Each action must map to a narrative choice (e.g., `venture-into-jungle` for node 1 → node 2) and produce effects matching the destination node’s state.
12. **Failure and Success States**: Include actions for failure endings (nodes 14, 15, 18, 24, 29, 33, 36) with effects like `(fatally-injured ?p)` or `(trapped ?p)`, and success ending (node 35) with `(treasure-found)`.
13. **Object Management**:
    - **Explicit Object Listing**: Ensure all objects mentioned in the narrative (e.g., locations: `island-shore`, `dense-jungle`, `rocky-shore`, `ancient-ruins`, `mountain-temple`, `la-boca-del-tiempo`; items: `grandfathers-compass`, `old-map`, `carved-obsidian-medallion`, `rusted-climbing-gear`, `wax-sealed-map-segment`, `torn-journal-page`, `purifying-canteen`; allies: `native-scout`, `hermit`; traps: `poison-dart-trap`, `pit-trap`, `collapsing-floor-trap`; puzzles: `altar-puzzle`, `vault-puzzle`) are accounted for in predicates and actions.
    - **Type Consistency**: Assign each object to a specific type (e.g., `dense-jungle - location`, `grandfathers-compass - item`, `native-scout - ally`) and ensure actions reference them correctly.
    - **Object Reference Validation**: All objects used in action parameters, preconditions, or effects must be declared as variables in `:parameters` and bound to narrative-defined objects.
    - **Prevent Undefined Objects**: Ensure no action references an object not explicitly defined in the narrative or not covered by a typed variable (e.g., `?i - item` covers all items like `grandfathers-compass`).
14. **Allies and Items**: Model allies (e.g., `native-scout`, `hermit`) with predicates like `(ally-present ?a ?l)` and items with `(has ?p ?i)`, reflecting acquisition or use in nodes (e.g., node 11 for `native-scout`, node 21 for `carved-obsidian-medallion`).
15. **Traps and Puzzles**: Model traps with predicates like `(trap-active ?t ?l)` and `(trap-triggered ?t ?l)`, and puzzles with `(puzzle-solved ?z ?l)`, with actions to disarm or solve them (e.g., nodes 17, 16, 22).
16. **Health Status**: Use predicates like `(poisoned ?p)`, `(fatally-injured ?p)`, `(trapped ?p)` to track player state, with actions reflecting narrative outcomes (e.g., node 14 for poison failure, node 35 for success).
17. **Output Only JSON**: Return only a valid JSON object, with no text, explanations, or markdown outside the JSON structure.

==============================
DEBUGGING GUIDANCE FOR PROBLEM FILE
==============================

To prevent "Undefined object" errors in the problem file:
- Declare all objects in `:objects` with their types, matching the narrative (e.g., `island-shore dense-jungle rocky-shore - location`, `grandfathers-compass old-map carved-obsidian-medallion - item`, `native-scout hermit - ally`).
- Ensure object names in the problem file match the kebab-case identifiers in the domain (e.g., `grandfathers-compass`, not `grandfather’s-compass`).
- Verify that all objects referenced in `:init` (e.g., `(player-at player island-shore)`, `(has player grandfathers-compass)`) are declared in `:objects`.
- Check that goal conditions in `:goal` only reference declared objects and valid predicates.

==============================
INPUT: Narrative
==============================

{narrative}
"""),
    ("user", "{narrative}")
])

# Prompt problema
problem_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an AI that generates a complete and valid PDDL problem file based on a narrative, a PDDL domain definition, and an initial state described in the lore.

Return ONLY a valid JSON object with the following structure:

{{
  "problem_name": "lowercase-kebab-case",
  "domain_name": "exact-domain-name",
  "objects": {{
    "object1": "type1",
    "object2": "type2"
  }},
  "init": [
    "(predicate constant1 constant2)"
  ],
  "goal": [
    "(predicate constant1 constant2)"
  ]
}}

==============================
RULES
==============================

- Use only predicates and types declared in the domain.
- All constants in init and goal must be declared in the objects section, EXCEPT those constants already defined as fixed constants in the domain file.
- Do NOT include in the objects section any constants that are already declared in the domain as fixed constants.
- Do not use variables in init or goal.
- Do not invent new types or predicates.
- The init should reflect the lore (i.e., the initial world state).
- The goal must reflect the success criteria in the narrative.
- For objects that must be acquired (e.g., a tome), include a predicate in init to specify their location (e.g., `(tome-at tome1 library)`).
- Only locations explicitly accessible in the initial state (per the lore) should have `(accessible location)` in init.
- Ensure the goal aligns with the narrative’s objective (e.g., possessing a specific object).
- Use only object names (constants) consistent with the domain's expectations, e.g., if the domain assumes objects like "map-fragment", name them accordingly (e.g., "map-fragment-1").
- The goal must correspond to the outcome of a high-level success action (e.g., (treasure-found adventurer1)) defined in the domain.
- Every object used in the goal must appear in init or be the result of a reachable action.
- Do not include predicates in init or goal that refer to undefined constants or omit required parameters.

==============================
STEPS
==============================

1. Extract all objects and assign them types based on the domain and narrative, EXCLUDING any constants already declared in the domain as fixed constants.
2. Instantiate the initial state from the lore using only valid predicates, including object locations.
3. Define the goal according to the narrative’s objective using ground atoms.
4. Ensure objects like tomes are placed in their correct initial locations (e.g., library) per the narrative.

==============================
EXAMPLE
==============================

Narrative: "A robot must move a box from room1 to room2."

Response:
{{
  "problem_name": "move-box",
  "domain_name": "box-moving",
  "objects": {{
    "robot1": "robot",
    "box1": "box",
    "room1": "room",
    "room2": "room"
  }},
  "init": [
    "(at robot1 room1)",
    "(box-at box1 room1)"
  ],
  "goal": [
    "(box-at box1 room2)"
  ]
}}

==============================
INPUT
==============================

Lore:
{lore}

Narrative:
{narrative}

Domain:
{domain}
"""),
    ("user", "{lore}"),
    ("user", "{narrative}"),
    ("user", "{domain}")
])

generate_story_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a story creator who must create a simple, interactive story. It must be based on the Lore Document and designed to produce a robust and consistent PDDL problem and domain, without duplicate or undefined objects.

You are provided with a Lore Document that includes:
- The initial state, objective, obstacles, and world context of a quest.
- A branching factor (minimum and maximum number of narrative choices per step).
- Depth constraints (minimum and maximum number of steps to reach the objective).

🎯 Your task:
Write a story composed of numbered sections, where each section represents a state of the story. Each section must include:
- A **Current State** section listing explicit boolean flags (e.g., `medallion_found: false`, `puzzle_solved: false`) that describe the protagonist's current world state, including location, inventory, health, alliances, and known information.
- A **Prerequisites** paragraph listing the specific conditions required to access this section, expressed as narrative statements that correspond to the boolean flags.
- A vivid **Narrative Description** (150-200 words) that immerses the reader in the scene, establishing its atmosphere and stakes, using consistent names for places, objects, and characters (e.g., "jungle", "carved obsidian medallion", "native explorer").
- A **Choices** section with a number of choices defined by the **branching factor** of the **Lore Document**, each of which includes:
  - A clear **action** taken by the protagonist, translatable into a PDDL operator.
  - The immediate **consequence**, which updates one or more boolean flags.
  - The target **section number** (e.g., [go to 7]).

🧩 Structure Rules:
- Use numbered sections (1, 2, 3, ...) to represent distinct story states.
- Each section must list all booleans relevant to the story state.
- Booleans must update logically across sections, and actions must change the relevant flags.
- Some paths may converge on the same section to create loops or shortcuts.
- Choices must vary in risk or difficulty (e.g., safe but slow vs. risky but fast).
- The path to success must require depth constraints defined in the Lore Document, which include actions such as:
  - Moving to multiple locations.
  - Collecting multiple items.
  - Solving puzzles.
  - Disarming traps.
  - Forming alliances.
  - Unlocking locations.
  - Performing a final ritual.
- Avoid generic actions such as 'navigate-traps-and-puzzles' or 'discover-treasure' that allow shortcuts to the objective.

❌ Rules for Failures:
- Include **at least 3 distinct failure endings**, marked with ❌.
- Failures must occur at different points in the narrative:
  - At least one early (within 3 phases).
  - At least one midway (4-6 phases).
  - At least one late (7+ phases).
- Failures must be reachable by **multiple paths** and result from plausible mistakes.

✅ Rules for Success:
- Include **at least one positive ending**, marked with ✅.
- The winning path must involve overcoming key obstacles and satisfy the **depth_constraints**.
- Success should not be the easiest or shortest path.

🎭 Narrative Guidelines:
- Keep the story **simple but engaging**, with a clear focus on the protagonist's journey.
- Use **descriptive prose** in the narrative description to create an immersive atmosphere (e.g., sounds, smells, emotions).
- Make choices meaningful and their consequences logical.
- Use consistent names for places, objects, and characters that align with PDDL.

🛍️ Format:
- Each section begins with a numbered heading (e.g., 1).
- Include a **Current State** section with boolean flags.
- Include a **Prerequisites** paragraph with narrative-style requirements based on the booleans.
- Include a **Narrative Description** (150-200 words).
- Conclude with a **Choices** section listing **depth_constraints** options in this format:
  → *Action*: *Consequence (updates booleans)* [go to X]
- Endings are marked:
  ✅ for positive endings
  ❌ for failure endings

🖍️ Output Style:
- Minimum **1,000 words** in total.
- Use vivid, engaging prose; avoid dry summaries.
- Make sure all actions and consequences are **specific and reflect boolean updates**.

📏 Example boolean flags:
- medallion_found
- native_trust_earned
- puzzle_solved
- wounded
- poisoned
- ally_present
- temple_accessible
- treasure_claimed

Here is the Lore Document:

{lore}
    """),
    ("user", "{lore}")
])


def reflectionAgent(error_log: str = "") -> Tuple[str, str, bool]:
    try:
        with open("story.txt", "r", encoding="utf-8") as file:
            story = file.read().strip()
   
        with open("domain.pddl", "r", encoding="utf-8") as file:
            domain = file.read()
   
        with open("problem.pddl", "r", encoding="utf-8") as file:
            problem = file.read()
    except FileNotFoundError:
        return "Nessun piano trovato. La tua avventura termina qui.", "", False
    
   
    if "search stopped without finding a solution." in error_log.lower():
        print("⚠️ Nessuna soluzione trovata.") 
        
        storyPrompt = ChatPromptTemplate.from_messages([
            ("system", """
You are an expert interactive narrative designer and planning assistant.

You are given:
- A narrative story.
- An error log from an AI planner that failed to generate a valid plan.
- A PDDL domain definition that was generated from the story.

Your task:
1. Analyze the story, domain, and the error log to infer why the planner failed.
2. Suggest potential modifications to the story.
3. Ask the user to approve or modify these narrative changes.
4. Format your suggestions clearly.

You should not output fixed domain/problem code — your goal is to help fix the story collaboratively.

---

Error Log:
{error_log}

Story:
{story}
"""),
            ("user", "Domain:\n{domain}\nError Log:\n{error_log}\nStory:\n{story}")
        ])
        
        story_corr = llm.invoke(storyPrompt.format_messages(domain=domain, error_log=error_log, story=story))
        options = story_corr.content.strip()

        print("\n--- Suggerimenti automatici ---\n")
        print(options)

        print("\nVuoi accettare queste modifiche? (s) or (n)")
        choice = input().strip().lower()

        if choice == 's':
            storyPromptGenerate = ChatPromptTemplate.from_messages([
("system", """
You are an expert interactive storyteller.

You are given:
- The original version of a fantasy narrative.
- A set of proposed changes to that story (e.g., add characters, modify goals, make locations accessible).

Your task is to rewrite the original story **by applying the proposed changes**, making sure the result is coherent, logical, and still aligned with the narrative tone and structure.

Return only the final, rewritten story.

---

Original Story:
{story}

Proposed Modifications:
{options}
"""),
("user", "Story:\n{story},Proposed Modifications:\n{options}")
])
            story_corrV = llm.invoke(storyPromptGenerate.format_messages(story=story, options=options))
            story_fixed = story_corrV.content.strip()
            try:
                with open("story.txt", "w") as f:
                    f.write(story_fixed)
                    return "","",True
            except Exception as e:
                print("Errore nella storia:", e)



        elif choice == 'n':
            print("Storia non valida")
            return "","",False
  



    # Prompt per correggere il dominio
    domain_corr_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert in PDDL domain modeling.
You are given a PDDL domain definition that may contain syntax or semantic errors with {story}.

You are also given an error log from a planner that tried to use the domain.

Your task:
- Validate the domain for correctness and completeness.
- Identify any errors such as missing predicates, incorrect types, undefined references, or syntax issues.
- Use the error log if relevant to locate the issues.
- Correct the domain so that it is valid and ready for a planner.
- Return ONLY the corrected PDDL domain text, with no extra explanation or formatting.

Error Log:
{error_log}
         
Story:
{story}
"""),
        ("user", "{domain},{story},{error_log}")
    ])

    domain_corr = llm.invoke(domain_corr_prompt.format_messages(domain=domain, error_log=error_log,story=story))
    domain_fixed = domain_corr.content.strip()

    # Prompt per il problema
    problem_corr_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert in PDDL problem modeling.
You are given a PDDL problem definition and its corresponding domain (which is correct)  with {story}.

You are also given the error log of a failed planning attempt.

Your task:
- Validate the problem for correctness and consistency with the domain.
- Use the error log if useful to identify possible semantic issues.
- Fix undefined objects, mismatched types, invalid initial state or goals.
- Return ONLY the corrected PDDL problem text, with no extra explanation or formatting.
- You not duplicate objects.

Domain:
{domain}

Error Log:
{error_log}
         
Story:
{story}
"""),
        ("user", "{problem},{error_log},{story}")
    ])

    problem_corr = llm.invoke(problem_corr_prompt.format_messages(
        domain=domain_fixed,
        problem=problem,
        error_log=error_log,
        story=story
    ))

    problem_fixed = problem_corr.content.strip()

    print("\n🧙‍♂️ Dominio PDDL corretto:\n", domain_fixed)
    print("\n📜 Problema PDDL corretto:\n", problem_fixed)

    domain_fixed = re.sub(r"```[a-z]*\n?", "", domain_fixed).strip()
    problem_fixed = re.sub(r"```[a-z]*\n?", "", problem_fixed).strip()

    with open("domain.pddl", "w") as f:
        f.write(domain_fixed)
    with open("problem.pddl", "w") as f:
        f.write(problem_fixed)

    return domain_fixed, problem_fixed, False
   

# Rendering
def render_pddl_action(action: PDDLAction) -> str:
    return f"""(:action {action.name}
    :parameters ({' '.join(action.parameters)})
    :precondition (and {' '.join(action.preconditions)})
    :effect (and {' '.join(action.effects)})
)"""

def render_pddl_domain(domain: PDDLDomain) -> str:
    requirements_str = " ".join(f":{r}" for r in domain.requirements)
    types_str = " ".join(domain.types)
    predicates_str = "\n    ".join(domain.predicates)
    actions_str = "\n".join(render_pddl_action(a) for a in domain.actions)

    return f"""(define (domain {domain.domain_name})
(:requirements {requirements_str})
(:types {types_str})
(:predicates
    {predicates_str})
{actions_str}
)
"""

def render_pddl_problem(problem: PDDLProblem) -> str:
    objects_str = "\n    ".join(f"{name} - {type_}" for name, type_ in problem.objects.items())
    init_str = "\n    ".join(problem.init)
    goal_str = " ".join(problem.goal)
 
    return f"""(define (problem {problem.problem_name})
(:domain {problem.domain_name})
(:objects
    {objects_str})
(:init
    {init_str})
(:goal
    (and {goal_str}))
)
"""


# Fast Downward runner
def run_fast_downward(domain_file: str, problem_file: str) -> Tuple[bool, str, str]:
    cmd = ["./downward/fast-downward.py", domain_file, problem_file, "--search", "astar(lmcut())"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Fast Downward Output:", result.stdout)
        if os.path.exists("sas_plan"):
            with open("sas_plan") as f: print("✅ Piano trovato:\n", f.read())
            return True, result.stdout, result.stderr
        print("❌ Nessun piano trovato.")
        return False, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:

        print("STDERR:\n", e.stdout)
        return False, e.stdout, e.stderr
    

narrative_input = lore_text.strip()


def saveGraphToJson(file_path="story.txt", output_file="langgraph_adventure.json"):
    try:
        graph = loadGraph(file_path)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=4, ensure_ascii=False)
        print(f"Graph saved successfully to {output_file}")
    except Exception as e:
        print(f"Error saving graph: {e}")



def loadGraph(file_path="story.txt"):
    """
    Loads a story from a text file and converts it into a LangGraph-compatible graph structure.
    
    Args:
        file_path (str): Path to the story text file. Defaults to "story.txt".
    
    Returns:
        dict: A dictionary representing the graph nodes with descriptions and options.
    
    Raises:
        FileNotFoundError: If the specified file is not found.
        ValueError: If the file is empty or has invalid format.
    """
    try:
        # Read the story file with UTF-8 encoding
        with open(file_path, "r", encoding="utf-8") as file:
            story = file.read().strip()
        
        # Check if the file is empty
        if not story:
            raise ValueError("Story file is empty or invalid.")

        # Regex to split the story into nodes (each starting with a number followed by a dot)
        node_pattern = re.compile(r'^(\d+)\s*(.*?)(?=^\d+\s*|\Z)', re.DOTALL | re.MULTILINE)
        nodes = node_pattern.findall(story)

        # Initialize graph structures
        graph = {}
        edges = defaultdict(list)

        # Parse each node
        for node_number, node_content in nodes:
            node_number = node_number.strip()
            if not node_number.isdigit():
                raise ValueError(f"Invalid node number: {node_number}")

            # Split node content into description and choices
            node_content = node_content.strip()
            choice_split_pattern = re.compile(r'\n\s*→\s*')
            parts = choice_split_pattern.split(node_content)
            description = parts[0].strip() if parts else ""
            choices = parts[1:] if len(parts) > 1 else []

            # Parse choices using regex to extract text and target node
            choice_pattern = re.compile(r'(.+?)\s*\[go to (\d+(?:\s*[✅❌])?)\]', re.DOTALL)
            outgoing = []
            for choice in choices:
                match = choice_pattern.search(choice.strip())
                if match:
                    text, target = match.groups()
                    outgoing.append({"text": text.strip(), "target": target.strip()})

            # Store node data
            graph[node_number] = {
                "description": description,
                "options": outgoing
            }


        langgraph_nodes = {}
        for node_id, node in graph.items():
            langgraph_node_id = f"node_{node_id}"
            langgraph_nodes[langgraph_node_id] = {
                "description": node["description"],
                "options": {
                    f"option_{i}": {
                        "text": opt["text"],
                        "target": f"node_{opt['target']}"
                    }
                    for i, opt in enumerate(node["options"])
                }
            }

            if '❌' in node["description"] or '✅' in node["description"]:
                langgraph_nodes[langgraph_node_id]["options"] = {}

        saveGraphToJson()

        return langgraph_nodes

    except FileNotFoundError:
        raise FileNotFoundError(f"Story file '{file_path}' not found.")
    except Exception as e:
        raise ValueError(f"Error parsing story file: {str(e)}")

def start_node(state: PlanningState):
    if not state.get("lore_text"):
        raise ValueError("❌ Nessuna narrativa fornita.")
    return state

"""def generate_story_node(state: PlanningState):
    print("Generate Story")
    #response = llm.invoke(generate_story_prompt.format_messages(lore=state["lore_text"]))
    #story = response.content.strip()
    with open("story.txt", "r", encoding="utf-8") as file:
        story = file.read().strip()
    state["story"] = story
    with open("story.txt", "w") as f:
        f.write(story)
    return state"""

def generate_story_node(state: PlanningState):
    print("Generate Story")
    response = llm.invoke(generate_story_prompt.format_messages(lore=state["lore_text"]))
    story = response.content.strip()
    state["story"] = story
    with open("story.txt", "w") as f:
        f.write(story)
    return state

def generate_domain_node(state: PlanningState):
    print("Generate Domain")
    response = llm.invoke(domain_prompt.format_messages(narrative=state["story"]))
    raw = response.content.strip().strip("`")
    with open("domain_raw.json", "w") as f:
        f.write(raw)
    domain_json = json.loads(raw)
    domain_obj = PDDLDomain(**domain_json)
    domain_str = render_pddl_domain(domain_obj)
    state["domain_obj"] = domain_obj
    state["domain_str"] = domain_str
    return state

def generate_problem_node(state: PlanningState):
    print("Generate Problem")
    response = llm.invoke(problem_prompt.format_messages(
        narrative=state["story"], domain=state["domain_str"], lore=state["lore_text"]
    ))
    content = response.content.strip()
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    json_str = match.group(1) if match else content
    with open("problem_raw.json", "w") as f:
        f.write(json_str)
    problem_json = json.loads(json_str)
    problem_obj = PDDLProblem(**problem_json)
    problem_str = render_pddl_problem(problem_obj)
    state["problem_obj"] = problem_obj
    state["problem_str"] = problem_str
    with open("domain.pddl", "w") as f:
        f.write(state["domain_str"])
    with open("problem.pddl", "w") as f:
        f.write(state["problem_str"])
    return state

def run_planner_node(state: PlanningState):
    print("Run Planner")
    success, stdout, stderr = run_fast_downward("domain.pddl", "problem.pddl")
    state["plan_success"] = success
    state["stdout"] = stdout
    state["stderr"] = stderr
    return state

def reflect_node(state: PlanningState):
    print("Agent")
    domain_fixed, problem_fixed, restart = reflectionAgent(error_log=state["stdout"])
    if(not restart):
        with open("domain.pddl", "w") as f:
            f.write(domain_fixed)
        with open("problem.pddl", "w") as f:
            f.write(problem_fixed)
    print(restart)
    state["restart_from_domain"] = restart
    return state


graph = StateGraph(PlanningState)

graph.set_entry_point("start")
graph.add_node("start", start_node)
graph.add_node("generate_story", generate_story_node)
graph.add_node("generate_domain", generate_domain_node)
graph.add_node("generate_problem", generate_problem_node)
graph.add_node("run_planner", run_planner_node)
graph.add_node("reflect", reflect_node)

# Definizione transizioni
graph.add_edge("start", "generate_story")
graph.add_edge("generate_story", "generate_domain")
graph.add_edge("generate_domain", "generate_problem")
graph.add_edge("generate_problem", "run_planner")
graph.add_conditional_edges("run_planner", lambda s: "reflect" if not s["plan_success"] else END)
graph.add_conditional_edges(
    "reflect",
    lambda s: "generate_domain" if s["restart_from_domain"] else "run_planner"
)


appG = graph.compile()

def main():
   input_state = PlanningState(lore_text=lore_text)
   final_state = appG.invoke(input_state)
   print("✅ Piano completato con successo") if final_state["plan_success"] else print("❌ Nessun piano trovato")
   #success, stdout, stderr = run_fast_downward("domain.pddl", "problem.pddl")
   
    

@app.route('/getGraph', methods=['GET'])
def getUserPhotos():
    graph=loadGraph()
    print(graph)

    return jsonify(graph), 200

"""if __name__ == "__main__":
    main()"""

if __name__ == '__main__':
    app.run(host = 'localhost', port = 8080, debug = True)

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
from langgraph.graph import StateGraph

builder = StateGraph()



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

# Carica la narrativa
try:
    with open("lore.txt", "r", encoding="utf-8") as file:
        lore_text = file.read()
except FileNotFoundError:
    print("Errore: Il file 'lore.txt' non è stato trovato.")
    exit(1)


#llm = ChatOllama(model="llama3.2")

llm = ChatOpenAI(model="gpt-4o", temperature=0)



# Prompt dominio
domain_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert PDDL domain modeler. Your task is to translate a narrative scenario into a complete, valid, and well-designed PDDL domain.

Return ONLY a **single valid JSON object**. No extra text, no formatting, no Markdown. Just the JSON.

==============================
OUTPUT STRUCTURE (JSON ONLY)
==============================

{{
  "domain_name": "lowercase-kebab-case-name",
  "requirements": ["strips", "typing"],
  "types": ["type1", "type2", "..."],
  "predicates": [
    "(predicate_name ?param1 - type1 ?param2 - type2 ...)"
  ],
  "actions": [
    {{
      "name": "action-name-in-kebab-case",
      "parameters": ["?param1 - type1", "?param2 - type2"],
      "preconditions": ["(predicate1 ...)", "(predicate2 ...)"],
      "effects": ["(predicate3 ...)", "(not (predicateX ...))"]
    }}
  ]
}}

==============================
RULES AND CONSTRAINTS
==============================

1. Output must be a valid JSON object. No comments, no explanations.
2. Do NOT include :init or :goal — this is only a domain definition.
3. Infer types from the scenario. Use generic, reusable categories (e.g., adventurer, location, object, creature).
4. All predicates and actions must follow PDDL syntax strictly.
5. Use kebab-case for all identifiers: domain name, action names.
6. Parameters must be typed. Variables must begin with ?.
7. Preconditions and effects must be flat lists (do not wrap them in `(and ...)`).
8. For every change in state, include both the new fact and removal of the old state (with `(not ...)` when applicable).
9. Only include predicates that are used in the domain.
10. All strings must be double-quoted to form valid JSON.
11. Include predicates to track object locations (e.g., `(object-at ?o - object ?l - location)`) and creature locations (e.g., `(creature-at ?c - creature ?l - location)`).
12. Ensure actions that grant access to new locations (e.g., solving puzzles, finding hidden paths) set `(accessible ?l - location)` for those locations.
13. Actions that move to goal locations (e.g., treasure chamber) must require specific conditions (e.g., puzzle solved, key acquired).
14. Prevent shortcuts by ensuring actions like `meditate` or `find-hidden-path` require specific preconditions (e.g., being at a sacred site or having a map).

==============================
NARRATIVE INPUT
==============================

NARRATIVE:
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
- All constants in init and goal must be declared in the objects section.
- Do not use variables in init or goal.
- Do not invent new types or predicates.
- The init should reflect the lore (i.e., the initial world state).
- The goal must reflect the success criteria in the narrative.
- For objects that must be acquired (e.g., a tome), include a predicate in init to specify their location (e.g., `(tome-at tome1 library)`).
- Only locations explicitly accessible in the initial state (per the lore) should have `(accessible location)` in init.
- Ensure the goal aligns with the narrative’s objective (e.g., possessing a specific object).

==============================
STEPS
==============================

1. Extract all objects and assign them types based on the domain and narrative.
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
You are a master narrative designer for interactive fiction.

You are given a **Lore Document** that includes:
- The initial state, goal, obstacles, and world context of a quest.
- A branching factor (min and max number of narrative choices per step),
- Depth constraints (min and max number of steps to reach the goal).

🎯 Your task:
Write a **graph-based narrative** made of numbered sections.
Each section is a node in a directed graph, with **choices leading to other nodes**.
Describe what happens in each node and where each choice leads next.

🔁 STRUCTURE RULES:
- Use **numbered sections** to represent states in the story.
- Each section describes a situation and **offers choices**, each one leading to a different section (e.g. → Confront the guardian [go to 7]).
- Some paths may converge to the same node.
- Branches must vary in difficulty and outcome.

❌ FAILURE RULES:
- Include **at least 3 distinct failure endings**, marked clearly (❌).
- These failure nodes must be reachable:
  - From **different parts of the graph**
  - At **different depths** (some early, some late)
  - From **multiple paths** (e.g. two choices far apart lead to the same bad ending)

✅ SUCCESS RULES:
- At least one winning path (✅) must exist.
- The successful path should **not be the easiest** or most obvious.
- Some difficult or risky paths may eventually lead to success.

🎭 NARRATIVE COMPLEXITY:
- Avoid simplistic cause-effect.
- Choices must have **surprising consequences** or delayed effects.
- Introduce dilemmas, moral ambiguity, or misleading clues.
- Mix challenges (logic, courage, knowledge, empathy, etc.).

🧭 FORMAT:
- Each section must be clearly numbered (e.g. 1, 2, 3, ...)
- At the end of each section, list choices with destination nodes like this:

→ Trust the stranger [go to 6]  
→ Sneak into the ruins [go to 7]

- Mark endings with:
  ✅ (if it's a winning goal state)
  ❌ (if it's a failure/dead end)

- Do **not** prompt the player to choose — just describe outcomes.
- Make sure the text is immersive and flows like a real story.

✍️ OUTPUT STYLE:
- Minimum 1000 words.
- Descriptive narrative prose, not bullet points or scripts.
- Each choice must feel meaningful and grounded in the world.

Here is the Lore Document:

{lore}
    """),
    ("user", "{lore}")
])


def reflectionAgent(error_log: str = "") -> Tuple[str, str]:
    print("Errore")
    print(error_log)
    import re

    try:
        with open("story.txt", "r", encoding="utf-8") as file:
            story = file.read().strip()
    except FileNotFoundError:
        return "Nessun piano trovato. La tua avventura termina qui.", "", False

    try:
        with open("domain.pddl", "r", encoding="utf-8") as file:
            domain = file.read()
    except FileNotFoundError:
        return "Nessun piano trovato. La tua avventura termina qui.", "", False

    try:
        with open("problem.pddl", "r", encoding="utf-8") as file:
            problem = file.read()
    except FileNotFoundError:
        return "Nessun piano trovato. La tua avventura termina qui.", "", False

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

    # Rimuove eventuali blocchi Markdown
    domain_fixed = re.sub(r"```[a-z]*\n?", "", domain_fixed).strip()
    problem_fixed = re.sub(r"```[a-z]*\n?", "", problem_fixed).strip()

    with open("domain.pddl", "w") as f:
        f.write(domain_fixed)
    with open("problem.pddl", "w") as f:
        f.write(problem_fixed)

    return domain_fixed, problem_fixed
   

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
        print("STDOUT:\n", e.stdout)
        print("STDERR:\n", e.stderr)
        return False, e.stdout, e.stderr
    


narrative_input = lore_text.strip()


def main():
    narrative_input = lore_text.strip()
    domain_obj = None

    """
    if not narrative_input:
        print("❌ Nessuna narrativa fornita.")
    
    generate_story=llm.invoke(generate_story_prompt.format_messages(lore=narrative_input))

    print(generate_story)
    if not isinstance(generate_story, AIMessage):
        print("Errore: risposta non valida dal modello per il dominio.")

    try:
        with open("story.txt", "w") as f:
            f.write(generate_story.content)
        
    except Exception as e:
        print("Errore nella storia:", e)


    



    try:
        with open("story.txt", "r", encoding="utf-8") as file:
            generate_story = file.read()
    except FileNotFoundError:
        print("Errore: Il file 'lore.txt' non è stato trovato.")
        exit(1)
    


    # Generazione dominio
    domain_raw = llm.invoke(domain_prompt.format_messages(narrative=generate_story))
    if not isinstance(domain_raw, AIMessage):
        print("Errore: risposta non valida dal modello per il dominio.")
    try:
        with open("domain_raw.json", "w") as f:
            f.write(domain_raw.content)
        domain_json = json.loads(domain_raw.content.strip().strip("`"))
        domain_obj = PDDLDomain(**domain_json)
    except Exception as e:
        print("Errore nel parsing del dominio:", e)
        print("Contenuto ricevuto:", domain_raw.content)

    domain_str = render_pddl_domain(domain_obj)

    # Generazione problema
    problem_raw = llm.invoke(problem_prompt.format_messages(narrative=generate_story, domain=domain_str, lore=lore_text))
    if not isinstance(problem_raw, AIMessage):
        print("Errore: risposta non valida dal modello per il problema.")

    content = problem_raw.content.strip()
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = content

    try:
        with open("problem_raw.json", "w") as f:
            f.write(json_str)
        problem_json = json.loads(json_str)
        problem_obj = PDDLProblem(**problem_json)
    except Exception as e:
        print("Errore nel parsing del problema:", e)
        print("Contenuto ricevuto:", content)

    
    problem_str = render_pddl_problem(problem_obj)

    print("\n🧙‍♂️ Dominio PDDL:\n", domain_str)
    print("\n📜 Problema PDDL:\n", problem_str)

    # Scrittura file
    with open("domain.pddl", "w", encoding="utf-8") as f:
        f.write(domain_str)
    with open("problem.pddl", "w", encoding="utf-8") as f:
        f.write(problem_str)
    

"""
    # Esecuzione planner
    print("\n🚀 Avvio Fast Downward...\n")
    success, stdout, stderr=run_fast_downward("domain.pddl", "problem.pddl")

    while not success:
        print("❌ Impossibile proseguire: nessun piano valido.")
        reflectionAgent(error_log=stdout)
        success, stdout, stderr=run_fast_downward("domain.pddl", "problem.pddl")


    exit(1)


"""
def main():
    print("\n🚀 Avvio Fast Downward...\n")
    if not run_fast_downward("domain.pddl", "problem.pddl"):
        print("❌ Impossibile proseguire: nessun piano valido.")
        print("Controlla fast_downward_log.txt per dettagli.")"""
     


if __name__ == "__main__":
    main()
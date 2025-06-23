from langchain_ollama import ChatOllama
from pydantic import BaseModel, ValidationError
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from typing import List
import subprocess
import os
import json
import sys

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
    objects: List[str]
    init: List[str]
    goal: List[str]

# Carica la narrativa
try:
    with open("lore.txt", "r", encoding="utf-8") as file:
        lore_text = file.read()
except FileNotFoundError:
    print("Errore: Il file 'lore.txt' non è stato trovato.")
    exit(1)

# Configura il modello
llm = ChatOllama(model="llama3.2")

# Prompt dominio
domain_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an AI assistant that generates a complete and valid PDDL domain based on a narrative scenario.

Return ONLY a valid JSON object with the following structure:

{{
  "domain_name": "lowercase_name",  // Short and lowercase
  "requirements": ["strips", "typing"],
  "types": ["wizard", "spell", "location", ...],
  "predicates": [
    "(predicate_name ?param - type ...)",
    ...
  ],
  "actions": [
    {{
      "name": "action-name-in-kebab-case",
      "parameters": ["?param1 - type1", "?param2 - type2"],
      "preconditions": ["(predicate1 ...)", "(predicate2 ...)"],
      "effects": ["(predicate3 ...)", "(not (predicate1 ...))"]
    }},
    ...
  ]
}}

Rules:
- Do NOT include 'init' or 'goal' in this JSON. That's for the problem file.
- Use only valid PDDL syntax: all parameters must be typed.
- Keep predicate and action names simple and general (e.g. `at`, `has`, `unlock`, etc.).
- Avoid hardcoding constants in predicates (e.g., `(at ?w - wizard castle)` ❌).
- Use domain types for generalization (e.g., `(at ?w - wizard ?l - location)` ✅).
- Make sure all predicates used in actions are declared in the `predicates` list.

Example output:

{{
  "domain_name": "castle_entry",
  "requirements": ["strips", "typing"],
  "types": ["wizard", "spell", "location"],
  "predicates": [
    "(has_spell ?w - wizard ?s - spell)",
    "(at ?w - wizard ?l - location)",
    "(castle ?l - location)"
  ],
  "actions": [
    {{
      "name": "learn-spell",
      "parameters": ["?w - wizard", "?s - spell"],
      "preconditions": [],
      "effects": ["(has_spell ?w ?s)"]
    }},
    {{
      "name": "cast-spell-to-enter",
      "parameters": ["?w - wizard", "?s - spell", "?l - location"],
      "preconditions": ["(has_spell ?w ?s)", "(castle ?l)"],
      "effects": ["(at ?w ?l)"]
    }}
  ]
}}

Narrative:
{narrative}
"""),
    ("user", "{narrative}")
])

# Prompt problema
problem_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an AI that generates a PDDL problem that is consistent with a domain and a narrative. Respond with valid json that respects the narrative:
Narrativa: {narrative}
"""),
    ("user", "{narrative}")
])

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
    objects_str = "\n    ".join(problem.objects)
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
def run_fast_downward(domain_file: str, problem_file: str) -> bool:
    cmd = ["./downward/fast-downward.py", domain_file, problem_file, "--search", "astar(lmcut())"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Fast Downward Output:", result.stdout)
        if os.path.exists("sas_plan"):
            with open("sas_plan") as f: print("✅ Piano trovato:\n", f.read())
            return True
        print("❌ Nessun piano trovato.")
        return False
    except subprocess.CalledProcessError as e:
        print("STDOUT:\n", e.stdout)
        print("STDERR:\n", e.stderr)
        return False

# Esecuzione
narrative_input = lore_text.strip()
if not narrative_input:
    print("❌ Nessuna narrativa.")
    exit()

# Generazione dominio
domain_raw = llm.invoke(domain_prompt.format_messages(narrative=narrative_input))
if not isinstance(domain_raw, AIMessage):
    print("Errore: risposta non valida dal modello.")
    exit()

try:
    domain_json = json.loads(domain_raw.content.strip().strip("`"))
    domain_obj = PDDLDomain(**domain_json)
except Exception as e:
    print("Errore nel parsing dominio:", e)
    print(domain_raw.content)
    exit(1)

# Generazione problema
problem_raw = llm.invoke(problem_prompt.format_messages(narrative=narrative_input))
if not isinstance(problem_raw, AIMessage):
    print("Errore: risposta non valida dal modello.")
    exit()

try:
    problem_json = json.loads(problem_raw.content.strip().strip("`"))

    problem_obj = PDDLProblem(**problem_json)
except Exception as e:
    print("Errore nel parsing problema:", e)
    print(problem_raw.content)
    exit(1)

# Stampa dominio e problema
domain_str = render_pddl_domain(domain_obj)
exit(1)
problem_str = render_pddl_problem(problem_obj)

print("\n🧙‍♂️ Dominio PDDL:\n", domain_str)
print("\n📜 Problema PDDL:\n", problem_str)

# Scrittura su file
with open("domain.pddl", "w") as f: f.write(domain_str)
with open("problem.pddl", "w") as f: f.write(problem_str)

# Esecuzione planner
print("\n🚀 Avvio Fast Downward...\n")
run_fast_downward("domain.pddl", "problem.pddl")
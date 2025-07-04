from typing import Tuple, List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError
from langchain_core.messages import AIMessage
import subprocess
import os
import json
import sys
import re
from dotenv import load_dotenv

load_dotenv()

# Suppress Trio warning
sys.excepthook = sys.__excepthook__

# Configura il modello
llm = ChatOpenAI(model="gpt-4o", temperature=0)

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
    objects: Dict[str, str]
    init: List[str]
    goal: List[str]

# Carica la narrativa iniziale
try:
    with open("lore.txt", "r", encoding="utf-8") as file:
        lore_text = file.read()
except FileNotFoundError:
    print("Errore: Il file 'lore.txt' non è stato trovato.")
    exit(1)

# Prompt per il dominio PDDL
domain_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert PDDL domain modeler. Your task is to translate a narrative scenario into a complete, valid, and well-designed PDDL domain.

Your output must be a **single valid JSON object**, and nothing else — no explanation, no formatting, no comments. The JSON must strictly follow the structure and rules below.

==============================
OUTPUT STRUCTURE (JSON ONLY)
==============================

{
  "domain_name": "lowercase-kebab-case-name",
  "requirements": ["strips", "typing"],
  "types": ["type1", "type2", "..."],
  "predicates": [
    "(predicate_name ?param1 - type1 ?param2 - type2 ...)"
  ],
  "actions": [
    {
      "name": "action-name-in-kebab-case",
      "parameters": ["?param1 - type1", "?param2 - type2"],
      "preconditions": ["(predicate1 ...)", "(predicate2 ...)"],
      "effects": ["(predicate3 ...)", "(not (predicateX ...))"]
    }
  ]
}

==============================
RULES AND CONSTRAINTS
==============================

1. Output only a JSON object — no extra text, no Markdown, no code blocks.
2. Do NOT include :init or :goal — this is a domain definition, not a problem instance.
3. All types must be inferred from the narrative, using abstract and reusable categories (e.g., wizard, spell, gate, location).
4. All predicates must be written in complete PDDL syntax, including variables and their types (e.g., (at ?w - wizard ?l - location)).
5. Variables in both predicates and actions must be typed and start with ?.
6. Use kebab-case for domain_name and all action name values (e.g., cast-spell).
7. Use flat lists for preconditions and effects. Do not wrap with (and ...).
8. Whenever an action modifies the world state, explicitly remove the old state using (not ...).
9. Use meaningful, semantic variable names (e.g., ?w - wizard, ?l - location, ?s - spell). Do not use ?p1, ?p2, etc.
10. All predicates used in actions must be declared in the predicates list above.
11. Ensure all variables in preconditions and effects are bound to parameters.

==============================
NARRATIVE INPUT
==============================

NARRATIVE:
{narrative}
"""),
    ("user", "{narrative}")
])

# Prompt per il problema PDDL
problem_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an AI that generates a complete and valid PDDL problem file based on a narrative and a corresponding domain definition.

Return ONLY a JSON object with the following structure:

{
  "problem_name": "lowercase-kebab-case",
  "domain_name": "exact-domain-name",
  "objects": {
    "object1": "type1",
    "object2": "type2"
  },
  "init": [
    "(predicate constant1 constant2)"
  ],
  "goal": [
    "(predicate constant1 constant2)"
  ]
}

Rules:
- Use only predicates and types declared in the domain.
- The `objects` section must declare all constants used in `init` and `goal`, with the correct type.
- The `init` field must define the initial state using valid ground atoms (with constants only).
- The `goal` field must define the desired end state, using valid ground atoms (no variables).
- Reflect the narrative's objectives and logic in the goal state.
- Be realistic: do not assume more objects than necessary.
- Avoid redundant predicates in `init`.

Narrative:
{narrative}

Domain:
{domain}
"""),
    ("user", "{narrative},{domain}")
])

# Prompt per aggiornare la narrativa
narrative_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a narrative engine for an interactive fantasy adventure game powered by a PDDL planner.

You are given:
- The previous narrative describing the story so far.
- The player's chosen action, described in narrative form.
- The current PDDL domain and problem definitions, which describe the world's logic, types, predicates, and state.
- The effects of the chosen action (PDDL effects applied to the world state).

Your task is to:
- Generate a new narrative that continues the story seamlessly.
- Incorporate the player's chosen action and its consequences (based on the effects) in a vivid, engaging way.
- Maintain consistency with the PDDL domain (types, predicates, actions) and problem (objects, initial state, goal).
- Introduce new events, challenges, or changes in the world that reflect the action's impact.
- End with a situation that suggests further possible actions without explicitly listing them.
- Keep the tone and style consistent with the fantasy setting.

Rules:
- Do NOT repeat the previous narrative verbatim.
- Do NOT describe the action in isolation; weave it into the story with its effects.
- Do NOT list options or ask the player what to do next.
- Use the PDDL domain, problem, and effects to ensure logical consistency.
- Keep the narrative concise (100–200 words) but rich in detail.

Return ONLY the new narrative in plain English.

Effects:
{effects}
"""),
    ("user", "Previous narrative:\n{narrative}\n\nPlayer's chosen action:\n{choice}\n\nPDDL Domain:\n{domain}\n\nPDDL Problem:\n{problem}\n\nEffects:\n{effects}")
])

# Rendering PDDL
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
)"""

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
)"""

# Esecuzione Fast Downward
def run_fast_downward(domain_file: str, problem_file: str) -> bool:
    cmd = ["./downward/fast-downward.py", domain_file, problem_file, "--search", "astar(lmcut())"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        with open("fast_downward_log.txt", "w") as log_file:
            log_file.write(f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        print("Fast Downward Output saved to fast_downward_log.txt")
        if os.path.exists("sas_plan"):
            with open("sas_plan") as f:
                print("✅ Piano trovato:\n", f.read())
            return True
        print("❌ Nessun piano trovato.")
        return False
    except subprocess.CalledProcessError as e:
        with open("fast_downward_log.txt", "a") as log_file:
            log_file.write(f"STDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")
        print("Errore Fast Downward, dettagli salvati in fast_downward_log.txt")
        return False

# Funzione per applicare gli effetti di un'azione
def apply_action_effects(action: str, domain: PDDLDomain, current_facts: set) -> set:
    # Estrai il nome dell'azione e i parametri
    action = action.strip().strip('()')
    action_name, *params = action.split()
    
    # Trova l'azione nel dominio
    for action_def in domain.actions:
        if action_def.name == action_name.replace('_', '-'):
            # Sostituisci i parametri formali con quelli effettivi
            param_map = dict(zip([p.split('-')[0].strip('?') for p in action_def.parameters], params))
            new_facts = set(current_facts)
            
            # Applica gli effetti
            for effect in action_def.effects:
                if effect.startswith('(not '):
                    # Rimuovi il predicato negato
                    predicate = effect[5:-1]  # Rimuove "(not " e ")"
                    predicate = replace_params(predicate, param_map)
                    new_facts.discard(predicate)
                else:
                    # Aggiungi il predicato positivo
                    predicate = replace_params(effect, param_map)
                    new_facts.add(predicate)
            
            return new_facts
    print(f"⚠️ Azione {action_name} non trovata nel dominio.")
    return current_facts

# Funzione per sostituire i parametri nei predicati
def replace_params(predicate: str, param_map: Dict[str, str]) -> str:
    predicate = predicate.strip('()')
    parts = predicate.split()
    predicate_name = parts[0]
    args = [param_map.get(arg, arg) for arg in parts[1:]]
    return f"({predicate_name} {' '.join(args)})"

# Reflection Agent
def reflectionAgent(domain: PDDLDomain, current_facts: set) -> Tuple[str, str, bool]:
    try:
        with open("sas_plan", "r", encoding="utf-8") as file:
            lines = file.readlines()
            sas_plan_actions = [line.strip() for line in lines if line.strip() and not line.startswith(";")]
    except FileNotFoundError:
        return "Nessun piano trovato. La tua avventura termina qui.", "", False

    if not sas_plan_actions:
        return "Non ci sono azioni disponibili. Hai perso.", "", False
    elif len(sas_plan_actions) == 1:
        return "Hai completato la tua missione! Hai vinto!", "", False

    next_action = sas_plan_actions[0]

    problem_prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a narrative-driven reflection agent in an interactive fantasy game powered by a PDDL planner.

You are given:
- The next grounded action from a valid PDDL plan, which represents the optimal choice for the player.
- The current PDDL domain definition, which describes the world's logic, types, predicates, and actions.
- The current world state (facts).

Your task is to:
1. Present the next action as the primary option with a vivid, story-driven explanation.
2. Invent 1–2 alternative actions that are plausible in the context of the fantasy world and the PDDL domain, but not part of the current plan.
3. Ensure all actions are described in a way that immerses the player in the story, avoiding generic or repetitive explanations.
4. Ensure invented actions are distinct from the plan but could realistically exist in the world, respecting the domain's types and predicates.

Rules:
- Do not reveal the full PDDL plan.
- Use narrative-driven language to describe each option (e.g., "You cast a spell to open the gate" instead of "Execute (cast-spell ?w ?s ?g ?l)").
- Always end with: “Which action do you want to perform?”
- Number the options starting from 1.
- Ensure invented actions are creative but grounded in the fantasy setting and domain constraints.

Output format:
Here are your options:
1. [Primary action] → [Narrative explanation]
2. [Invented action 1] → [Narrative explanation]
3. [Invented action 2] → [Narrative explanation]

Which action do you want to perform?

Domain:
{domain}

Current facts:
{facts}
"""),
        ("user", f"Next action in the plan:\n{next_action}")
    ])

    reflection = llm.invoke(problem_prompt.format_messages(domain=render_pddl_domain(domain), facts="\n".join(current_facts)))
    print("\n" + reflection.content.strip() + "\n")

    while True:
        choice = input("Inserisci il numero della tua scelta (es. '1'): ").strip()
        options = [line.strip() for line in reflection.content.strip().split('\n') if line.strip().startswith(f"{choice}.")]
        if options:
            selected_action = options[0]
            return selected_action, next_action, True
        print("Scelta non valida. Per favore, scegli un numero tra quelli proposti.")

# Ciclo principale del gioco
def main():
    narrative_input = lore_text.strip()
    current_facts = set()
    first_iteration = True
    domain_obj = None

    while True:
        if not narrative_input:
            print("❌ Nessuna narrativa fornita.")
            break

        # Generazione dominio
        domain_raw = llm.invoke(domain_prompt.format_messages(narrative=narrative_input))
        if not isinstance(domain_raw, AIMessage):
            print("Errore: risposta non valida dal modello per il dominio.")
            break
        try:
            with open("domain_raw.json", "w") as f:
                f.write(domain_raw.content)
            domain_json = json.loads(domain_raw.content.strip().strip("`"))
            domain_obj = PDDLDomain(**domain_json)
        except Exception as e:
            print("Errore nel parsing del dominio:", e)
            print("Contenuto ricevuto:", domain_raw.content)
            break

        domain_str = render_pddl_domain(domain_obj)

        # Generazione problema
        problem_raw = llm.invoke(problem_prompt.format_messages(narrative=narrative_input, domain=domain_str))
        if not isinstance(problem_raw, AIMessage):
            print("Errore: risposta non valida dal modello per il problema.")
            break

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
            break

        # Aggiornamento fatti
        if first_iteration:
            current_facts = set(problem_obj.init)
            first_iteration = False
            print("\n📋 Stato iniziale:", current_facts)
        else:
            new_facts = set(problem_obj.init)
            added = new_facts - current_facts
            removed = current_facts - new_facts
            print("\n➕ Fatti aggiunti:", added)
            print("\n➖ Fatti rimossi:", removed)
            current_facts = new_facts

        problem_str = render_pddl_problem(problem_obj)

        print("\n🧙‍♂️ Dominio PDDL:\n", domain_str)
        print("\n📜 Problema PDDL:\n", problem_str)

        # Scrittura file
        with open("domain.pddl", "w", encoding="utf-8") as f:
            f.write(domain_str)
        with open("problem.pddl", "w", encoding="utf-8") as f:
            f.write(problem_str)

        # Esecuzione planner
        print("\n🚀 Avvio Fast Downward...\n")
        if not run_fast_downward("domain.pddl", "problem.pddl"):
            print("❌ Impossibile proseguire: nessun piano valido.")
            print("Controlla fast_downward_log.txt per dettagli.")
            break

        # ReflectionAgent
        choice, executed_action, status = reflectionAgent(domain_obj, current_facts)
        print("\n🎯 Scelta del giocatore:", choice)

        if not status:
            print("\n🏁", choice)
            break

        # Applica gli effetti dell'azione scelta
        current_facts = apply_action_effects(executed_action, domain_obj, current_facts)
        print("\n🔄 Stato aggiornato:", current_facts)

        # Rimuovi l'azione eseguita dal piano
        if os.path.exists("sas_plan"):
            with open("sas_plan", "r") as f:
                lines = f.readlines()
            with open("sas_plan", "w") as f:
                f.writelines(lines[1:])  # Rimuove la prima azione

        # Aggiornamento narrativa
        effects_str = "\n".join(current_facts)
        narrative_messages = narrative_prompt.format_messages(
            narrative=narrative_input,
            choice=choice,
            domain=domain_str,
            problem=problem_str,
            effects=effects_str
        )
        response = llm.invoke(narrative_messages)
        narrative_input = response.content.strip()
        print("\n📖 Nuova narrativa:\n", narrative_input)

        # Salva narrativa aggiornata
        with open("lore_updated.txt", "w", encoding="utf-8") as f:
            f.write(narrative_input)

        # Aggiorna il problema PDDL con il nuovo stato
        problem_obj.init = list(current_facts)
        problem_str = render_pddl_problem(problem_obj)
        with open("problem.pddl", "w", encoding="utf-8") as f:
            f.write(problem_str)

if __name__ == "__main__":
    main()
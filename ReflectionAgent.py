from tokenize import String
from typing import Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv 

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)


def reflectionAgent() -> Tuple[str, bool]:
    try:
        with open("sas_plan", "r", encoding="utf-8") as file:
            lines = file.readlines()
            sas_plan_text = "".join(lines)
            sas_plan_actions = [line.strip() for line in lines if line.strip() and not line.startswith(";")]
    except FileNotFoundError:
        print("Error: The file 'sas_plan' was not found.")
        exit(1)

    if not sas_plan_actions:
        return "You have lost.", False#gestione a llm
    elif len(sas_plan_actions) == 1:
        return "You have won.", False

    next_action = sas_plan_actions[0]  # La prossima azione nel piano

    # Prompt: suggerisce la prossima azione nel piano e anche alternative inventate
    problem_prompt = ChatPromptTemplate.from_messages([
        ("system", """
            You are a smart reflection agent in a game where the world is driven by a sequence of PDDL plan actions.

            You are given:
            - A list of grounded actions from a valid PDDL plan.
            - The first action in the plan represents what the player should do next.
            - Your role is to offer that action as the main choice, and also invent 1–2 **alternative actions** that the player *could* take instead (imaginative but realistic within a PDDL world).

            ⚠️ Rules:
            - Do not list all the actions from the plan — only the next one and your invented suggestions.
            - Invented actions must sound plausible in a fantasy/PDDL environment.
            - Always end your reply with: “Which action do you want to perform?”

            Output format:
            Here are your options:
            1 (real action) → explanation
            2 (invented action) → explanation
            3 (optional invented action) → explanation

            Which action do you want to perform?
        """),
        ("user", f"The next action in the plan is:\n{next_action}")
    ])

    reflection = llm.invoke(problem_prompt.format_messages())
    print(reflection.content.strip())
    
    choice = input("Fai una scelta ")

    options = [line.strip() for line in reflection.content.strip().split('\n') if line.strip().startswith(str(choice.strip()))]

    if not options:
        print("Scelta non valida.")
        return

    selected_action = options[0]
    return selected_action, True



    

# main.py

import logging
import os

from agents.agent_factory import AgentFactory
from utils.result_formatter import format_results

import google.generativeai as genai

# Configure logging with rotation
from logging.handlers import RotatingFileHandler

log_directory = 'logs'
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, 'system.log')

handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)  # 5MB per file, 5 backups
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Configure the Gemini API
genai.configure(api_key=os.getenv("GENIE_API_KEY"))  # Ensure API key is set as an environment variable

def process_user_problem(user_problem):
    """
    Processes the user problem through a sequence of agents.
    Yields solutions from each agent for streaming.
    """
    logger.info("User problem received: %s", user_problem)

    agent_factory = AgentFactory()
    agents = agent_factory.create_agents()  # Returns the list of agents in sequence

    previous_solution = None
    all_solutions = []

    for idx, agent in enumerate(agents, start=1):
        agent_name = f"Agent{idx}"
        solution = agent.get_solution(user_problem, previous_solution)
        all_solutions.append((agent_name, solution))
        logger.info("Agent %s provided solution: %s", agent_name, solution)
        yield agent_name, solution  # Yield each step for streaming
        previous_solution = solution  # Pass the current solution to the next agent

    final_solution = previous_solution
    formatted_result = format_results(all_solutions, final_solution)
    logger.info("Final formatted result: %s", formatted_result)
    yield "final", formatted_result  # Yield the final formatted result
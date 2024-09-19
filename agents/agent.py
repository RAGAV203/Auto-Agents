# agents/agent.py

import logging
import google.generativeai as genai
import re
import json
import time

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, name, role_prompt):
        self.name = name
        self.role_prompt = role_prompt

    def get_solution(self, problem, previous_solution=None):
        messages = []

        # System prompt
        messages.append({"role": "system", "content": self.role_prompt})

        # User prompt
        if previous_solution:
            messages.append({"role": "user", "content": f"Problem:\n{problem}\n\nPrevious Solution:\n{previous_solution}\n\nPlease proceed with your analysis."})
        else:
            messages.append({"role": "user", "content": f"Problem:\n{problem}\n\nPlease provide your solution."})

        # Assistant initial acknowledgment
        messages.append({"role": "assistant", "content": "Understood. I will begin my reasoning steps now."})

        steps = []
        step_count = 1

        for _ in range(4):  # Assuming 4 agents; adjust as needed
            solution = self.make_api_call_with_retry(messages)
            if not solution:
                logger.error(f"{self.name} did not return a valid solution after retries.")
                break  # Exit the loop if no valid solution is obtained

            step_data = self.parse_response(solution)

            if not step_data:
                logger.error(f"{self.name} failed to parse response: {solution}")
                break  # Exit the loop on parsing failure

            # Log the response for debugging
            logger.info(f"{self.name} received response: {solution}")
            logger.info(f"Parsed step data: {step_data}")

            # Store the step and content
            steps.append((f"Step {step_count}: {step_data['title']}", step_data['content']))

            messages.append({"role": "assistant", "content": solution})

            if step_data['next_action'] == 'final_answer':
                break

            step_count += 1

        # Compile the agent's solution
        agent_solution = self.compile_solution(steps)
        logger.info(f"{self.name} completed their solution with steps: {steps}")
        return agent_solution

    def build_prompt(self, messages):
        # Combine messages into a single prompt
        prompt = ''
        for message in messages:
            role = message['role']
            content = message['content']
            if role == 'system':
                prompt += f"System: {content}\n\n"
            elif role == 'user':
                prompt += f"User: {content}\n\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n\n"
        return prompt

    def make_api_call_with_retry(self, messages, max_retries=3, delay=10):
        """
        Makes an API call to the Generative AI model with retry logic.
        Retries the API call up to `max_retries` times if an error occurs.
        Waits for `delay` seconds between retries.

        Returns:
            The response text if successful, else an empty string.
        """
        prompt = self.build_prompt(messages)
        attempt = 0

        while attempt < max_retries:
            try:
                model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash-exp-0827',
                    tools='code_execution'
                )
                response = model.generate_content(prompt)
                if hasattr(response, 'text') and response.text:
                    return response.text
                else:
                    logger.warning(f"{self.name} received an empty response.")
            except Exception as e:
                attempt += 1
                logger.error(f"Error during API call for {self.name} (Attempt {attempt}/{max_retries}): {str(e)}")
                if attempt < max_retries:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"{self.name} failed to get a valid response after {max_retries} attempts.")
        return ""

    

    def parse_response(self, response_text):
        if not isinstance(response_text, str):
            logger.error(f"{self.name} received a non-string response: {response_text}")
            return None

        try:
            # Sanitize response text by removing unwanted control characters
            sanitized_text = re.sub(r'[^\x20-\x7E]', '', response_text)  # Remove non-printable ASCII characters

            # Remove possible trailing characters that might be causing issues
            sanitized_text = sanitized_text.rstrip(' \t\n\r')

            # Extract JSON from the response
            json_pattern = r"```json\s*(\{[\s\S]*?\})\s*```"
            match = re.search(json_pattern, sanitized_text)
            if match:
                response_json = match.group(1)
                return json.loads(response_json)
            else:
                # Attempt to parse the entire sanitized response as JSON
                try:
                    return json.loads(sanitized_text)
                except json.JSONDecodeError as e:
                    # Log and attempt to extract JSON manually
                    logger.error(f"{self.name} error parsing JSON response: {str(e)} - Sanitized Response Text: {sanitized_text}")
                    return self.extract_and_parse_fallback_json(sanitized_text)
        except Exception as e:
            logger.error(f"{self.name} unexpected error parsing response: {str(e)}")
            return None

    def extract_and_parse_fallback_json(self, text):
        # Attempt to manually clean and extract JSON content
        try:
            # Basic attempt to extract JSON-like text from the response
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                potential_json = text[start:end+1]
                return json.loads(potential_json)
        except json.JSONDecodeError as e:
            logger.error(f"{self.name} fallback JSON parsing failed: {str(e)} - Text: {text}")
        return None



    def compile_solution(self, steps):
        solution_text = ""
        for title, content in steps:
            solution_text += f"### {title}\n{content}\n\n"
        return solution_text

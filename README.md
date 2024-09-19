# Auto-Agent: Replicating Chain of Thought Reasoning

## Project Overview

This project acts as a **proof of concept** aimed at replicating the reasoning capabilities of OpenAI's newly released O1 model. The O1 model leverages chain-of-thought prompting and reinforcement learning to enhance its problem-solving abilities through iterative reasoning. Our goal is to mimic this behavior using alternative models.

In this implementation, we utilize a sequential agent-based system powered by the Gemini API (or any model with function-calling capabilities). This system is designed to generate solutions for coding-related problems and iteratively refine these solutions through chain-of-thought reasoning and reflective techniques. The Gemini API, with its robust code execution capabilities, is particularly well-suited for this project. Although it is compatible with Gemini Flash, we recommend using the Pro version to mitigate issues with external package dependencies, as the Pro version typically aligns with Python's standard library.

### Flask Application

To facilitate user interaction with the Auto-Agent system, we implement a Flask application. This web-based interface allows users to submit coding problems and receive refined solutions in real time. The Flask app manages user requests and orchestrates the interaction between the user and the Gemini API, providing a seamless experience. By leveraging Flask's lightweight framework, we can efficiently handle multiple requests while maintaining a responsive interface, making the project accessible and user-friendly.
## Flask Application Implementation

### 1. Setting Up the Environment Variable

To utilize the Gemini API, you need to configure an environment variable for your Google API key. You can do this by executing the following command in your terminal:

```bash
export GENIE_API_KEY=<your_api_key>
```

### 2. Creating a Conda Virtual Environment

It is advisable to work within a Conda environment for this project to manage dependencies effectively. To create and activate a new Conda environment, run:

```bash
conda create -n auto-agent python=3.10
conda activate auto-agent
```

### 3. Installing Required Dependencies

Next, install the necessary dependencies using pip. Make sure you have a `requirements.txt` file that lists all the required packages. You can install them by running:

```bash
pip install -r requirements.txt
```

### 4. Running the Flask Application

Once the environment is set up and the dependencies are installed, you can start the Flask application by executing the following command:

```bash
python app.py
```

This command will initiate the Flask server, allowing you to interact with the Auto-Agent system through a web interface. The application is designed to facilitate coding problem-solving by leveraging the capabilities of the Gemini API to generate and refine solutions iteratively.

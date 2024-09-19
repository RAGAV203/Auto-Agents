# app.py

from flask import Flask, render_template, request, Response, stream_with_context
import time
import os
import bleach  # For enhanced sanitization

from main import process_user_problem

app = Flask(__name__)

# Path to the log file
LOG_FILE_PATH = 'logs/system.log'

def tail_log():
    """
    Generator function that yields new log lines as they are written.
    """
    with open(LOG_FILE_PATH, 'r') as f:
        # Go to the end of the file
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                # Sanitize log lines to prevent HTML injection
                escaped_line = bleach.clean(line, tags=[], attributes={}, styles=[], strip=True)
                yield f"data: {escaped_line}<br/>\n\n"
            else:
                time.sleep(1)

def generate_output(user_problem):
    """
    Generator function that processes the user problem and yields output.
    """
    for agent_name, solution in process_user_problem(user_problem):
        if agent_name != "final":
            # Properly format agent output with line breaks and indentation
            formatted_step = f"<strong>{agent_name}:"+"</strong> "+ solution.replace('\n', '<br/>')
            yield f"data: {formatted_step}"+"<br/>\n\n"
        else:
            start_marker = "=== Final Synthesized Solution ==="
            start_index = solution.find(start_marker)
            
            if start_index != -1:
                # Extract the part of the finalSolution after the marker
                final_content = solution[start_index + len(start_marker):].strip()
            else:
                final_content = "No final solution found."
            #print(final_content)    
            yield "data: "+final_content+"\n\n"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_process', methods=['POST'])
def start_process():
    user_input = request.form.get('user_input')
    if not user_input:
        return Response("No input provided.", status=400)
    # Sanitize input to prevent injection
    safe_input = bleach.clean(user_input.strip(), tags=[], attributes={}, styles=[], strip=True)
    return Response(stream_with_context(generate_output(safe_input)), mimetype='text/event-stream')

@app.route('/logs')
def logs():
    return Response(stream_with_context(tail_log()), mimetype='text/event-stream')

if __name__ == '__main__':
    # Ensure the log directory exists
    os.makedirs('logs', exist_ok=True)
    # Start the Flask app
    app.run(debug=True, threaded=True)

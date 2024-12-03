from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os
import sys
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory to store Python files temporarily
FILES_DIR = './files'
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

# Dynamically determine the Python executable
python_executable = sys.executable

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code', '')
    file_name = data.get('fileName', 'main.py')

    if not code:
        return jsonify({"error": "No code provided"}), 400

    # Save the code to a Python file
    file_path = os.path.join(FILES_DIR, file_name)
    try:
        with open(file_path, 'w') as f:
            f.write(code)
    except IOError as e:
        logger.error(f"Failed to write to file {file_path}: {e}")
        return jsonify({"error": "Failed to save the code to a file."}), 500

    # Run the Python file
    try:
        process = subprocess.run(
            [python_executable, file_path],
            capture_output=True, text=True, check=True
        )
        return jsonify({"output": process.stdout})
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running code: {e.stderr}")
        return jsonify({"error": e.stderr}), 400

@app.route('/install', methods=['POST'])
def install_module():
    data = request.get_json()
    module_name = data.get('module', '')

    if not module_name:
        return jsonify({"error": "No module name provided"}), 400

    # Install the module using pip
    try:
        process = subprocess.run(
            [python_executable, '-m', 'pip', 'install', module_name],
            capture_output=True, text=True, check=True
        )
        logger.info(f"Successfully installed module {module_name}")
        return jsonify({"output": process.stdout})
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing module {module_name}: {e.stderr}")
        return jsonify({"error": e.stderr}), 400

if __name__ == '__main__':
    app.run(debug=True)

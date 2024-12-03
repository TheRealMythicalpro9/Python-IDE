from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os

app = Flask(__name__)

# Directory to store Python files temporarily
FILES_DIR = './files'
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code', '')
    file_name = data.get('fileName', 'main.py')

    # Save the code to a Python file
    file_path = os.path.join(FILES_DIR, file_name)
    with open(file_path, 'w') as f:
        f.write(code)

    # Run the Python file
    try:
        process = subprocess.run(
            ['python', file_path],
            capture_output=True, text=True, check=True
        )
        return jsonify({"output": process.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr})

@app.route('/install', methods=['POST'])
def install_module():
    data = request.get_json()
    module_name = data.get('module', '')

    if not module_name:
        return jsonify({"error": "No module name provided"}), 400

    try:
        process = subprocess.run(
            ['pip', 'install', module_name],
            capture_output=True, text=True, check=True
        )
        return jsonify({"output": process.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr})

if __name__ == '__main__':
    app.run(debug=True)

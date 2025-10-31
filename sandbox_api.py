from flask import Flask, request, jsonify
import docker
import tempfile
import os

app = Flask(__name__)
client = docker.from_env()

# 🔒 Token rahasia sederhana
SANDBOX_TOKEN = "9da29573101a49f21ec1dccf724430dc7b8cec3ee49e1e67bf8249ef3f80214c"


@app.route('/run', methods=['POST'])
def run_code():
    # Cek token autentikasi
    token = request.headers.get("Authorization")
    if token != f"Bearer {SANDBOX_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    code = data.get("code", "")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(code.encode('utf-8'))
        temp_file_path = temp_file.name

    try:
        result = client.containers.run(
            "python:3.11-slim",
            command=["python", f"/code/{os.path.basename(temp_file_path)}"],
            volumes={os.path.dirname(temp_file_path): {
                'bind': '/code', 'mode': 'ro'}},
            remove=True,
            stderr=True,
            mem_limit="128m",
            network_disabled=True
        )
        output = result.decode('utf-8')
    except docker.errors.ContainerError as e:
        output = e.stderr.decode('utf-8') if e.stderr else str(e)
    except Exception as e:
        output = f"Error: {e}"
    finally:
        os.remove(temp_file_path)

    return jsonify({"output": output})


if __name__ == '__main__':
    print("🚀 Sandbox API running on http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001)

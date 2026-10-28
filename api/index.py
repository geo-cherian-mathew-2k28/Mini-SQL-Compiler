import os
import sys

# Ensure root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, send_from_directory
from src.compiler import MiniSQLCompiler
from src.semantic.schema import get_default_catalog

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "web"))

catalog = get_default_catalog()
compiler = MiniSQLCompiler(catalog)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


@app.route("/api/schema", methods=["GET"])
def get_schema():
    return jsonify(catalog.to_dict())


@app.route("/api/compile", methods=["POST"])
def compile_query():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    result = compiler.compile(query)
    return jsonify(result.to_dict())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

import json
import os
import sqlite3
import subprocess
import time
import threading
from pathlib import Path
from flask import Flask, jsonify, render_template, request, send_file
import requests

from logic_controller import LogicController
from node_mesh import NodeRegistry, TaskDispatcher

# Configuration
ROOT = Path(__file__).parent
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3")  # Default to small model
DB_PATH = ROOT / "nineten_v3.db"

app = Flask(__name__)

# Global State
STOP_FLAG = threading.Event()
logic = LogicController()
registry = NodeRegistry()

def local_llama_call(task):
    prompt = task.get("prompt", "")
    return call_ollama(prompt)

dispatcher = TaskDispatcher(registry, local_fallback=local_llama_call)

# Database Setup
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instance_id TEXT NOT NULL,
            persona TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            ts REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def db_append(instance_id, persona, role, content):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO conversation_log (instance_id, persona, role, content, ts) VALUES (?, ?, ?, ?, ?)",
        (instance_id, persona, role, content, time.time()),
    )
    conn.commit()
    conn.close()

def db_load_history(instance_id, persona, limit=10):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT role, content FROM conversation_log WHERE instance_id = ? AND persona = ? ORDER BY id DESC LIMIT ?",
        (instance_id, persona, limit),
    ).fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in reversed(rows)]

init_db()

# Core Logic
def call_ollama(prompt, system_prompt=""):
    if STOP_FLAG.is_set():
        return "[STOPPED]"
    
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "stop": ["User:", "System:", "Nine:", "Ten:"]
            }
        }
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        return f"[ERROR] Ollama connection failed: {e}"

def synthesize_voice(text):
    """Uses Termux TTS if available."""
    try:
        subprocess.run(["termux-tts-speak", text], timeout=15)
    except:
        pass

# Routes
@app.route("/api/chat", methods=["POST"])
def api_chat():
    if STOP_FLAG.is_set():
        return jsonify({"error": "System is in Force Stop mode. Reset to continue."}), 403
        
    data = request.json
    instance_id = data.get("instance_id", "default")
    persona = data.get("persona", "nine")
    message = data.get("message", "")
    
    history = db_load_history(instance_id, persona)
    
    # Logic Pass
    cleaned_msg, is_valid = logic.validate_response(message, []) # Validate input if needed
    
    prompt = f"Context: {json.dumps(history)}\nUser: {message}\nAssistant:"
    system = f"You are {persona.upper()} in the NINETEN system. Be logical and concise."
    
    reply = call_ollama(prompt, system)
    
    # Logic Pass on Output
    final_reply, is_valid = logic.validate_response(reply, history)
    
    if is_valid:
        db_append(instance_id, persona, "User", message)
        db_append(instance_id, persona, persona, final_reply)
        synthesize_voice(final_reply)
        
    return jsonify({"reply": final_reply, "valid": is_valid})

@app.route("/api/stop", methods=["POST"])
def force_stop():
    STOP_FLAG.set()
    return jsonify({"status": "FORCE STOP ACTIVATED"})

@app.route("/api/reset_stop", methods=["POST"])
def reset_stop():
    STOP_FLAG.clear()
    return jsonify({"status": "System resumed"})

@app.route("/api/mesh/register", methods=["POST"])
def register_node():
    data = request.json
    node_id = registry.register(data.get("url"), data.get("name", "Node"))
    return jsonify({"node_id": node_id, "status": "registered"})

@app.route("/api/mesh/state", methods=["GET"])
def mesh_state():
    return jsonify(registry.get_state())

@app.route("/")
def health():
    return "NINETEN v3.0 Core Active"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

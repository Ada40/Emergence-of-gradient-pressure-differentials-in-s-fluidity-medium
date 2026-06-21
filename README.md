# NINETEN v3.0: Dual-Brain Quantum Architecture

Extended architecture for Adam Lee Hatchett's NINETEN system. Optimized for Termux, Ollama, and distributed computation.

## Features
- **Ollama Backend**: Flexible model support (Phi-3, Llama-3, etc.).
- **Logic Controller**: Advanced repetition detection and garbage filtering to prevent looping.
- **Node Mesh**: Distributed computation allowing multiple phones/devices to share LLM tasks.
- **Force Stop**: Immediate global kill switch for all AI processes.
- **Termux Integration**: Native Android TTS support.

## Installation (Termux)
1. Install Ollama and start the server.
2. Install Python dependencies: `pip install flask requests`
3. Run the server: `python server.py`

## Usage
- Access the local API at `http://localhost:5000`
- Use `/api/stop` to immediately halt operations.
- Use `/api/mesh/register` to connect other devices to your compute mesh.

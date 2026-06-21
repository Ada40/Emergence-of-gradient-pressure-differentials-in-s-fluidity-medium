# NINETEN v3.0: Dual-Brain Quantum Architecture (Extended)

## Overview
NINETEN v3.0 is an evolution of the dual-brain architecture, optimized for mobile deployment (Termux), distributed computation, and robust logical reasoning. It integrates Ollama for flexible model management and a peer-to-peer node mesh for shared computation.

## Key Components

### 1. Adaptive Chat Engine
- **Ollama Integration**: Native support for Ollama API, allowing easy swapping of models (e.g., Llama3, Phi-3, Mistral).
- **Logic Controller**: A middle layer that monitors output for:
    - **Repetition**: N-gram based loop detection.
    - **Garbage Filtering**: Regex-based removal of common LLM artifacts or "hallucinated" system prompts.
    - **Reflection**: An optional secondary pass where the model evaluates its own response for coherence.

### 2. Distributed Node Mesh (Emergence Layer)
- **Peer Registration**: Any device running the NINETEN server can register as a "Compute Node."
- **Task Dispatcher**: Distributes batch prompts across available nodes.
- **Computation Value**: Nodes contribute their local LLM inference capacity to the mesh, enabling faster batch processing.

### 3. Immediate Force Stop
- **Global Kill Switch**: A thread-safe flag that interrupts long-running bridge sessions or batch tasks.
- **Endpoint**: `/api/stop` to trigger the shutdown of current active processes.

### 4. Adaptability & Multi-Instance Support
- **Dynamic Personas**: Defined in `config.json` rather than hardcoded.
- **Architecture Templates**: Support for "Variations" of the same core logic (e.g., Research mode, Creative mode, Math mode).

### 5. Mobile Optimization (Termux)
- **SQLite Memory**: Persistent conversation history.
- **Android TTS**: Integration with `termux-tts-speak` for voice output.
- **Low-Memory Mode**: Optimized context window management for 8GB devices.

## API Specification (New/Updated)
- `POST /api/register`: Register a new node to the mesh.
- `POST /api/stop`: Immediate force stop of all active logic.
- `POST /api/task/dispatch`: Send tasks to the mesh.
- `GET /api/config`: Retrieve current instance configuration.

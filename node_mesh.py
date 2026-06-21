import time
import threading
import requests
import uuid
from typing import List, Dict, Any, Optional

class Node:
    def __init__(self, url: str, name: str = "Anonymous Node"):
        self.id = str(uuid.uuid4())[:8]
        self.url = url
        self.name = name
        self.last_seen = time.time()
        self.active = True

class NodeRegistry:
    """Manages the list of active compute nodes in the mesh."""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self._lock = threading.Lock()

    def register(self, url: str, name: str) -> str:
        with self._lock:
            # Check if URL already exists
            for node in self.nodes.values():
                if node.url == url:
                    node.last_seen = time.time()
                    node.active = True
                    return node.id
            
            new_node = Node(url, name)
            self.nodes[new_node.id] = new_node
            return new_node.id

    def get_active_nodes(self) -> List[Node]:
        with self._lock:
            # Clean up stale nodes (inactive for > 5 mins)
            now = time.time()
            for nid in list(self.nodes.keys()):
                if now - self.nodes[nid].last_seen > 300:
                    self.nodes[nid].active = False
            
            return [n for n in self.nodes.values() if n.active]

    def get_state(self) -> Dict:
        active = self.get_active_nodes()
        return {
            "total_nodes": len(self.nodes),
            "active_nodes": len(active),
            "nodes": [{"id": n.id, "name": n.name, "url": n.url} for n in active]
        }

class TaskDispatcher:
    """Distributes LLM tasks across the node mesh."""
    def __init__(self, registry: NodeRegistry, local_fallback: Any):
        self.registry = registry
        self.local_fallback = local_fallback

    def dispatch_tasks(self, tasks: List[Dict[str, Any]], timeout: int = 30) -> List[Dict[str, Any]]:
        results = []
        nodes = self.registry.get_active_nodes()
        
        if not nodes:
            # No nodes available, run everything locally
            for task in tasks:
                results.append({"task": task, "result": self.local_fallback(task), "node": "local"})
            return results

        # Simple round-robin or parallel dispatch could be implemented here
        # For now, we'll try to use nodes and fallback to local
        threads = []
        
        def run_task(task, node_idx):
            node = nodes[node_idx % len(nodes)]
            try:
                resp = requests.post(
                    f"{node.url}/api/chat_internal", 
                    json=task, 
                    timeout=timeout
                )
                if resp.status_code == 200:
                    results.append({"task": task, "result": resp.json(), "node": node.name})
                else:
                    results.append({"task": task, "result": self.local_fallback(task), "node": "local-fallback"})
            except:
                results.append({"task": task, "result": self.local_fallback(task), "node": "local-fallback"})

        for i, task in enumerate(tasks):
            t = threading.Thread(target=run_task, args=(task, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return results

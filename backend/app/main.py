from fastapi import FastAPI
from pydantic import BaseModel, Field, validator
from typing import Set
import networkx as nx
from networkx.readwrite import json_graph

app = FastAPI()

class TopologyRequest(BaseModel):
    num_nodes: int = Field(..., gt=2, description="Total number of nodes in the topology (must be greater than 2)")
    # Renamed skips to permutations. Constraint >= 0
    permutations: Set[int] = Field(..., description="Set of unique permutation values (each >= 0). p=0 connects to next node, p=1 skips 1 node.")

    @validator('permutations')
    def check_permutations_non_negative(cls, v):
        if any(p < 0 for p in v):
            raise ValueError('Permutation values must be non-negative.')
        return v

class TopologyResponse(BaseModel):
    graph_json: dict # Node-link data
    config: TopologyRequest # The configuration used
    topology_type: str = "ring" # Added topology type field

@app.get("/")
def read_root():
    return {"message": "Network Topology Generator Backend"}

@app.post("/generate_topology", response_model=TopologyResponse)
def generate_topology(request: TopologyRequest):
    """
    Generates a stacked ring topology based on a fixed number of nodes
    and a list of unique permutation values.
    Permutation 'p' connects node 'i' to node '(i + p + 1) % n'.
    """
    G = nx.Graph()
    n = request.num_nodes

    # Add all necessary nodes first
    G.add_nodes_from(range(n))

    # Add edges for each permutation configuration
    # Use 'p' for permutation value, consistent with user definition
    for p in request.permutations:
        # Add edges for the ring with permutation p
        for i in range(n):
            # Permutation p=0 -> target=(i+1)%n
            # Permutation p=1 -> target=(i+2)%n
            source_node = i
            target_node = (i + p + 1) % n
            # Avoid self-loops (important for n=1 or p+1=multiple of n)
            # Condition num_nodes > 2 already prevents n=1, n=2 edge cases mostly.
            # Example n=3, p=2 -> target=(i+3)%3=i -> self-loop. Prevent this.
            if source_node != target_node:
                 G.add_edge(source_node, target_node)

    # Serialize graph to JSON node-link format
    graph_data = json_graph.node_link_data(G)

    # Include the topology type in the response
    return TopologyResponse(graph_json=graph_data, config=request, topology_type="ring")

# Example of how to run the app (optional, for local testing)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000) 
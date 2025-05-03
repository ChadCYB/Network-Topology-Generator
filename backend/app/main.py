from fastapi import FastAPI
from pydantic import BaseModel, Field, validator
from typing import Set, List, Optional
import networkx as nx
from networkx.readwrite import json_graph

app = FastAPI()

class EdgeAttr(BaseModel):
    bandwidth: str = "400Gbps"
    delay: str = "0.0005ms"
    error_rate: str = "0"

class TopologyRequest(BaseModel):
    num_nodes: int = Field(..., gt=2, description="Total number of nodes in the topology (must be greater than 2)")
    permutations: Set[int] = Field(..., description="Set of unique permutation values (each >= 0). p=0 connects to next node, p=1 skips 1 node.")
    bandwidth: Optional[str] = Field("400Gbps", description="Bandwidth for each link.")
    delay: Optional[str] = Field("0.0005ms", description="Delay for each link.")
    error_rate: Optional[str] = Field("0", description="Error rate for each link.")

    @validator('permutations')
    def check_permutations_non_negative(cls, v):
        if any(p < 0 for p in v):
            raise ValueError('Permutation values must be non-negative.')
        return v

class TopologyResponse(BaseModel):
    graph_json: dict # Node-link data
    config: TopologyRequest # The configuration used
    topology_type: str = "ring" # Added topology type field
    edge_list: List[List] # For export: [source, target, bandwidth, delay, error_rate]

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
    G = nx.DiGraph()
    n = request.num_nodes

    # Add all necessary nodes first
    G.add_nodes_from(range(n))

    edge_list = []
    for p in request.permutations:
        for i in range(n):
            source_node = i
            target_node = (i + p + 1) % n
            if source_node != target_node:
                G.add_edge(
                    source_node, target_node,
                    bandwidth=request.bandwidth,
                    delay=request.delay,
                    error_rate=request.error_rate
                )
                edge_list.append([
                    source_node, target_node,
                    request.bandwidth, request.delay, request.error_rate
                ])

    graph_data = json_graph.node_link_data(G)

    return TopologyResponse(
        graph_json=graph_data,
        config=request,
        topology_type="ring",
        edge_list=edge_list
    )

# Example of how to run the app (optional, for local testing)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000) 
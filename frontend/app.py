import streamlit as st
import requests
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import json
import io
import os # Added for path manipulation

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000/generate_topology"
# Define project root relative to this script's location
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Helper Functions ---
def draw_graph(graph_data):
    """Draws the network graph using NetworkX and Matplotlib."""
    if not graph_data:
        st.info("No graph data to display.")
        return None
    try:
        G = json_graph.node_link_graph(graph_data)
        # Use the slider value for figure size directly here if passed
        # Default figure size set via slider default value later
        fig, ax = plt.subplots() # Size will be set before display
        try:
            pos = nx.kamada_kawai_layout(G)
        except nx.NetworkXError:
            pos = nx.spring_layout(G, seed=42)
        except ImportError:
            st.warning("Kamada-Kawai layout requires SciPy. Using Spring layout.")
            pos = nx.spring_layout(G, seed=42)

        nx.draw(G, pos, ax=ax, with_labels=True, node_color='lightblue', node_size=500, edge_color='gray', font_size=10)
        ax.set_title("Generated Network Topology")
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    except Exception as e:
        st.error(f"Error drawing graph: {e}")
        return None

# --- Backend Interaction ---
def generate_and_update_topology():
    """Calls the backend to generate topology and updates session state."""
    if st.session_state.num_nodes is None or not st.session_state.permutation_configs:
        st.warning("Cannot generate topology without nodes and at least one permutation.")
        return False

    payload = {
        "num_nodes": st.session_state.num_nodes,
        "permutations": list(st.session_state.permutation_configs)
    }
    try:
        response = requests.post(BACKEND_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        # Store the graph and the full response data separately
        st.session_state.generated_topology = data.get("graph_json")
        # Store the whole response dict to include topology_type later
        st.session_state.last_topology_response = data
        st.success("Topology generated successfully!")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {e}")
        st.session_state.generated_topology = None
        st.session_state.last_topology_response = None # Clear response on error
        return False
    except Exception as e:
        st.error(f"An error occurred during generation: {e}")
        st.session_state.generated_topology = None
        st.session_state.last_topology_response = None # Clear response on error
        return False

# --- Initialize Session State ---
if 'num_nodes' not in st.session_state:
    st.session_state.num_nodes = None
if 'permutation_configs' not in st.session_state:
    st.session_state.permutation_configs = set()
if 'generated_topology' not in st.session_state:
    st.session_state.generated_topology = None
# Changed from last_config_request to last_topology_response
if 'last_topology_response' not in st.session_state:
    st.session_state.last_topology_response = None

def reset_config():
    """Resets the configuration in the session state."""
    st.session_state.num_nodes = None
    st.session_state.permutation_configs = set()
    st.session_state.generated_topology = None
    st.session_state.last_topology_response = None # Updated state variable
    st.success("Configuration reset.")

# --- UI ---
st.set_page_config(layout="wide")
st.title("Network Topology Generator")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Configuration")

    if st.button("Reset Configuration"):
        reset_config()
        st.rerun()

    # 1. Configure Number of Nodes
    if st.session_state.num_nodes is None:
        with st.form("node_config_form"):
            st.subheader("Step 1: Set Number of Nodes")
            num_nodes_input = st.number_input("Number of Nodes", min_value=3, value=5, step=1,
                                              help="Set the total number of nodes for the topology. This cannot be changed later without resetting.")
            submitted_nodes = st.form_submit_button("Set Nodes")
            if submitted_nodes:
                st.session_state.num_nodes = num_nodes_input
                st.success(f"Number of nodes set to {st.session_state.num_nodes}.")
                st.rerun()
    else:
        st.subheader(f"Step 1: Number of Nodes: {st.session_state.num_nodes}")
        st.caption("To change the number of nodes, reset the configuration.")

        # 2. Add Permutations
        st.subheader("Step 2: Add Permutations")
        # Calculate maximum permutation value based on number of nodes
        # For n nodes, we only need permutations from 0 to (n/2 - 1)
        # because p and (n-p-2) create the same graph
        max_perm_value = (st.session_state.num_nodes // 2) - 1
        
        with st.form("add_permutation_form", clear_on_submit=True):
            # Add permutation input with dynamic max value
            st.number_input(
                "Permutation Value",
                min_value=0,
                max_value=max_perm_value,
                value=0,
                key="permutation",
                help=f"Enter a permutation value between 0 and {max_perm_value}. p=0 connects to next node, p=1 skips 1 node, etc."
            )
            submitted_permutation = st.form_submit_button("Add Permutation")
            if submitted_permutation:
                if st.session_state.permutation not in st.session_state.permutation_configs:
                    st.session_state.permutation_configs.add(st.session_state.permutation)
                    st.success(f"Added permutation: {st.session_state.permutation}")
                    if generate_and_update_topology(): # This function now updates last_topology_response
                        st.rerun()
                else:
                    st.warning(f"Permutation {st.session_state.permutation} already exists.")

        # Display current permutations
        st.subheader("Current Permutations")
        if not st.session_state.permutation_configs:
            st.info("No permutations added yet.")
        else:
            perms_to_remove = set()
            # Display sorted list for consistency
            sorted_perms = sorted(list(st.session_state.permutation_configs))
            for p_val in sorted_perms:
                col_perm, col_btn = st.columns([4, 1])
                with col_perm:
                     st.markdown(f"- Permutation: **{p_val}**")
                with col_btn:
                     if st.button(f"Delete", key=f"del_{p_val}"):
                         perms_to_remove.add(p_val)

            if perms_to_remove:
                st.session_state.permutation_configs -= perms_to_remove
                if st.session_state.permutation_configs:
                     if generate_and_update_topology(): # This function now updates last_topology_response
                          st.rerun()
                     else:
                          st.rerun()
                else:
                     st.session_state.generated_topology = None
                     st.session_state.last_topology_response = None # Update state variable
                     st.rerun()

        # 3. Explicit Generate Topology Button (Optional, as it generates on add/delete)
        # Can still be useful if backend connection fails initially
        if st.session_state.num_nodes is not None and st.session_state.permutation_configs:
             # type="primary" might make it blue, not easily green without CSS hacks
             if st.button("Regenerate Topology"):
                 if generate_and_update_topology(): # This function now updates last_topology_response
                      st.rerun()
        elif st.session_state.num_nodes is not None:
             st.warning("Add at least one permutation to generate the topology.")

with col2:
    st.header("Topology Visualization")
    # Set default slider value to 6
    fig_size = st.slider("Adjust Plot Size", min_value=4, max_value=20, value=6, step=1)
    fig = draw_graph(st.session_state.generated_topology)
    if fig:
        fig.set_size_inches(fig_size, fig_size)
        # Add use_container_width=True
        st.pyplot(fig, use_container_width=True)
    # Use last_topology_response to check if generation was attempted
    elif st.session_state.last_topology_response:
         st.warning("Could not display topology. Check configuration or backend connection.")
    else:
        st.info("Configure nodes and permutations to visualize the topology.")

    # --- Export Configuration ---
    # Use last_topology_response here
    if st.session_state.last_topology_response:
         st.subheader("Export Configuration")
         try:
            # Prepare the JSON data for export, including topology_type
             export_data = st.session_state.last_topology_response.get("config", {})
             export_data["topology_type"] = st.session_state.last_topology_response.get("topology_type", "unknown")

             config_json = json.dumps(export_data, indent=2)
             json_bytes = config_json.encode('utf-8')

             # Display topology type from the prepared data
             st.markdown(f"**Topology Type:** {export_data['topology_type']}")

             st.text_area("Configuration JSON", value=config_json, height=150,
                          help="The JSON configuration used for the last successful generation.")

             # Add columns for buttons
             btn_col1, btn_col2 = st.columns(2)

             with btn_col1:
                 st.download_button(
                     label="Download Configuration (JSON)",
                     data=json_bytes,
                     file_name="config.json", # Changed filename for consistency
                     mime="application/json",
                 )

             with btn_col2:
                 if st.button("Export config.json to Project Root"):
                     export_path = os.path.join(PROJECT_ROOT, "config.json")
                     try:
                         with open(export_path, "w", encoding='utf-8') as f:
                             f.write(config_json)
                         st.success(f"Configuration exported to: {export_path}")
                     except PermissionError:
                         st.error(f"Permission denied: Cannot write to {export_path}. Check script permissions.")
                     except Exception as e:
                         st.error(f"Failed to export configuration file: {e}")

         except Exception as e:
             st.error(f"Error preparing/displaying JSON: {e}") 
import pandas as pd
import networkx as nx
from pyvis.network import Network

# Assuming 'cleaned_data' is your DataFrame
class TopTen_cell_phone_number_GraphGenerator:
    def __init__(self, cleaned_data):
        self.cleaned_data = cleaned_data
        self.G = nx.Graph()  # Create a directed graph
        self.components = None

    def cell_phone_number_generate_top_ten_graph(self):
        for _, row in self.cleaned_data.iterrows():
            # Add node for each ID

            self.G.add_node(row['id_number'])

            cell_phone_neighbors = self.cleaned_data[self.cleaned_data['cell_phone_number'] == row['cell_phone_number']]['id_number'].tolist()
            for neighbor in cell_phone_neighbors:
                self.G.add_edge(row['id_number'], neighbor)



        # Identify connected components
        components = list(nx.connected_components(self.G))

        # Sort components by size (number of nodes) and select the top ten
        top_ten_components = sorted(components, key=len, reverse=True)[:10]

        # Create a new graph containing only the nodes from the top ten components
        top_ten_graph =self.G.subgraph(set(node for component in top_ten_components for node in component))

        # Filter out isolated nodes (nodes with no incoming or outgoing edges)
        isolated_nodes = [node for node in top_ten_graph.nodes() if top_ten_graph.degree(node) == 0]
        filtered_top_ten_graph = top_ten_graph.copy()
        filtered_top_ten_graph.remove_nodes_from(isolated_nodes)

        # Identify connected components again
        components = list(nx.connected_components(filtered_top_ten_graph))
        self.components = components 

        # Sort components by size (number of nodes) and select the top ten
        top_ten_components = sorted(components, key=len, reverse=True)[:10]

        # Create a new graph containing only the nodes from the top ten components
        top_ten_graph = self.G.subgraph(set(node for component in top_ten_components for node in component))
        return top_ten_graph

    def create_cell_phone_number_pvis_network(self,top_ten_graph):
        # Visualization using pyvis
        nt = Network(
            notebook=False,
            height='2000px',
            width='100%',
            font_color="black",
            filter_menu=True,
            select_menu=True,
            directed=False  # Set directed to False for an undirected graph
        )

        nt.from_nx(top_ten_graph)


        cluster_cell_phone_number = {}
        for i, component in enumerate(self.components):
            cluster_cell_phone_in_component = set(self.cleaned_data.loc[self.cleaned_data['id_number'].isin(component), 'cell_phone_number'])
            cluster_cell_phone_number[i + 1] = str(cluster_cell_phone_in_component).strip('{}')
        # Add a single label for each connected component
        # Add a single label for each connected component based on addresses
        for i, component in enumerate(self.components):
            cluster_cell_phone_num = cluster_cell_phone_number[i + 1]
            nt.add_node(cluster_cell_phone_num, label=cluster_cell_phone_num, color='gray', size=10)  # Optional: Customize appearance of cluster nodes
            for node in component:
                # Check if the source and target nodes are different before adding the edge
                if node != cluster_cell_phone_num:
                    nt.add_edge(cluster_cell_phone_num, node)

        # Save the graph visualization as an HTML file
        nt.save_graph('one_label_per_connected_component_cell_phone_number.html')
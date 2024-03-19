import pandas as pd
import networkx as nx
from pyvis.network import Network
import re

class TopTen_addresses_GraphGenerator:
    def __init__(self, cleaned_data):
        self.cleaned_data = cleaned_data
        self.G = nx.Graph()  # Create a directed graph
        self.components = None

    # Function to filter addresses
    def filter_addresses(address):
        # Define a regular expression pattern for addresses with just country and township
        pattern = r'^[a-zA-Z\s,]+, [a-zA-Z\s,]+$'
        
        # Return True if the pattern matches, indicating the address lacks street number and building name
        return not bool(re.match(pattern, address))

    # Function to filter addresses
    def removeInvalid_addresses(address):
        # Split the address into fields using commas
        address_fields = address.split(',')
        
        # Return True if the address has more than two fields
        return len(address_fields) > 3
    def remove_rows_with_empty_column(self,column_to_check):
        """
        Remove rows from a DataFrame where a specific column is empty.

        Parameters:
        - df: pandas DataFrame
        - column_to_check: str, the column to check for empty values

        Returns:
        - pandas DataFrame with rows removed where the specified column is empty
        """

        return self.cleaned_data.dropna(subset=[column_to_check], how='any')
    
    def clean_addresses(self):
        self.cleaned_data = self.remove_rows_with_empty_column('valid_address')
        self.cleaned_data = self.cleaned_data[self.cleaned_data['valid_address'].apply(TopTen_addresses_GraphGenerator.filter_addresses)]
        self.cleaned_data = self.cleaned_data[self.cleaned_data['valid_address'].apply(TopTen_addresses_GraphGenerator.removeInvalid_addresses)]
        
    def addresses_generate_top_ten_graph(self):
        count = 0
        for _, row in self.cleaned_data.iterrows():
            # Add node for each ID
            count += 1
            self.G.add_node(row['id_number'])

            address_neighbors = self.cleaned_data[self.cleaned_data['valid_address'] == row['valid_address']]['id_number'].tolist()
            for neighbor in address_neighbors:
                self.G.add_edge(row['id_number'], neighbor)

        # # Create a NetworkX graph with edge labels
        # G_with_labels = nx.Graph()
        # for edge in self.G.edges():
        #     source, target = edge
        #     source_address = self.cleaned_data.loc[self.cleaned_data['id_number'] == source, 'valid_address'].values[0]
        #     target_address = self.cleaned_data.loc[self.cleaned_data['id_number'] == target, 'valid_address'].values[0]
        #     edge_label = f"{source_address} to {target_address}"
        #     G_with_labels.add_edge(source, target, label=edge_label)

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
    
    def create_addresses_pvis_network(self,top_ten_graph):
        
       # Visualization using pyvis
        nt = Network(
            notebook=False,
            height='2000px',
            width='100%',
            font_color="black",
            filter_menu=True,
            select_menu=True,
            directed=False,
            layout=True,  # Use a layout algorithm
        )

        # Set physics options through the options parameter
        nt.set_options('''
        var options = {
        "physics": {
            "barnesHut": {
            "gravitationalConstant": -2000,
            "centralGravity": 0.3,
            "springLength": 150,
            "springConstant": 0.05,
            "damping": 0.09,
            "avoidOverlap": 0.5
            },
            "minVelocity": 0.75,
            "maxVelocity": 10
        }
        }
        ''')

        nt.from_nx(top_ten_graph)


        cluster_addresses = {}
        for i, component in enumerate(self.components):
            addresses_in_component = set(self.cleaned_data.loc[self.cleaned_data['id_number'].isin(component), 'valid_address'])
            cluster_addresses[i + 1] = ", ".join(addresses_in_component)
        # Add a single label for each connected component
        # Add a single label for each connected component based on addresses
        for i, component in enumerate(self.components):
            cluster_address = cluster_addresses[i + 1]
            nt.add_node(cluster_address, label=cluster_address, color='gray', size=10)  # Optional: Customize appearance of cluster nodes
            for node in component:
                # Check if the source and target nodes are different before adding the edge
                if node != cluster_address:
                    nt.add_edge(cluster_address, node)

        # Save the graph visualization as an HTML file
        nt.save_graph('one_label_per_connected_component_address.html')




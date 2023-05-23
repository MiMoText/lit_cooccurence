import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Load the TSV file
filename = "work_title.tsv"
df = pd.read_csv(filename, sep='\t')

# Filter the data
filtered_df = df[(df['type'] == 'Literary work') & (df['MiMoTextBase_ID'].notna())]

# Get unique entities from the filtered data
unique_entities = filtered_df['text'].unique()

# Get unique entities and create an empty co-occurrence matrix
entities = filtered_df['Identifier'].unique()
co_occurrence_matrix = np.zeros((len(entities), len(entities)))

# Iterate over the rows to fill the co-occurrence matrix
for _, row in filtered_df.iterrows():
    text = row['text']
    identifier = row['Identifier']
    text_indices = np.where(filtered_df['text'] == text)[0]
    
    # Increment co-occurrence count for each pair of entities
    for idx in text_indices:
        other_identifier = filtered_df.iloc[idx]['Identifier']
        if identifier != other_identifier:
            identifier_index = np.where(entities == identifier)[0][0]
            other_index = np.where(entities == other_identifier)[0][0]
            co_occurrence_matrix[identifier_index, other_index] += 1

# Print the co-occurrence matrix
print(co_occurrence_matrix)

# Convert the co-occurrence matrix into a network graph
G = nx.from_numpy_array(co_occurrence_matrix)

# Get the entity labels from the original dataframe
entity_labels = {idx: entity for idx, entity in enumerate(entities)}

# Set the labels of the nodes in the network graph
nx.set_node_attributes(G, entity_labels, 'label')

nx.write_gexf(G, "work_title_graph.gexf")

### some backup code
"""
# Calculate degree centrality for each node
degree_centrality = nx.degree_centrality(G)

# Sort nodes based on degree centrality
sorted_nodes = sorted(degree_centrality, key=degree_centrality.get, reverse=True)

# Output a list of node labels and their centrality measures
node_centrality_list = []
for node in sorted_nodes:
    label = entity_labels[node]
    centrality = degree_centrality[node]
    node_centrality_list.append((label, centrality))

# Print the sorted list of node labels and centrality measures
for label, centrality in node_centrality_list:
    print(f"Node: {label} | Degree Centrality: {centrality}")

# Visualize the network graph with labels
plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G)
labels = nx.get_node_attributes(G, 'label')
nx.draw_networkx(G, pos, labels=labels, with_labels=True, node_size=500, node_color='lightblue', edge_color='gray')
plt.title('Co-occurrence Network Graph')
plt.axis('off')
plt.show()
"""

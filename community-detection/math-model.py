import networkx as nx
import matplotlib.pyplot as plt
import json

def modularity(G, partition):
    m = G.number_of_edges()
    Q = 0
    for community in set(partition.values()):
        nodes_in_community = [node for node, comm in partition.items() if comm == community]
        subgraph = G.subgraph(nodes_in_community)
        L_c = subgraph.number_of_edges()
        d_c = sum(dict(G.degree(nodes_in_community)).values())
        Q += (L_c / (2 * m)) - ((d_c / (2 * m))**2)
    return Q

def louvain_algorithm(G):
    partition = {node: node for node in G.nodes}
    modularity_history = [modularity(G, partition)]

    while True:
        for node in G.nodes:
            current_community = partition[node]
            best_community = current_community
            max_modularity_gain = 0

            neighbors = list(G.neighbors(node))
            current_community_size = sum(1 for n in G.nodes if partition[n] == current_community)

            for neighbor in set(neighbors):
                neighbor_community_size = sum(1 for n in G.nodes if partition[n] == partition[neighbor])
                modularity_gain = (
                    (G.degree(node) / (2 * G.number_of_edges())) -
                    (neighbor_community_size / (2 * G.number_of_edges())) +
                    ((current_community_size - 1) / (2 * G.number_of_edges())) *
                    (1 - (neighbor_community_size / G.number_of_edges()))
                )

                if modularity_gain > max_modularity_gain:
                    max_modularity_gain = modularity_gain
                    best_community = partition[neighbor]

            if best_community != current_community:
                partition[node] = best_community

        modularity_value = modularity(G, partition)
        modularity_history.append(modularity_value)

        if modularity_value <= max(modularity_history[:-1]):
            break

    return partition

# Create a graph
G = nx.karate_club_graph()

json_file_path = "results/pairwise_sim_report_bot.json"
with open(json_file_path, "r") as file:
    data = json.load(file)

# Add nodes and edges based on similarity threshold
similarity_threshold = 0.98

for entry in data:
    if entry["sim"] >= similarity_threshold:
        user1, user2 = entry["user_pair"]
        G.add_node(user1)
        G.add_node(user2)
        G.add_edge(user1, user2, weight=entry["sim"])

# Perform Louvain community detection
final_partition = louvain_algorithm(G)

# Get the number of communities
num_communities = len(set(final_partition.values()))
print("Number of communities:", num_communities)

# Visualize the network with community detection
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G)  # You can use a different layout algorithm if needed
colors = [final_partition[node] for node in G.nodes()]
nx.draw(G, pos, with_labels=True, node_color=colors, cmap=plt.cm.Blues, node_size=200, font_size=8)

# Customize the plot
plt.title("Network with Community Detection (Louvain)")
plt.show()

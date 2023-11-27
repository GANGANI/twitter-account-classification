import json
import networkx as nx
import matplotlib.pyplot as plt
import community

# Read data from the JSON file
json_file_path = "results/pairwise_sim_report_bot.json"
with open(json_file_path, "r") as file:
    data = json.load(file)

# Create a graph
G = nx.karate_club_graph()

# Add nodes and edges based on similarity threshold
similarity_threshold = 0.98

for entry in data:
    if entry["sim"] >= similarity_threshold:
        user1, user2 = entry["user_pair"]
        G.add_node(user1)
        G.add_node(user2)
        G.add_edge(user1, user2, weight=entry["sim"])

# Perform community detection using the Louvain algorithm
partition = community.best_partition(G)

# Get the number of communities
num_communities = max(partition.values()) + 1
print("Number of communities:", num_communities)

# Visualize the network with community detection
plt.figure(figsize=(8, 6))
nx.draw_kamada_kawai(G, with_labels=False, node_size=10, node_color=list(partition.values()),
                     edge_color='gray', width=0.5)

# Customize the plot
plt.title("Network with Community Detection (Louvain)")
plt.axis("off")

# Display the plot
plt.show()

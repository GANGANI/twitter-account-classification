import json
from tqdm import tqdm

class CommunityDetection:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.node_to_community = {node: i for i, node in enumerate(nodes)}

    def modularity(self, communities, adjacency_matrix):
        Q = 0
        m = len(self.edges)
        for i in range(len(communities)):
            for j in range(len(communities)):
                Q += (adjacency_matrix[i][j] - (sum(adjacency_matrix[i]) * sum(adjacency_matrix[j]) / (2 * m)))
        return Q / (2 * m)

    def get_neighbors(self, node):
        return [edge[1] for edge in self.edges if edge[0] == node] + [edge[0] for edge in self.edges if edge[1] == node]

    def run_louvain(self):
        # Get the number of nodes in the network
        num_nodes = len(self.nodes)

        # Initialize an empty adjacency matrix filled with zeros
        adjacency_matrix = []

        # Iterate over the nodes to create rows in the matrix
        for _ in tqdm(range(num_nodes)):
            # Create a row with zeros, representing connections to other nodes
            row = [0] * num_nodes
            # Append the row to the adjacency matrix
            adjacency_matrix.append(row)

        for edge in self.edges:
            i = self.nodes.index(edge[0])
            j = self.nodes.index(edge[1])
            adjacency_matrix[i][j] = 1
            adjacency_matrix[j][i] = 1

        modularity_gain = True
        while modularity_gain:
            modularity_gain = False
            for i in range(len(self.nodes)):
                for j in range(len(self.nodes)):
                    if self.node_to_community[self.nodes[i]] != self.node_to_community[self.nodes[j]]:
                        current_community = self.node_to_community[self.nodes[i]]
                        self.node_to_community[self.nodes[j]] = current_community

                        current_modularity = self.modularity(
                            [list(self.node_to_community.values())], adjacency_matrix
                        )
                        self.node_to_community[self.nodes[j]] = j

                        if current_modularity > self.modularity([list(self.node_to_community.values())],
                                                                adjacency_matrix):
                            self.node_to_community[self.nodes[j]] = current_community
                            modularity_gain = True

        communities = {}
        for node, community in self.node_to_community.items():
            if community not in communities:
                communities[community] = [node]
            else:
                communities[community].append(node)

        return communities


with open("results/pairwise_sim_report_bot.json", "r") as file:
    data = json.load(file)

similarity_threshold = 0.0

nodes = []
edges = []
for entry in tqdm(data):
    if entry["sim"] >= similarity_threshold:
        user1, user2 = entry["user_pair"]
        edge = (user1, user2)
        nodes.append(user1)
        nodes.append(user2)
        edges.append(edge)

cd = CommunityDetection(nodes, edges)
result = cd.run_louvain()
print(result)

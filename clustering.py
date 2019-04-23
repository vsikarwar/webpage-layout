import networkx as nx
import os
import json
from networkx.readwrite import json_graph

path = 'graph/'

def read_json_file(filename):
    with open(filename) as f:
        js_graph = json.load(f)
    return json_graph.node_link_graph(js_graph)

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.g' in file:
            files.append(os.path.join(r, file))

graphs = []

def id_name_mapping():
    map = {}
    f = open("graph/id-name-map.txt", "r")
    for line in f:
        ln = line.split(',')
        map[int(ln[0])] = ln[1]
    print(map)
    return map

#id_map = id_name_mapping()
#print(id_map)


for f in files:
    graphs.append((f, read_json_file(f)))

n = len(graphs)
sim_mat = [[0] * n for i in range(n)]
#calculate similarity
for i in range(n):
    for j in range(i, n):
        print("Calculating similarity for ", graphs[i][0], graphs[j][0])
        sim = 0.0
        if i != j:
            #sim = nx.optimize_graph_edit_distance(graphs[i][1], graphs[j][1])
            for v in nx.optimize_graph_edit_distance(graphs[i][1], graphs[j][1]):
                sim = v
        sim_mat[i][j] = sim
        sim_mat[j][i] = sim
        print("similarity for ", graphs[i][0], graphs[j][0], sim)

print(sim_mat)

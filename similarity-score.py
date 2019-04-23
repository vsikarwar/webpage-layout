import matplotlib.pyplot as plt
from collections import defaultdict
from bs4 import BeautifulSoup
import networkx as nx
import urllib.request
from collections import deque

page = urllib.request.urlopen('http://www.google.com/')
soup = BeautifulSoup(page)


def html_to_dom_tree(root):
    labels={}
    node_id = 1
    q = deque()
    graph = nx.Graph()

    q.appendleft({'element': root, "root_id": node_id})
    while len(q):
        node = q.pop()

        if node and node['element'].name == "body":
            graph.add_node(node_id, element=node['element'].name)
            node_id += 1

        root_id = node['root_id']
        labels[root_id] = node['element'].name


        for t in node['element'].contents:
            if t and t.name:
                graph.add_node(node_id, element=t.name)
                graph.add_edge(root_id, node_id)
                q.appendleft({"element": t, "root_id": node_id})
                node_id += 1

    return graph, labels


graph1, labels = html_to_dom_tree(soup.find("body"))

graph2, _ = html_to_dom_tree(soup.find("body"))

#nx.draw(graph1, labels=labels, with_labels = True)
#plt.show()

#https://networkx.github.io/documentation/latest/reference/algorithms/generated/networkx.algorithms.similarity.graph_edit_distance.html
dist = nx.graph_edit_distance(graph1, graph2)

print(dist)

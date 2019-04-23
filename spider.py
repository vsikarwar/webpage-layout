import urllib.request
from bs4 import BeautifulSoup
from networkx.readwrite import json_graph
import networkx as nx
import json


def html_to_dom_tree(root):
    labels={}
    node_id = 1
    #q = deque()
    q = []
    graph = nx.Graph()

    q.append({'element': root, "root_id": node_id, "depth":0})
    while len(q):
        node = q.pop(0)

        if node['depth'] > 4:
            break;

        if node and node['element'].name == "body":
            graph.add_node(node_id, element=node['element'].name)
            node_id += 1

        root_id = node['root_id']
        labels[root_id] = node['element'].name

        for t in node['element'].contents:
            if t and t.name:
                graph.add_node(node_id, element=t.name)
                graph.add_edge(root_id, node_id)
                q.append({"element": t, "root_id": node_id, "depth": node['depth']+1})
                node_id += 1

    return graph, labels

f_dump = open('graph/dump.txt', 'w')
f_id_map = open('graph/id-name-map.txt', 'w')


host_name = 'https://pythonprogramming.net'
paths = ['/introduction-to-python-programming']

page_id = 0
while paths:
    path = paths[0]
    child = []

    page_id = page_id + 1
    print('Scapping .... ', page_id, path)

    page = urllib.request.urlopen(host_name + path)
    soup = BeautifulSoup(page, "lxml")

    id_map_str = str(page_id) + ',' + path
    f_id_map.write(id_map_str + "\n")

    g, _ = html_to_dom_tree(soup.find('body'))

    data1 = json_graph.node_link_data(g)
    s1 = json.dumps(data1)

    f_graph = open('graph/' + str(page_id)+'.g', 'w')
    f_graph.write(s1)
    f_graph.close()

    for link in soup.find_all('a'):
        ln = link.get('href')

        if ln not in paths and ln.startswith('/') :
            paths.append(ln)
            child.append(ln)

    p_str = path + ',' + ','.join(child)

    f_dump.write(p_str + '\n')
    paths.pop(0)

f_dump.close()
f_id_map.close()

import urllib.request
from bs4 import BeautifulSoup
from networkx.readwrite import json_graph
import networkx as nx
import json

def scrap(host, max_depth=3):
    f_dump = open('./graph/dump.txt', 'w')
    g_dump = open('./graph/graphs.txt', 'w')

    visited = set()

    #visited = set()
    queue = [{'host': host, 'path': '/', 'id': -1, 'depth': 0, 'parent_id': -1}]
    node_id = 0

    while len(queue):
        node = queue.pop(0)
        if max_depth <= node['depth']:
            break

        url = node['host'] + node['path']
        if node['path'] in visited:
            continue

        node_id = node_id + 1
        node['id'] = node_id

        print('Scapping ... ', node)

        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, "lxml")
        body = soup.find('body')

        g = dom_to_graph(body, node['id'])

        data = json_graph.node_link_data(g)
        #print(data)
        j_dump = json.dumps(data)
        g_dump.write(j_dump + '\n')



        visited.add(node['path'])
        for link in soup.find_all('a'):
            ln = link.get('href')
            if ln not in visited and ln.startswith('/') :
                queue.append({'host': node['host'], 'path': ln, 'id': -1, 'depth': node['depth']+1, 'parent_id': node['id']})
        f_dump.write(json.dumps(node) + '\n')
    f_dump.close()
    g_dump.close()



def dom_to_graph(node, id):
    q = []
    graph = nx.Graph()

    node_id = 0
    root = {'node': node, 'id': 0, 'parent': -1, 'depth': 0, 'name': node.name}
    q.append(root)

    while len(q):
        n = q.pop(0)

        if n['parent'] == -1:
            graph.add_node(n['id'], element=n['name'])
        node_id += 1

        n['id'] = node_id
        graph.add_node(n['id'], element=n['name'])
        graph.add_edge(n['parent'], n['id'])

        for t in n['node'].contents:
            if t and t.name and not t.name == 'script':
                q.append({'node': t, 'id': 0, 'parent': n['id'], 'depth': n['depth']+1, 'name': t.name})

    return graph


def reader():
    file = open('./graph/graphs.txt', 'r')
    graphs = []
    for f in file:
        graphs.append(json_graph.node_link_graph(json.loads(f)))
    file.close()
    return graphs

def similarity(graphs):
    n = len(graphs)
    sim_mat = [[0] * n for i in range(n)]
    #calculate similarity
    for i in range(n):
        for j in range(i, n):
            print("Calculating similarity for ", i, j)
            if i == j:
                sim_mat[i][j] = 0.0
                continue
            sim = nx.graph_edit_distance(graphs[i], graphs[j])
            #for v in nx.optimize_graph_edit_distance(graphs[i][1], graphs[j][1]):
            #    sim = v
            sim_mat[i][j] = sim
            sim_mat[j][i] = sim
            print("similarity for ", i, j, sim)


class Node:
    def __init__(self, content=None, name=None, id=None, parent=None, cls=None, depth=None, tree_id=None):
        self.content = content
        self.name = name
        self.children = []
        self.cls = cls
        self.id = id
        self.parent=parent
        self.depth = depth
        self.tree_id=tree_id


    def __str__(self):
        return str({'name' : self.name, 'id': self.id, 'parent': self.parent, 'class': self.cls, 'depth':self.depth, 'tree_id': self.tree_id, 'children': self.children})

    def __repr__(self):
        return self.__str__()

scrap('https://pythonprogramming.net')

#graphs = reader()
#similarity(graphs)

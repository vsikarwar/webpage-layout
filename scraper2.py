import urllib.request
from bs4 import BeautifulSoup
import json
from collections import namedtuple
from zss import simple_distance, Node
import numpy as np
from sklearn.cluster import DBSCAN
import requests
import pickle

dump_path = './tree/fifa-dump.txt'
trees_path = './tree/fifa-trees.txt'

def scrap(host, max_depth=3):
    f_dump = open(dump_path, 'w')
    t_dump = open(trees_path, 'w')

    visited = set()

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

        r  = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, "lxml")

        #page = urllib.request.urlopen(url)
        #soup = BeautifulSoup(page, "lxml")
        body = soup.find('body')

        t = dom_to_tree(body, node['id'])
        t_dump.write(json.dumps(t) + '\n')

        visited.add(node['path'])
        for link in soup.find_all('a'):
            ln = link.get('href')
            if ln and ln not in visited and ln.startswith('/') :
                queue.append({'host': node['host'], 'path': ln, 'id': -1, 'depth': node['depth']+1, 'parent_id': node['id']})
        f_dump.write(json.dumps(node) + '\n')
    f_dump.close()
    t_dump.close()


def dom_to_tree(root, id):
    q = []
    node_id = 0

    node = {'name': root.name,
            'id': node_id,
            'depth': 0,
            'parent': -1,
            'tree_id': id,
            'children': []}

    if root.has_attr('class'):
        node['class'] = list(root['class'])

    q.append({'node': node, 'content': root})

    while len(q):
        element = q.pop(0)
        n = element['node']
        c = element['content']

        for t in c.contents:
            if t and t.name:
                node_id += 1
                c_node = {'name': t.name,
                          'id': node_id,
                          'depth': n['depth']+1,
                          'parent': n['parent'],
                          'tree_id': n['tree_id'],
                          'children': []}
                if t.has_attr('class'):
                    c_node['class'] = t['class']
                n['children'].append(c_node)
                q.append({'node': c_node, 'content': t})

    return node


def reader():
    file = open(trees_path, 'r')
    trees = []
    for f in file:
        trees.append(json.loads(f))
    file.close()
    return trees

def getList(node):
    lst = []
    for n in node:
        if not n['name'] == 'script':
            lst.append({'name': n['name']})
    s_lst = sorted(lst, key=lambda k: k['name'])
    return lst

def frequency_similarity(t1, t2):
    q = []
    q.append({'t1': t1['children'], 't2': t2['children']})
    edit_dists = []

    count = 0
    while q:
        node = q.pop(0)
        c_t1 = node['t1']
        c_t2 = node['t2']

        c1 = getList(c_t1)
        c2 = getList(c_t2)
        if not c1 and not c2:
            continue

        edit_dist = editDistDP(c1, c2, compare3)
        edit_dists.append(edit_dist)

        c_n = {'t1': [], 't2': []}
        for c in c_t1:
            if c['children']:
                c_n['t1'] = c_n['t1'] + c['children']
        for c in c_t2:
            if c['children']:
                c_n['t2'] = c_n['t2'] + c['children']
        q.append(c_n)

    div = 1
    _sum = 0
    for e in edit_dists:
        _sum += e/div
        div *= 2
    return _sum


def clustering_DBSCAN(sim_mat):
    X = np.array(sim_mat)
    clustering = DBSCAN(eps=3, min_samples=2).fit(X)
    return clustering.labels_

def zss_tree(node):
    q = []
    q.append(node)

    while len(node):
        n = q.pop(0)
        name = n['name']

        for c in n['children']:
            q.append(c)

def zss_similarity(node1, node2):
    a = Node(node1['name'], node1['children'])
    b = Node(node2['name'], node2['children'])

    dist = simple_distance(a, b)

    return dist

def compare3(n1, n2, i, j):
    if n1[i]['name'] == n2[j]['name']:
        return True
    return False

def compare2(node1, node2, i, j):
    if node1[i] == node2[j]:
        return True
    return False

def compare1(node1, node2, i, j):
    if node1[i]['name'] == node2[j]['name']:
        return True
    return False

def similarity(trees, sim_func):
    n = len(trees)
    sim_mat = [[0] * n for i in range(n)]
    #calculate similarity
    for i in range(n):
        for j in range(i, n):
            if i == j:
                sim_mat[i][j] = 0.0
                continue
            sim = sim_func(trees[i], trees[j])
            sim_mat[i][j] = sim
            sim_mat[j][i] = sim
    return sim_mat


def editDistDP(lst1, lst2, compare):
    # Create a table to store results of subproblems
    m = len(lst1)
    n = len(lst2)
    dp = [[0 for x in range(n+1)] for x in range(m+1)]

    # Fill d[][] in bottom up manner
    for i in range(m+1):
        for j in range(n+1):

            # If first string is empty, only option is to
            # insert all characters of second string
            if i == 0:
                dp[i][j] = j    # Min. operations = j

            # If second string is empty, only option is to
            # remove all characters of second string
            elif j == 0:
                dp[i][j] = i    # Min. operations = i

            # If last characters are same, ignore last char
            # and recur for remaining string
            elif compare(lst1, lst2, i-1, j-1):
                dp[i][j] = dp[i-1][j-1]

            # If last character are different, consider all
            # possibilities and find minimum
            else:
                dp[i][j] = 1 + min(dp[i][j-1],        # Insert
                                   dp[i-1][j],        # Remove
                                   dp[i-1][j-1])    # Replace

    return dp[m][n]


host = 'https://www.fifa.com'
#scrap(host)

trees = reader()
#print(trees[0]['children'])
#frequency_similarity(trees[0], trees[1])
#dist = zss_similarity(trees[0], trees[1])
#print(dist)
sim_mat = similarity(trees, frequency_similarity)
print(sim_mat)
pickle.dump(sim_mat, open('./images/fifa/sim.p', 'wb'))
#sim_mat = pickle.load(open('./images/fifa/sim.p', 'rb'))
#print(sim_mat)
#clusters = clustering_DBSCAN(sim_mat)
#print(clusters)

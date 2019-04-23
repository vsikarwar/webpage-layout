import urllib.request
from bs4 import BeautifulSoup
import json
from collections import namedtuple
from zss import simple_distance, Node
import numpy as np
from sklearn.cluster import DBSCAN
import requests
import pickle
from os import listdir
from os.path import isfile, join
from sklearn.cluster import KMeans
import sys
import tqdm
from tqdm import trange

page_path = './dumps/page_'
trees_path = './trees/tree_'
sim_mat_path = './sim-mat/'
score_path = './score/'
dump_path = './'
image_path = './images/'

host = 'https://www.fifa.com'

def scrap(host, max_depth = 3):
    root = {'host': host, 'path': '/', 'id': -1, 'depth': 0, 'parent_id': -1, 'data': None}
    queue = [root]
    tree_id = 0

    visited = set()

    _d_fd = open('./dumps.txt', 'a')

    while queue:
        node = queue.pop(0)

        # break if the depth is greater than asked depth
        if max_depth <= node['depth']:
            break

        if node['path'] in visited:
            continue

        url = node['host'] + node['path']

        #increment  node
        tree_id += 1

        node['id'] = tree_id

        print('Scapping ... ', node)

        r  = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, "lxml")

        pagePath = page_path +  str(node['id']) + '.soup'
        imagePath = folder_path + str(node['id']) + '.png'

        node['data'] = pagePath
        node['image'] = imagePath

        fd = open(pagePath, 'w')
        fd.write(soup.prettify())
        fd.close()

        #take screenshot
        #hrefs = asyncio.get_event_loop().run_until_complete(screenshot(url, imagePath))

        _d_fd.write(json.dumps(node) + '\n')

        visited.add(node['path'])
        for link in soup.find_all('a'):
            ln = link.get('href')
            if ln and ln not in visited and ln.startswith('/') :
                queue.append({'host': node['host'], 'path': ln, 'id': -1, 'depth': node['depth']+1, 'parent_id': node['id'], 'data': None})

    _d_fd.close()

async def screenshot(url, filePath):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.setViewport({ 'width': 1920, 'height': 1080 });
    await page.goto(url)
    await page.screenshot({'path': filePath, 'fullPage':True})
    element = await page.querySelectorAll('a')
    hrefs = []
    for ele in element:
        href = await page.evaluate('(ele) => ele.href', ele)
        hrefs.append(href)
    await browser.close()
    return hrefs


def reader():
    data = []
    fd = open('./dumps.txt', 'r')
    for f in fd:
        data.append(json.loads(f))
    fd.close()
    return data

def dom_to_tree(data):
    nodes = []
    for d in data:
        file = open(d['data'], 'r')
        soup = BeautifulSoup(file, "lxml")
        body = soup.find('body')
        t = _dom_to_tree(body, d['id'])
        nodes.append(t)
    #return nodes

def _dom_to_tree(root, id):
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

    while q:
        element = q.pop(0)
        n = element['node']
        c = element['content']

        for t in c.contents:
            if t and t.name:
                node_id += 1
                c_node = {'name': t.name,
                          'id': node_id,
                          'depth': n['depth']+1,
                          'parent': n['id'],
                          'tree_id': n['tree_id'],
                          'children': []}
                if t.has_attr('class'):
                    c_node['class'] = t['class']
                n['children'].append(c_node)
                q.append({'node': c_node, 'content': t})
    fd = open(trees_path + str(id) + '.tree', 'w')
    fd.write(json.dumps(node))
    fd.close()

    return node

def readTrees(data, path='./trees/'):
    trees = []
    for d in data:
        _path = path + 'tree_' + str(d['id']) + '.tree'
        fd = open(_path, 'r')
        trees.append(json.loads(fd.read().rstrip()))
    return trees

def compareTrees(trees):
    n = len(trees)
    sim_mat = [[0] * n for i in range(n)]
    t = trange(n, desc='Bar desc', leave=True)
    for i in t:
        for j in tqdm.tqdm(range(i, n)):
            if i == j:
                sim_mat[i][j] = 0

            t1 = trees[i]
            t2 = trees[j]

            edit_dist = _compareTrees(t1, t2)
            dist = _edit_dist(edit_dist)
            sim_mat[i][j] = dist
            sim_mat[j][i] = dist

            t.set_description(' %d / %d = %d'% (t1['tree_id'], t2['tree_id'], dist))

    return sim_mat


def _edit_dist(lst):
    dist = 0
    for i in range(len(lst)):
        dist = dist + (lst[i] / (2**i))
    return dist


def _compareTrees(tree1, tree2):

    lst_t1 = []
    lst_t1.append(tree1)

    lst_t2 = []
    lst_t2.append(tree2)

    edit_score = []

    q = []
    q.append((lst_t1, lst_t2))

    while q:
        ele = q.pop(0)
        #print(ele)

        e1 = []
        for t in ele[0]:
            e1.append(t['name'])

        e2 = []
        for t in ele[1]:
            e2.append(t['name'])

        #print(e1, e2)

        edit_score.append(editDistDP(e1, e2, compareNode2))

        #print(edit_score)

        child1 = []
        for l in ele[0]:
            if l['children']:
                child1.extend(l['children'])

        child2 = []
        for l in ele[1]:
            if l['children']:
                child2.extend(l['children'])

        if child1 and child2:
            q.append((child1, child2))
    return edit_score


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


def compareNode2(n1, n2, i, j):
    if n1[i] == n2[j]:
        return True
    return False

def compareNode(n1, n2, i, j):
    print(n1, n2)
    if n1[i]['name'] == n2[j]['name']:
        return True
    return False

def compare(tree1, tree2):
    tup = (tree1, tree2)

    q = []

    q.append(tup)

    while q:
        t = q.pop(0)

        child1 = tree1['children']
        child2 = tree2['children']


def clustering_Kmeans(sim_mat):
    X = np.array(sim_mat)
    clustering = KMeans(n_clusters=2, random_state=0).fit(X)
    return clustering.labels_

def clustering_DBSCAN(sim_mat):
    X = np.array(sim_mat)
    clustering = DBSCAN(eps=8, min_samples=3).fit(X)
    return clustering.labels_

def decodeClusters(clusters_, data):
    m = {}
    for i in range(len(clusters_)):
        if clusters_[i] not in m:
            m[clusters_[i]] = []
        #print(data)
        ele = (data[i]['id'], data[i]['path'])
        m[clusters_[i]].append(ele)
    for k in m:
        print(k, m[k] , '\n')


#scrap(host)

data = reader()
#dom_to_tree(data)
trees = readTrees(data)
#trees = sorted(readTrees(), key=lambda e: e['tree_id'])

#pickle.dump(compareTrees(trees), open(sim_file, 'wb'))

sim_file = './sim1.p'
cluster_file = './cluster_DBSCAN_1.p'

sim_mat = pickle.load(open(sim_file, 'rb'))
pickle.dump(clustering_DBSCAN(sim_mat), open(cluster_file, 'wb'))
decodeClusters(pickle.load(open(cluster_file, 'rb')), data)

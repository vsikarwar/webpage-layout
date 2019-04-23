import asyncio
from pyppeteer import launch
import json
import numpy as np
import cv2
import math
from sklearn.cluster import DBSCAN

folder_path = './images/fifa/'
dump_path = folder_path + 'dump.txt'
cnts_path = folder_path + 'cnts.txt'


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


def scrap(host, max_depth=3):
    f_dump = open(dump_path, 'w')

    visited = set()
    queue = [{'path': host, 'id': -1, 'depth': 0, 'parent_id': -1}]
    node_id = 0

    while len(queue):
        node = queue.pop(0)
        if max_depth <= node['depth']:
            break

        url = node['path']
        if url in visited:
            continue

        node_id = node_id + 1
        node['id'] = node_id
        image = folder_path + str(node['id']) + '.png'
        node['image'] = image

        print('Scapping ... ', node)

        #take screenshot
        hrefs = asyncio.get_event_loop().run_until_complete(screenshot(url, image))

        visited.add(url)

        for link in hrefs:
            if link not in visited and link.startswith(host):
                queue.append({'path': link, 'id': -1, 'depth': node['depth']+1, 'parent_id': node['id']})
        f_dump.write(json.dumps(node) + '\n')
    f_dump.close()

def reader():
    file = open(dump_path, 'r')
    data = []
    for f in file:
        data.append(json.loads(f))
    file.close()
    return data

def processor(data):
    cnts = []
    f = open(cnts_path, 'w')
    for d in data:
        c = contours(d)
        f.write(json.dumps(c) + '\n')
        cnts.append(c)
    f.close()
    return cnts

def isSame(cnt1, cnt2, i, j):
    dist_th = 5
    area_th = 5

    center1 = cnt1['center'][i]
    center2 = cnt2['center'][j]
    dist = distance(center1, center2)

    area1 = cnt1['area'][i]
    area2 = cnt2['area'][j]
    area_diff = abs(area1-area2)

    if dist < dist_th and area_diff < area_th:
        return True

    return False


def distance(a, b):
     dist = math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
     return dist

def editDistDP(cnt1, cnt2):
    # Create a table to store results of subproblems
    m = cnt1['len']
    n = cnt2['len']
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
            elif isSame(cnt1, cnt2, i-1, j-1):
                dp[i][j] = dp[i-1][j-1]

            # If last character are different, consider all
            # possibilities and find minimum
            else:
                dp[i][j] = 1 + min(dp[i][j-1],        # Insert
                                   dp[i-1][j],        # Remove
                                   dp[i-1][j-1])    # Replace

    return dp[m][n]


def similarityScore(cnts):
    n = len(cnts)
    sim_mat = [[0 for x in range(n)] for x in range(n)]
    sim = 0
    for i in range(n):
        for j in range(i, n):
            if i == j:
                sim_mat[i][j] = 0
                continue
            cnt1 = cnts[i]
            cnt2 = cnts[j]

            dist = editDistDP(cnt1, cnt2)
            sim_mat[i][j] = dist
            sim_mat[j][i] = dist
    return sim_mat

def contours(data):
    # read image
    img = cv2.imread(data['image'])

    # resize image
    scale_percent = 70 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    resized_img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    gray_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)

    blur_img = cv2.medianBlur(gray_img,5)

    th = cv2.adaptiveThreshold(blur_img,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
                cv2.THRESH_BINARY_INV,11,2)

    kernel = np.ones((3, 5), np.uint8)

    temp_img = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=3)

    (_, contours, _) = cv2.findContours(temp_img.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    (cnts, boundingBoxes) = sort_contours(contours)

    cnts_map = {'id': data['id'], 'rect': [], 'c_x': [], 'c_y': [], 'center': [], 'area': [], 'len': len(contours)}
    for cnt, box in zip(cnts, boundingBoxes):
        x, y, w, h = box
        cx = x+w/2; cy = y+h/2
        area = cv2.contourArea(cnt);
        cnts_map['c_x'].append(cx)
        cnts_map['c_y'].append(cy)
        cnts_map['center'].append((cx, cy))
        cnts_map['rect'].append((x, y, w, h))
        cnts_map['area'].append(area)

    return cnts_map


def sort_contours(cnts, method="left-to-right"):
	# initialize the reverse flag and sort index
	reverse = False
	i = 0

	# handle if we need to sort in reverse
	if method == "right-to-left" or method == "bottom-to-top":
		reverse = True

	# handle if we are sorting against the y-coordinate rather than
	# the x-coordinate of the bounding box
	if method == "top-to-bottom" or method == "bottom-to-top":
		i = 1

	# construct the list of bounding boxes and sort them from top to
	# bottom
	boundingBoxes = [cv2.boundingRect(c) for c in cnts]
	a = zip(*sorted(zip(cnts, boundingBoxes), \
                    key=lambda b:b[1][i], reverse=reverse))

	# return the list of sorted contours and bounding boxes
	return (cnts, boundingBoxes)


def clustering_DBSCAN(sim_mat):
    X = np.array(sim_mat)
    clustering = DBSCAN(eps=30, min_samples=2).fit(X)
    return clustering.labels_

def kmean(sim_mat):
    pass


def decode_cluster(clusters, data):
    map = {}

    for i in range(len(clusters)):
        d = data[i]
        c = clusters[i]
        if c not in map:
            map[c] = []

        map[c].append(d)
    return map

def analyze():
    d = reader()
    c = processor(d)
    sim_mat = similarityScore(c)
    clusters = clustering_DBSCAN(sim_mat)
    result = decode_cluster(clusters, d)
    print(sim_mat)
    print('\n')
    print(clusters)
    print('\n')
    for r in result:
        print(result[r], '\n')


host = 'https://www.fifa.com/'
#scrap('https://pythonprogramming.net/')
#scrap(host)
analyze()

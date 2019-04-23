import numpy as np
import cv2

# read image
img = cv2.imread("test-sample2.jpeg")

# resize image
scale_percent = 50 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
# resize image
resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

cv2.imshow('resized' , resized)

'''
#convert bgr to hsv
hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

# define range of red color in HSV
lower_red = np.array([30,150,50])
upper_red = np.array([255,255,180])

mask = cv2.inRange(hsv, lower_red, upper_red)

# Bitwise-AND mask and original image
res = cv2.bitwise_and(resized,resized, mask= mask)

# finds edges in the input image image and
# marks them in the output map edges
edges = cv2.Canny(resized,5,20)

#Display edges in a frame
cv2.imshow('Edges',edges)
'''

gray_img = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
cv2.imshow('morphlogyEx',gray_img)

img = cv2.medianBlur(gray_img,5)

th2 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
            cv2.THRESH_BINARY_INV,11,2)
th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY_INV,11,2)

_, th1 = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

cv2.imshow('threshhold',th2)

kernel = np.ones((3, 5), np.uint8)

temp_img = cv2.morphologyEx(th2, cv2.MORPH_CLOSE, kernel, iterations=3)

cv2.imshow('morphlogyEx',temp_img)


#(_, contours, hierarchy) = cv2.findContours(temp_img.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
(_, contours, hierarchy) = cv2.findContours(temp_img.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

#print(heirarchy)
#print(heirarchy[0])

#print(hierarchy)
#hierarchy = hierarchy[0] # get the actual inner list of hierarchy descriptions

cntrs = {}

'''
# For each contour, find the bounding rectangle and draw it
for component in zip(contours, hierarchy):
    currentContour = component[0]
    currentHierarchy = component[1]
    #print('current hier ', currentHierarchy)
    x,y,w,h = cv2.boundingRect(currentContour)
    if currentHierarchy[2] < 0:
        # these are the innermost child components
        cv2.rectangle(resized,(x,y),(x+w,y+h),(0,0,255),1)
    elif currentHierarchy[3] < 0:
        # these are the outermost parent components
        #cv2.rectangle(resized,(x,y),(x+w,y+h),(0,255,0),1)
        pass
    else:
        #pass
        cv2.rectangle(resized,(x,y),(x+w,y+h),(255,0,0),1)

'''

'''
areas = []

for c in contours:
    #print('contours ', c)
    (x, y, w, h) = cv2.boundingRect(c)
    area = cv2.contourArea(c)
    if area not in cntrs:
        cntrs[area] = []
    cntrs[area].append(c)
    areas.append(area)
    #cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 1)

mean = sum(areas)/len(areas)

for cnt in cntrs:
    if cnt > mean:
        for c in cntrs[cnt]:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 1)


#print(cntrs)
'''

for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(resized, (x, y), (x+w, y+h), (0, 255, 0), 1)
cv2.imshow('contours',resized)


cv2.waitKey(0)

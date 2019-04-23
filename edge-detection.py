import cv2
import numpy as np

img1 = cv2.imread("test-sample1.jpeg")

#convert bgr to hsv
hsv = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)

# define range of red color in HSV
lower_red = np.array([30,150,50])
upper_red = np.array([255,255,180])

mask = cv2.inRange(hsv, lower_red, upper_red)

# Bitwise-AND mask and original image
res = cv2.bitwise_and(img1,img1, mask= mask)

# Display an original image
cv2.imshow('Original',img1)

# finds edges in the input image image and
# marks them in the output map edges
edges = cv2.Canny(img1,50,200)


# Display edges in a frame
cv2.imshow('Edges',edges)

ret,th = cv2.threshold(edges,127,255,cv2.THRESH_BINARY)

#cv2.imshow('threshold',th)

#kernel = np.ones((5, 5), np.uint8)
#temp_img = cv2.dilate(th, kernel, iterations=5)

#temp_img = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=3)
#temp_img_1 = cv2.erode(temp_img,kernel,iterations=1)

#cv2.imshow('dilation',temp_img)

(_, contours, _) = cv2.findContours(th.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

for c in contours:
    (x, y, w, h) = cv2.boundingRect(c)
    cv2.rectangle(img1, (x, y), (x + w, y + h), (0, 255, 0), 3)

cv2.imshow('contours',img1)

# Wait for Esc key to stop
cv2.waitKey(0)

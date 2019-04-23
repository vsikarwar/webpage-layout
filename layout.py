import numpy as np
import cv2

img = cv2.imread("test-sample2.jpeg")

# resize image
scale_percent = 30 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
# resize image
resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

cv2.imshow('resized' , resized)

#copy the original image
img1 = resized.copy()

#convert the image into grayscale
gray_img = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

#otsu threshold
#blur = cv2.GaussianBlur(gray_img,(5,5),0)
#cv2.imshow("test-blur", blur)
_, th = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
#ret,th = cv2.threshold(blur,240,255,cv2.THRESH_BINARY_INV)


#cv2.imshow("test-th", th)

#(_, th) = cv2.threshold(gray_img, 100, 255, cv2.THRESH_BINARY)

#assign the kernel size
#kernel = np.ones((2, 1), np.uint8)
kernel = np.ones((2, 2), np.uint8)

temp_img = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=1)
cv2.imshow("test-img", temp_img)
#temp_img_1 = cv2.erode(temp_img,kernel,iterations=1)

#temp_img = cv2.dilate(th, kernel, iterations=9)

#find contours
#(_, contours, _) = cv2.findContours(temp_img.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
(_, contours, _) = cv2.findContours(temp_img, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

col_img = cv2.cvtColor(temp_img, cv2.COLOR_GRAY2RGB)

cv2.drawContours(img1, contours, -1, (255,0,0), 5)

'''
for c in contours:
    (x, y, w, h) = cv2.boundingRect(c)
    cv2.rectangle(img1, (x, y), (x + w, y + h), (0, 255, 0), 3)
'''
'''
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(img1, (x, y), (x+w, y+h), (0, 255, 0), 1)
'''

#cv2.imshow("test-img", img_cp)

cv2.waitKey(0)

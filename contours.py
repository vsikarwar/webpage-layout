import numpy as np
import cv2

# read image
img = cv2.imread("test-sample3.jpeg")

# resize image
scale_percent = 50 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
# resize image
resized_img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

#cv2.imshow('resized' , resized)

gray_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)

blur_img = cv2.medianBlur(gray_img,5)

th = cv2.adaptiveThreshold(blur_img,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
            cv2.THRESH_BINARY_INV,11,2)

kernel = np.ones((3, 5), np.uint8)

temp_img = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=3)

(_, contours, _) = cv2.findContours(temp_img.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

print(len(contours))

for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    cx = x+w/2; cy = y+h/2
    area = cv2.contourArea(c);
    cv2.rectangle(resized_img, (x, y), (x+w, y+h), (0, 255, 0), 1)

cv2.imshow('contours',resized_img)

cv2.waitKey(0)

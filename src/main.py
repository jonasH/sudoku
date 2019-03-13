from matplotlib import pyplot as plt
import cv2
import numpy as np
from scratch import calc_size, find_corners, Point2f
from itertools import product
import sys
plt.rcParams['figure.figsize'] = [15, 10]
canny_limit = 65


def convert_corners(corners):
    result = []
    for corner in corners:
        result.append([corner.x, corner.y])

    return np.float32(result)

def find_largest_contour(imgx):
    edgesx = cv2.Canny(imgx, canny_limit, canny_limit * 2, apertureSize=3)
    contours, hierarchy = cv2.findContours(edgesx, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    largest_area = 0.0
    largest_contour = []
    for contour in contours:
        area = cv2.contourArea(contour, False)
        if area > largest_area:
            largest_contour = contour
            largest_area = area
    return largest_contour

def remove_lines(img):
    ret,img2 = cv2.threshold(~img,127,255,cv2.THRESH_BINARY)
    edges = cv2.Canny(img2,100,150,apertureSize = 3)

    # probably need to get this down to 450x450 to make the threshold work
    lines = cv2.HoughLines(edges,1,np.pi/180, 100)
    for line in lines:
        for rho,theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))

            cv2.line(img,(x1,y1),(x2,y2),(255,255,255), 5)

    return img


img = cv2.imread(sys.argv[1])
means = cv2.fastNlMeansDenoising(img)

#img = cv2.cvtColor(means,cv2.COLOR_BGR2GRAY)
ret,img = cv2.threshold(means,127,255,cv2.THRESH_BINARY)
#make this always resize to 450x450 or there about
imgx = cv2.resize(img, (0,0), fx=0.25, fy=0.25)



largest_contour = find_largest_contour(imgx)
rect = cv2.boundingRect(largest_contour)
corners = find_corners(largest_contour)
size = calc_size(corners)
flat_corners = []
flat_corners.append(Point2f(0,0))
flat_corners.append(Point2f(size.width,0))
flat_corners.append(Point2f(size.width, size.height))
flat_corners.append(Point2f(0, size.height))
transform = cv2.getPerspectiveTransform(convert_corners(corners), convert_corners(flat_corners))
imgx = cv2.warpPerspective(imgx, transform, (int(size.width), int(size.height)))

imgx1 = cv2.GaussianBlur(imgx, (0, 0), 3);
imgx2 = cv2.addWeighted(imgx, 1.5, imgx1, -0.5, 0);

imgx = remove_lines(imgx2)

width, height, _ = imgx.shape
sq_width = width // 9
sq_height = height // 9
xs = range(0, width - sq_width, sq_width)
ys = range(0, height - sq_height, sq_height)
i = 1
for y in ys:
    for x in xs:
        sub_img = imgx[y:y + sq_height, x:x+sq_width]
        largest_contour = find_largest_contour(sub_img)
        if len(largest_contour):
            rect = cv2.boundingRect(largest_contour)
            cv2.rectangle(sub_img, rect, (255, 0, 0), 1)
        plt.subplot(9,9, i), plt.imshow(sub_img)
        i += 1
plt.show()

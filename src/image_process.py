import cv2
from matplotlib import pyplot as plt
from collections import namedtuple
import numpy
import numpy as np
from nptyping import Array
Point2f = namedtuple('Point2f', ['x','y'])
Size = namedtuple('Size', ['width','height'])
canny_limit = 65

def calc_euclidian_dist(a, b):
    return numpy.sqrt(numpy.power(a.x - b.x, 2) + numpy.power(a.y - b.y, 2))

def calc_size(corners):
    # determine the dimensions that we should warp this contour to
    widthTop = calc_euclidian_dist(corners[0], corners[1])
    widthBottom = calc_euclidian_dist(corners[2], corners[3])

    heightLeft = calc_euclidian_dist(corners[0], corners[3])
    heightRight = calc_euclidian_dist(corners[1], corners[2])

    return Size(max(widthTop, widthBottom), max(heightLeft, heightRight))


def find_corners(largestContour):
        maxDist = [0, 0, 0, 0]
        corners = [0, 0, 0, 0]
        M = cv2.moments(largestContour, True)
        cX = M['m10'] / M['m00']
        cY = M['m01'] / M['m00']
        for i in range(4):
            maxDist[i] = 0.0;
            corners[i] = Point2f(cX, cY)
        
        center = Point2f(cX, cY)
        
        # find the most distant point in the contour within each quadrant
        for point in largestContour:
            p = Point2f(point[0][0], point[0][1])
            dist = calc_euclidian_dist(p, center)
            # print("(", p.x , "," , p.y , ") is " , dist , " from (" , cX , "," , cY , ")")
            if p.x < cX and p.y < cY and maxDist[0] < dist:
                # top left
                maxDist[0] = dist
                corners[0] = p
            elif p.x > cX and p.y < cY and maxDist[1] < dist:
                # top right
                maxDist[1] = dist
                corners[1] = p
            elif p.x > cX and p.y > cY and maxDist[2] < dist:
                # bottom right
                maxDist[2] = dist
                corners[2] = p
            elif p.x < cX and p.y > cY and maxDist[3] < dist:
                # bottom left
                maxDist[3] = dist
                corners[3] = p

        
        return corners


def convert_corners(corners) -> Array[np.float32]:
    result = []
    for corner in corners:
        result.append([corner.x, corner.y])

    return np.float32(result)

def find_largest_contour(imgx: Array[np.uint8]) -> Array[np.int32]:
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

def remove_lines(img: Array[np.uint8]):

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

def load_img(filename):
    img = cv2.imread(filename)
    means = cv2.fastNlMeansDenoising(img)
    ret,img = cv2.threshold(means,127,255,cv2.THRESH_BINARY)
    imgx = cv2.resize(img, (0,0), fx=0.25, fy=0.25)
    return imgx


def unwrap_img(imgx):
    largest_contour = find_largest_contour(imgx)
    corners = find_corners(largest_contour)
    size = calc_size(corners)
    flat_corners = []
    flat_corners.append(Point2f(0.0,0.0))
    flat_corners.append(Point2f(size.width, 0.0))
    flat_corners.append(Point2f(size.width, size.height))
    flat_corners.append(Point2f(0.0, size.height))
    transform = cv2.getPerspectiveTransform(convert_corners(corners), convert_corners(flat_corners))
    imgx = cv2.warpPerspective(imgx, transform, (int(size.width), int(size.height)))

    imgx1 = cv2.GaussianBlur(imgx, (0, 0), 3);
    imgx2 = cv2.addWeighted(imgx, 1.5, imgx1, -0.5, 0);
    return imgx2


def extact_numbers(imgx):
    result = []
    width, height, _ = imgx.shape
    sq_width = width // 9
    sq_height = height // 9
    xs = range(0, width - sq_width, sq_width)
    ys = range(0, height - sq_height, sq_height)
    #i = 1
    for y in ys:
        row_result = []
        for x in xs:
            sub_img = imgx[y:y + sq_height, x:x+sq_width]
            largest_contour = find_largest_contour(sub_img)
            if len(largest_contour):
                rect = cv2.boundingRect(largest_contour)
                #cv2.rectangle(sub_img, rect, (255, 0, 0), 1)
                #plt.subplot(9,9, i), plt.imshow(sub_img)
                number = sub_img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+ rect[2]]
            else:
                number = []
            #i += 1
            row_result.append(number)
        result.append(row_result)
    #plt.show()

    return np.array(result)

def extract_squares(filename: str):
    imgx = load_img(filename)
    imgx2 = unwrap_img(imgx)
    imgx = remove_lines(imgx2)
    return extact_numbers(imgx)

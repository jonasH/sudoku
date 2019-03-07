import cv2
from collections import namedtuple
import numpy

Point2f = namedtuple('Point2f', ['x','y'])
Size = namedtuple('Size', ['width','height'])


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

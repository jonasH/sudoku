import cv2 as cv
from matplotlib import pyplot as plt
img = cv.imread('mittgavle_sudoku.jpg',0)
ret,thresh1 = cv.threshold(img,75,255,cv.THRESH_BINARY)
plt.imshow(thresh1)
plt.show()

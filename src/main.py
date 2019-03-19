from matplotlib import pyplot as plt
from image_process import extract_squares
import sys
plt.rcParams['figure.figsize'] = [15, 10]

def main():
    squares = extract_squares(sys.argv[1])
    i = 1
    for row in squares:
        for square in row:
            if len(square):
                plt.subplot(9,9,i), plt.imshow(square)
                
            i += 1

    plt.show()
    
if __name__ == '__main__':
    main()

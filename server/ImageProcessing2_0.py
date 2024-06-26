import numpy as np
from skimage.segmentation import slic
import cv2
import matplotlib.pyplot as plt

class ImageProcessor():
    NUMSEGMENT = 170
    COMPACTNESS = 80
    RESIZEPARM = 5
    
    def __init__(self, img, width, height) -> None:
        
        self.colorScheme = []
        self.pixelData = []
        self.img = img
        self.width = width
        self.height = height
        self.threshold = 15

    def process(self):
        preprocessed = self.preprocess()
        dim = (self.width // self.RESIZEPARM, self.height // self.RESIZEPARM)
        # resized = cv2.resize(np.int8(preprocessed), dim, interpolation = cv2.INTER_LINEAR)
        pixelated = self.pixelate(preprocessed)
        # plt.imshow(pixelated)
        # plt.show()

        pixelData = self.flattenPixel(pixelated)
        colorScheme = self.flattenColorScheme()
        
        return pixelData, colorScheme

    def preprocess(self):
        preprocessed = []
        
        for row in range(0,self.height):
            curRow = []

            for col in range(0, self.width*4, 4):
                red = self.img[col + row * self.width * 4]
                green = self.img[col + 1+ row * self.width * 4]
                blue = self.img[col + 2 +row * self.width * 4]

                pixel = [red, green, blue]

                curRow.append(pixel)

            preprocessed.append(curRow)
        
        return preprocessed

    def pixelate(self, preprocessed):
        original = np.int16(preprocessed)
        segmented = slic(original ,n_segments=self.NUMSEGMENT,compactness=self.COMPACTNESS)
        pixelated = self.reduce(segmented,original).tolist()
        return pixelated

    def colorCache(self, c1):
        r1, g1, b1 = c1
        for c2 in self.colorScheme:
            r2, g2, b2 = c2

            if abs(r1 - r2) > self.threshold: continue
            if abs(g1 - g2) > self.threshold: continue
            if abs(b1 - b2) > self.threshold: continue
            return [r2, g2, b2]

        self.colorScheme.append([int(r1), int(g1), int(b1)])
        return c1

    def reduce(self, segmented, original):
        unique = np.unique(segmented)
        final = np.int16(original)
        for u in np.asarray((unique)).T:
            inds = np.where(segmented == u)
            avg_col = np.mean(final[inds], axis = 0, dtype=np.int32)

            final[inds] = self.colorCache(avg_col)

        return final
    
    def flattenColorScheme(self):
        flattened = []

        for color in self.colorScheme:
            flattened.append({
                'r' : color[0],
                'g' : color[1],
                'b' : color[2]
            })

        return flattened

    def flattenPixel(self, pixelated):
        
        flattened = []
        for row in pixelated:
            curRow = []
            for color in row:
                curRow.append({
                    'r' : color[0],
                    'g' : color[1],
                    'b' : color[2]
                })
            flattened.append(curRow)

        return flattened
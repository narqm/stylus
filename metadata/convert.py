from img2pdf import convert
from os import remove
import cv2 as cv
import numpy as np
from shutil import copy

class Convert:
    '''Converts cover_page.jpg to PDF'''

    @staticmethod
    def remove_watermark():
        '''Removes the watermark from Google Books preview image'''
        img = cv.imread('cover_page.jpg')
        blank = np.zeros(img.shape[:2], dtype='uint8')

        start_pt = (img.shape[1]-152, img.shape[0]-36)
        end_pt = (img.shape[1]-15, img.shape[0]-21)
        mask = cv.rectangle(blank, start_pt, end_pt, 255, -1)

        kernel_size = (5, 5)
        mask = cv.GaussianBlur(mask, kernel_size, cv.BORDER_DEFAULT)

        dst = cv.inpaint(img, mask, 3, cv.INPAINT_TELEA)
        cv.imwrite('cover_page.jpg', dst)
    
    @staticmethod
    def import_image(image):
        '''Copies a given image for use by the other methods'''
        assert image.endswith('.jpg'), 'Image file needs to be .jpg'
        copy(image, 'cover_page.jpg')

    @staticmethod
    def convert_to_pdf():
        '''Converts jpg to a PDF'''
        with open('cover_page.pdf', 'wb') as f:
            f.write(convert('cover_page.jpg'))
        
        remove('cover_page.jpg')
import cv2 as cv


class IgnoreRegion:
    def __init__(self, image: tuple = None, position: str = None, ratio: float = None):
        self._x1 = None
        self._y1 = None
        self._x2 = None
        self._y2 = None
        
        # If a position and rario has been given, use that, otherwise show the ROT selector
        if position is not None and ratio is not None and image is not None:
            image_width = image.shape[1]
            image_height = image.shape[0]
            
            if position == 'left':
                self._x1 = 0
                self._y1 = 0
                self._x2 = int(image_width * ratio)
                self._y2 = image_height
            elif position == 'right':
                self._x1 = int(image_width * (1 - ratio))
                self._y1 = 0
                self._x2 = image_width
                self._y2 = image_height
        elif image is not None:
            bounding_box = cv.selectROI(image)
            image_width = image.shape[0]
            image_height = image.shape[1]
            
            self._x1 = bounding_box[0]
            self._y1 = bounding_box[1]
            self._x2 = bounding_box[0] + bounding_box[2]
            self._y2 = bounding_box[1] + bounding_box[3]
        
    def is_in_ignore_region(self, bounding_box: tuple):
        bbox_x2 = bounding_box[0] + bounding_box[2]
        bbox_y2 = bounding_box[1] + bounding_box[3]
        
        # Do the math to check for a collision on both axis
        # Check if there was a collison
        if bbox_x2 >= self._x1 and self._x2 >= bounding_box[0] and bbox_y2 >= self._y1 and self._y2 >= bounding_box[1]:
            return True
        else:
            return False
    
    def draw(self, image):
        cv.rectangle(image, (self._x1, self._y1), (self._x2, self._y2), (0,255,0), 2, 1)
        return image

from common.ignore_region import IgnoreRegion
import cv2 as cv


class TrackedPerson:
    def __init__(self, tracker, bounding_box):
        self._tracker = tracker
        self._bounding_box = bounding_box
        self._num_fails = 0
        self._was_last_update_successful = False
    
    def update(self, image):
        # Update the tracker based on the given image
        ok, bbox = self._tracker.update(image)

        if ok:
            # Update the bounding box if the update was successful
            self._bounding_box = bbox
            self._was_last_update_successful = True
            return True # Return true: the update was successful
        else:
            # If the update wasn't successful, increment the number of fails
            self._num_fails += 1
            
            self._was_last_update_successful = False
            
            return False # Return false: the update wasn't successful
    
    def draw(self, image):
        if self._was_last_update_successful:
            # Prepare the bounding box data to be passable to cv.rectangle()
            p1 = (int(self._bounding_box[0]), int(self._bounding_box[1]))
            p2 = (int(self._bounding_box[0]) + int(self._bounding_box[2]), int(self._bounding_box[1]) + int(self._bounding_box[3]))
            
            # Pass the bounding box data to cv.rectangle to be drawn to the image
            cv.rectangle(image, p1, p2, (255,0,0), 2, 1)
            return image
    
    def is_overlapping_ir(self, ignore_region: IgnoreRegion):
        return ignore_region.is_in_ignore_region(self._bounding_box)

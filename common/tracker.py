from tokenize import Ignore
import cv2 as cv

from common.capture import Capture
from common.ignore_region import IgnoreRegion
from common.tracked_person import TrackedPerson


class Tracker:
    def __init__(self, capture: Capture, ignore_region: IgnoreRegion = None):
        self._capture = capture
        self._ignore_region = ignore_region
        self._num_people_who_left_feed = 0
        
        # Initialise the object detection algorithm
        self._hog = cv.HOGDescriptor()
        
        # Set the hog to detect people
        self._hog.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())
        
        # Initialise an empty list of TrackedPerson objects
        self._tracked_people = []
    
    def detect(self):
        image = self._capture.read()  # Read the next frame from the capture feed
        
        if image is not None:
            # Reset all the trackers
            self._tracked_people = []

            # Detect all the people in the image
            predictions, _w = self._hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.10)

            # Loop through each detected person
            for x, y, w, h in predictions:
                # Reduce the size of the bounding box, hog tends to make them quite large
                pad_w, pad_h = int(0.15 * w), int(0.05 * h)
                
                # Set the bounding box values
                bounding_box = (x + pad_w, y + pad_w, w - pad_w, h - pad_h)

                # Determine if the person should be tracked based on if the they overlap the ignore region or not
                should_track = True
                if self._ignore_region is not None:
                    if self._ignore_region.is_in_ignore_region(bounding_box=bounding_box):
                        should_track = False

                # If the person should be tracked, create a tracker and append it to the trackers list
                if should_track:
                    # Create and initialise a new tracker
                    tracker = cv.legacy.TrackerMOSSE_create()
                    ok = tracker.init(image, bounding_box)
                    
                    # Create a new TrackedPerson object and append it the the tracked people list
                    tracked_person = TrackedPerson(tracker, bounding_box)
                    self._tracked_people.append(tracked_person)
        else:
            # If OpenCV for whatever reason couldn't capture an image from the VideoCapture
            print("Error: Couldn't read capture feed.")
    
    def track(self):
        image = self._capture.read()
        
        num_tracked = 0
        num_who_just_left_feed = 0

        if image is not None:
            
            # Loop through each tracked person
            for index, tracked_person in enumerate(self._tracked_people):
                # Update the tracked person based on the image
                if tracked_person.update(image):
                    # Increment the number of people who are being tracked in the image
                    num_tracked += 1
                    
                    if self._ignore_region is not None:
                        # Check if the tracked person is overlapping with the ignore region
                        if tracked_person.is_overlapping_ir(self._ignore_region):
                            # Remove the tracked person from the tracked people list
                            self._tracked_people.pop(index)
                            
                            # Increment these, since a tracked person has left the feed
                            num_who_just_left_feed += 1
                            self._num_people_who_left_feed += 1
                            continue   
        else:
            print("Error: Couldn't read capture feed.")
        
        return {"num_people_tracked": num_tracked, 
                "num_who_just_left_feed": num_who_just_left_feed,
                "num_total_left_feed": self._num_people_who_left_feed}
    
    def detect_once(self):
        image = self._capture.read()  # Read the next frame from the capture feed
        
        if image is not None:
            # Reset all the trackers
            self._tracked_people = []

            # Detect all the people in the image
            predictions, _ = self._hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.10)

            for x, y, w, h in predictions:
                cv.rectangle(image, (x,y), (x + w, y + h), (0, 0, 255), 2)
            
            return {"num_detected": len(predictions)}
        else:
            return {"num_detected": 0}
    
    def draw_and_show(self):
        # Get an image of the last read frame
        image = self._capture.last_frame
        
        if image is not None:
            # Draw the Ignore Region to the image if it exists
            if self._ignore_region is not None:
                self._ignore_region.draw(image)
            
            # Draw boxes around the tracked people
            for tracked_person in self._tracked_people:
                tracked_person.draw(image)
            
            # Show the image in a window
            cv.imshow("Tracker Feed", image)
            cv.waitKey(1)
    
    def reset(self, capture: Capture, ignore_region: IgnoreRegion = None):
        self._capture = capture
        self._ignore_region = ignore_region
        self._num_people_who_left_feed = 0
        self._tracked_people = []

import cv2
import numpy as np
from PIL import Image
import random
from region import DifferenceRegion

# Class 2: ImageProcessor
# Handles all OpenCV image loading, cloning, and programmatic alteration
class ImageProcessor:

    # Total number of differences to introduce into the modified image
    NUM_DIFFERENCES = 5
    # Minimum and maximum pixel size for each difference region
    MIN_SIZE = 45
    MAX_SIZE = 95

    def __init__(self):
        # Store the original image as a BGR numpy array (None until loaded)
        self.original_bgr = None
        # Store the modified clone with hidden differences applied
        self.modified_bgr = None
        # Store the list of DifferenceRegion objects for the current image
        self.differences  = []

    def load_image(self, filepath):
        # Attempt to read the image file from disk using OpenCV
        img = cv2.imread(filepath)
        # Return False immediately if OpenCV could not open the file
        if img is None:
            return False
        # Save the original image and build the modified version with differences
        self.original_bgr = img
        self.modified_bgr, self.differences = self._build_modified(img)
        return True

    def get_display_pair(self, max_w, max_h):
        # Convert both BGR numpy images to PIL and scale them to fit the canvas
        return (self._fit(self._to_pil(self.original_bgr), max_w, max_h),
                self._fit(self._to_pil(self.modified_bgr),  max_w, max_h))

    def _build_modified(self, src):
        # Make an exact pixel copy of the original to modify
        clone = src.copy()
        # Read the image height and width for boundary calculations
        h, w  = src.shape[:2]
        # Keep a list of placed regions and count placement attempts
        diffs, attempts = [], 0

        # Keep trying to place regions until we have 5 or run out of attempts
        while len(diffs) < self.NUM_DIFFERENCES and attempts < 800:
            attempts += 1
            # Pick a random width and height for this region
            rw = random.randint(self.MIN_SIZE, self.MAX_SIZE)
            rh = random.randint(self.MIN_SIZE, self.MAX_SIZE)
            # Pick a random top-left position that keeps the region fully inside the image
            rx = random.randint(5, w - rw - 6)
            ry = random.randint(5, h - rh - 6)
            # Create a temporary region object to test for overlap
            candidate = DifferenceRegion(len(diffs), rx, ry, rw, rh, "")
            # Skip this position if it overlaps with any already-placed region
            if self._overlaps(candidate, diffs):
                continue
            # Choose a random alteration type and apply it to the cloned image
            dtype = random.choice(DifferenceRegion.TYPES)
            candidate.diff_type = dtype
            self._alter(clone, rx, ry, rw, rh, dtype)
            # Add the confirmed region to the list
            diffs.append(candidate)

        return clone, diffs

    def _overlaps(self, cand, existing, pad=25):
        # Check the candidate rectangle against every already-placed region
        for d in existing:
            # Condition: the two rectangles overlap including the padding gap
            if (cand.x < d.x + d.width  + pad and
                cand.x + cand.width  + pad > d.x and
                cand.y < d.y + d.height + pad and
                cand.y + cand.height + pad > d.y):
                return True
        return False

    def _alter(self, img, x, y, w, h, dtype):
        # Extract the rectangular region of interest from the image
        roi = img[y:y+h, x:x+w]

        # Alteration 1 - Colour Shift: rotate the hue channel in HSV colour space
        if dtype == "colour_shift":
            shift = random.choice([35, -35, 55, -55])
            # Convert the region to HSV so we can shift the hue independently
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).astype(np.int32)
            # Add the shift to the hue channel and wrap around at 180 degrees
            hsv[:, :, 0] = (hsv[:, :, 0] + shift) % 180
            # Convert back to BGR and write the altered region into the image
            img[y:y+h, x:x+w] = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # Alteration 2 - Brightness: multiply pixel values to darken or brighten
        elif dtype == "brightness":
            # Choose a factor below 1 to darken or above 1 to brighten
            f = random.choice([0.50, 1.60])
            # Multiply every channel by the factor and clip to valid 0-255 range
            img[y:y+h, x:x+w] = np.clip(roi.astype(np.float32) * f, 0, 255).astype(np.uint8)

        # Alteration 3 - Blur: apply a Gaussian blur to soften the region
        elif dtype == "blur":
            # Choose a large odd kernel size to make the blur noticeable
            k = random.choice([13, 17, 21])
            img[y:y+h, x:x+w] = cv2.GaussianBlur(roi, (k, k), 0)

    @staticmethod
    def _to_pil(bgr):
        # Convert a BGR numpy array to an RGB PIL Image for display in Tkinter
        return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))

    @staticmethod
    def _fit(img, max_w, max_h):
        # Copy the image then shrink it to fit within max_w x max_h, keeping aspect ratio
        img = img.copy()
        img.thumbnail((max_w, max_h), Image.LANCZOS)
        return img

import math

# Class 1: DifferenceRegion
# Stores the position, size, type, and found-status of one hidden difference
class DifferenceRegion:

    # The three types of alteration the program can apply to a region
    TYPES = ["colour_shift", "brightness", "blur"]

    def __init__(self, region_id, x, y, width, height, diff_type):
        # Store a unique number to identify this region
        self.region_id = region_id
        # Store the top-left corner coordinates in original image pixels
        self.x         = x
        self.y         = y
        # Store the width and height of the rectangular region
        self.width     = width
        self.height    = height
        # Store which type of alteration was applied to this region
        self.diff_type = diff_type
        # Track whether the player has found this difference yet
        self.found     = False

    @property
    def center(self):
        # Calculate and return the centre point of the region as (x, y)
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def radius(self):
        # Calculate the circle radius as half the longest side plus padding
        return max(self.width, self.height) // 2 + 12

    def contains_point(self, px, py, tolerance=0):
        # Calculate straight-line distance from the click to the region centre
        cx, cy = self.center
        dist = math.hypot(px - cx, py - cy)
        # Return True if the click falls within the radius plus any extra tolerance
        return dist <= self.radius + tolerance

    def __repr__(self):
        # Return a readable string summary of this region for debugging
        return (f"DifferenceRegion(#{self.region_id} {self.diff_type} "
                f"@({self.x},{self.y}) {self.width}x{self.height} found={self.found})")

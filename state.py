# Class 3: GameState
# Tracks mistakes, found differences, and overall score across all rounds
class GameState:

    # Maximum number of wrong clicks allowed before the round ends
    MAX_MISTAKES = 3
    # Total number of differences to find per image
    TOTAL = 5

    def __init__(self):
        # Initialise the cumulative score that carries over between images
        self.total_found = 0
        # Reset all per-round counters to their starting values
        self.reset()

    def reset(self):
        # Reset the mistake counter for the new round
        self.mistakes         = 0
        # Reset the number of differences found in this round
        self.found_this_round = 0
        # Clear the game-over flag so the player can click again
        self.game_over        = False
        # Clear the round-complete flag so the win state is not triggered early
        self.round_complete   = False

    @property
    def remaining(self):
        # Return how many differences the player still needs to find this round
        return self.TOTAL - self.found_this_round

    @property
    def mistakes_left(self):
        # Return how many wrong clicks the player can still make this round
        return self.MAX_MISTAKES - self.mistakes

    @property
    def active(self):
        # Return True only when the round is still in progress
        return not self.game_over and not self.round_complete

    def correct(self):
        # Increment both the round counter and the cumulative total
        self.found_this_round += 1
        self.total_found      += 1
        # Mark the round as complete once all 5 differences have been found
        if self.found_this_round >= self.TOTAL:
            self.round_complete = True

    def wrong(self):
        # Increment the mistake counter for this round
        self.mistakes += 1
        # End the round if the player has used all three allowed mistakes
        if self.mistakes >= self.MAX_MISTAKES:
            self.game_over = True

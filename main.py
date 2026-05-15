'''
HIT137 - Group Assignment 3, Group: Sydney 14

Question: 1 ->
Two images are shown side by side. The right one has 5 hidden changes
made by the program. The player clicks on the right image to find them.
Each click is checked against the known difference locations.

'''

from app import SpotTheDifferenceApp

# Entry point - create and run the application
if __name__ == "__main__":
    # Create the main application window and start the Tkinter event loop
    app = SpotTheDifferenceApp()
    app.mainloop()
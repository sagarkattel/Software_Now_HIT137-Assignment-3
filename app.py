import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk

# Import the refactored classes
from theme import Theme
from processor import ImageProcessor
from state import GameState

# Class 4: SpotTheDifferenceApp
# Main Tkinter window - inherits from tk.Tk to demonstrate inheritance
# Builds and manages the entire GUI and connects it to the game logic
class SpotTheDifferenceApp(tk.Tk):

    # Maximum pixel dimensions for each image canvas panel
    IMG_W     = 540
    IMG_H     = 460
    # Extra pixels beyond a region's radius that still count as a correct click
    TOLERANCE = 20

    def __init__(self):
        # Call the parent tk.Tk constructor to create the main window
        super().__init__()
        self.title("Spot the Difference  ·  HIT137")
        self.configure(bg=Theme.BG_BASE)
        self.resizable(True, True)

        # Create the ImageProcessor to handle all OpenCV work
        self.proc  = ImageProcessor()
        # Create the GameState to track score and mistakes
        self.state = GameState()

        # Store references to PhotoImage objects to prevent garbage collection
        self._orig_tk = None
        self._mod_tk  = None
        # Store the scale factors from original image pixels to display pixels
        self._scale_x = 1.0
        self._scale_y = 1.0
        # Store the actual displayed image size after thumbnail scaling
        self._disp_w  = 0
        self._disp_h  = 0

        # Create Tkinter StringVars so the status bar updates automatically
        self._var_remaining = tk.StringVar(value="--")
        self._var_mistakes  = tk.StringVar(value="0 / 3")
        self._var_score     = tk.StringVar(value="0")
        self._var_msg       = tk.StringVar(value="Load an image to begin playing")

        # Build all UI sections and show the empty placeholder canvases
        self._build_ui()
        self._draw_placeholder()

   
    # Class _build_ui
    # Calls each section builder in order from top to bottom
    def _build_ui(self):
        self._build_header()
        self._build_status_bar()
        self._build_image_area()
        self._build_footer()

    # Class _build_header
    # Creates the top bar with the game title and the two action buttons
    def _build_header(self):
        # Create a fixed-height frame for the header area
        hdr = tk.Frame(self, bg=Theme.BG_HEADER, height=68)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        # Place the title and subtitle labels on the left side of the header
        tblock = tk.Frame(hdr, bg=Theme.BG_HEADER)
        tblock.pack(side=tk.LEFT, padx=24, pady=10)
        tk.Label(tblock, text="[+]  SPOT THE DIFFERENCE",
                 bg=Theme.BG_HEADER, fg=Theme.GOLD,
                 font=("Georgia", 17, "bold")).pack(anchor="w")
        tk.Label(tblock,
                 text="Find all 5 hidden changes · click only the modified image",
                 bg=Theme.BG_HEADER, fg=Theme.TEXT_SECONDARY,
                 font=("Georgia", 9, "italic")).pack(anchor="w")

        # Place the Load Image and Reveal All buttons on the right side
        bframe = tk.Frame(hdr, bg=Theme.BG_HEADER)
        bframe.pack(side=tk.RIGHT, padx=20, pady=14)
        self._flat_btn(bframe, "  Load Image  ",
                       self._load_image, Theme.GOLD).pack(side=tk.LEFT, padx=6)
        self._flat_btn(bframe, "  Reveal All  ",
                       self._reveal_all, Theme.COBALT).pack(side=tk.LEFT, padx=6)

        # Draw a thin gold line below the header as a visual accent
        tk.Frame(self, bg=Theme.GOLD, height=2).pack(fill=tk.X)

    # Class _build_status_bar
    # Creates the live-updating counters for remaining, mistakes, and score
    def _build_status_bar(self):
        # Create the dark background bar that spans the full window width
        bar = tk.Frame(self, bg=Theme.BG_STATUS)
        bar.pack(fill=tk.X)

        inner = tk.Frame(bar, bg=Theme.BG_STATUS)
        inner.pack(fill=tk.BOTH, padx=24, pady=8)

        # Helper function to build one labelled counter block
        def stat(parent, label, var, accent):
            f = tk.Frame(parent, bg=Theme.BG_STATUS)
            f.pack(side=tk.LEFT, padx=18)
            # Small uppercase label above the number
            tk.Label(f, text=label,
                     bg=Theme.BG_STATUS, fg=Theme.TEXT_MUTED,
                     font=("Courier", 8, "bold")).pack(anchor="w")
            # Large coloured number that updates via the StringVar
            tk.Label(f, textvariable=var,
                     bg=Theme.BG_STATUS, fg=accent,
                     font=("Courier", 16, "bold")).pack(anchor="w")

        # Build the three stat blocks with their matching accent colours
        stat(inner, "REMAINING",   self._var_remaining, Theme.EMERALD)
        stat(inner, "MISTAKES",    self._var_mistakes,  Theme.CRIMSON)
        stat(inner, "TOTAL FOUND", self._var_score,     Theme.GOLD)

        # Add a thin vertical line to separate the counters from the message
        tk.Frame(inner, bg=Theme.TEXT_MUTED, width=1).pack(
            side=tk.LEFT, padx=22, fill=tk.Y, pady=2)

        # Build the status message block that shows feedback after each click
        mblock = tk.Frame(inner, bg=Theme.BG_STATUS)
        mblock.pack(side=tk.LEFT)
        tk.Label(mblock, text="STATUS",
                 bg=Theme.BG_STATUS, fg=Theme.TEXT_MUTED,
                 font=("Courier", 8, "bold")).pack(anchor="w")
        # Store a reference to this label so we can change its colour later
        self.lbl_msg = tk.Label(mblock, textvariable=self._var_msg,
                                 bg=Theme.BG_STATUS, fg=Theme.TEXT_PRIMARY,
                                 font=("Courier", 11))
        self.lbl_msg.pack(anchor="w")

        # Draw a thin separator line between the status bar and image panels
        tk.Frame(self, bg=Theme.TEXT_MUTED, height=1).pack(fill=tk.X)

    # Class _build_image_area
    # Creates the two canvas panels side by side with a VS divider between them
    def _build_image_area(self):
        # Create the container frame for both panels
        area = tk.Frame(self, bg=Theme.BG_BASE)
        area.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        # Build the original (reference) panel on the left
        self.canvas_orig = self._image_panel(
            area, "ORIGINAL  ·  reference only", accent=Theme.TEXT_SECONDARY)
        self.canvas_orig.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Build the narrow VS divider between the two panels
        div = tk.Frame(area, bg=Theme.BG_BASE, width=40)
        div.pack(side=tk.LEFT, fill=tk.Y)
        div.pack_propagate(False)
        # Place a vertical line through the centre of the divider
        tk.Frame(div, bg=Theme.TEXT_MUTED, width=1).place(
            relx=0.5, rely=0.05, relheight=0.9)
        # Place the VS label at the midpoint of the divider
        tk.Label(div, text="VS", bg=Theme.BG_BASE, fg=Theme.TEXT_MUTED,
                 font=("Georgia", 9, "bold italic")).place(
            relx=0.5, rely=0.5, anchor="center")

        # Build the modified (clickable) panel on the right
        self.canvas_mod = self._image_panel(
            area, "MODIFIED  ·  click here to find differences",
            accent=Theme.GOLD, clickable=True)
        self.canvas_mod.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Bind left-click events to the click handler
        self.canvas_mod.bind("<Button-1>", self._on_click)
        # Bind mouse movement to change the cursor near difference regions
        self.canvas_mod.bind("<Motion>",   self._on_hover)
        self.canvas_mod.config(cursor="crosshair")

    def _image_panel(self, parent, label_text, accent, clickable=False):
        # Use gold border for the clickable panel, muted border for the reference
        border_col = Theme.GOLD if clickable else Theme.TEXT_MUTED
        # The outer frame acts as the coloured border by using padx/pady of 1
        outer = tk.Frame(parent, bg=border_col, padx=1, pady=1)
        outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # The inner frame holds the label and canvas on the dark background
        inner = tk.Frame(outer, bg=Theme.BG_PANEL)
        inner.pack(fill=tk.BOTH, expand=True)

        # Add the panel label at the top
        tk.Label(inner, text=label_text,
                 bg=Theme.BG_PANEL, fg=accent,
                 font=("Courier", 9, "bold"),
                 pady=7, padx=10, anchor="w").pack(fill=tk.X)

        # Draw a thin line separating the label from the canvas
        tk.Frame(inner, bg=border_col, height=1).pack(fill=tk.X)

        # Create and return the canvas where the image will be displayed
        canvas = tk.Canvas(inner, bg=Theme.BG_BASE,
                            highlightthickness=0,
                            width=self.IMG_W, height=self.IMG_H)
        canvas.pack(fill=tk.BOTH, expand=True)
        return canvas

    # Class _build_footer
    # Creates a small info strip at the very bottom of the window
    def _build_footer(self):
        # Draw a thin separator line above the footer
        tk.Frame(self, bg=Theme.TEXT_MUTED, height=1).pack(fill=tk.X)
        foot = tk.Frame(self, bg=Theme.BG_HEADER, height=28)
        foot.pack(fill=tk.X)
        foot.pack_propagate(False)
        # Place the course info text on the right side of the footer
        tk.Label(foot,
                 text="HIT137 Assignment 3  ·  OOP + Tkinter + OpenCV  ·  3 alteration types",
                 bg=Theme.BG_HEADER, fg=Theme.TEXT_MUTED,
                 font=("Courier", 8)).pack(side=tk.RIGHT, padx=14, pady=6)

    # Class _flat_btn
    # Builds a custom flat button that inverts colours on hover
    def _flat_btn(self, parent, text, command, fg):
        # Use a Label widget styled as a button with a coloured border
        btn = tk.Label(parent, text=text, bg=Theme.BG_HEADER, fg=fg,
                        font=("Courier", 10, "bold"),
                        relief=tk.FLAT, padx=8, pady=5,
                        highlightthickness=1, highlightbackground=fg,
                        cursor="hand2")
        # Trigger the command function when the label is left-clicked
        btn.bind("<Button-1>", lambda e: command())
        # Invert foreground and background colours when the mouse enters
        btn.bind("<Enter>",    lambda e: btn.config(bg=fg, fg=Theme.BG_BASE))
        # Restore original colours when the mouse leaves
        btn.bind("<Leave>",    lambda e: btn.config(bg=Theme.BG_HEADER, fg=fg))
        return btn

    # Class _draw_placeholder
    # Draws a dashed rectangle and helper text before any image is loaded
    def _draw_placeholder(self):
        # Define the placeholder text for the original and modified panels
        configs = [
            (self.canvas_orig, "No image loaded", "will appear here"),
            (self.canvas_mod,  "No image loaded", "<-- click to find differences"),
        ]
        for canvas, line1, line2 in configs:
            canvas.delete("all")
            w, h = self.IMG_W, self.IMG_H
            # Draw a dashed border rectangle to indicate the image area
            canvas.create_rectangle(18, 18, w-18, h-18,
                                     outline=Theme.TEXT_MUTED, dash=(7, 5), width=1)
            # Draw the placeholder icon text in the centre
            canvas.create_text(w//2, h//2 - 30, text="[ IMG ]",
                                font=("Courier", 20, "bold"), fill=Theme.TEXT_MUTED)
            # Draw the first hint line below the icon
            canvas.create_text(w//2, h//2 + 22, text=line1,
                                fill=Theme.TEXT_SECONDARY, font=("Courier", 13))
            # Draw the second hint line below the first
            canvas.create_text(w//2, h//2 + 46, text=line2,
                                fill=Theme.TEXT_MUTED, font=("Courier", 10))

    # Class _load_image
    # Opens a file dialog, loads the chosen image, and starts a new round
    def _load_image(self):
        # Open a file browser and ask the player to select an image file
        path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp"),
                       ("All files", "*.*")])
        # Do nothing if the player closed the dialog without choosing a file
        if not path:
            return
        # Show an error message if OpenCV could not read the selected file
        if not self.proc.load_image(path):
            self._set_msg("Could not load image -- try another file.", Theme.CRIMSON)
            return

        # Reset the game state and recompute the display scale for the new image
        self.state.reset()
        self._compute_scale()
        self._repaint()
        self._refresh_status()
        self._set_msg("Image loaded -- find the 5 hidden differences!", Theme.EMERALD)

    def _compute_scale(self):
        # Read the pixel dimensions of the original image
        h, w = self.proc.original_bgr.shape[:2]
        # Create a dummy PIL image and thumbnail it to find the displayed size
        dummy = Image.new("RGB", (w, h))
        dummy.thumbnail((self.IMG_W, self.IMG_H), Image.LANCZOS)
        self._disp_w, self._disp_h = dummy.size
        # Calculate how many display pixels correspond to one original image pixel
        self._scale_x = self._disp_w / w
        self._scale_y = self._disp_h / h

    # Class _repaint
    # Redraws both canvases from scratch, optionally drawing circles on them
    def _repaint(self, circles=None):
        # Get fresh PIL images scaled to fit the canvas panels
        orig_pil, mod_pil = self.proc.get_display_pair(self.IMG_W, self.IMG_H)

        # If there are circles to draw, convert the PIL images to numpy arrays
        if circles:
            orig_cv = np.array(orig_pil)
            mod_cv  = np.array(mod_pil)
            for region, bgr in circles:
                # Convert the original image coordinates to display coordinates
                cx = int(region.center[0] * self._scale_x)
                cy = int(region.center[1] * self._scale_y)
                r  = int(region.radius * min(self._scale_x, self._scale_y))
                # Swap BGR to RGB because numpy/PIL uses RGB channel order
                rgb = (bgr[2], bgr[1], bgr[0])
                # Draw an outer glow ring slightly larger than the main circle
                cv2.circle(orig_cv, (cx, cy), r + 5, rgb, 1)
                cv2.circle(mod_cv,  (cx, cy), r + 5, rgb, 1)
                # Draw the main circle outline around the difference region
                cv2.circle(orig_cv, (cx, cy), r,     rgb, 3)
                cv2.circle(mod_cv,  (cx, cy), r,     rgb, 3)
                # Draw a small filled dot at the exact centre of the region
                cv2.circle(orig_cv, (cx, cy), 5,     rgb, -1)
                cv2.circle(mod_cv,  (cx, cy), 5,     rgb, -1)
            # Convert the annotated numpy arrays back to PIL Images
            orig_pil = Image.fromarray(orig_cv)
            mod_pil  = Image.fromarray(mod_cv)

        # Convert both PIL images to Tkinter-compatible PhotoImage objects
        self._orig_tk = ImageTk.PhotoImage(orig_pil)
        self._mod_tk  = ImageTk.PhotoImage(mod_pil)

        # Calculate the offset to centre the image inside the canvas
        ox = (self.IMG_W - self._disp_w) // 2
        oy = (self.IMG_H - self._disp_h) // 2

        # Clear each canvas and redraw the image at the centred position
        for canvas, photo in [(self.canvas_orig, self._orig_tk),
                               (self.canvas_mod,  self._mod_tk)]:
            canvas.delete("all")
            canvas.create_image(ox, oy, anchor=tk.NW, image=photo)

    def _gather_circles(self, reveal_unfound=False):
        # Build a list of (region, colour) pairs to pass into _repaint
        circles = []
        for r in self.proc.differences:
            # Use the found colour for regions the player has already located
            if r.found:
                circles.append((r, Theme.CV_FOUND))
            # Use the reveal colour for unfound regions only when revealing all
            elif reveal_unfound:
                circles.append((r, Theme.CV_REVEAL))
        # Return None instead of an empty list so _repaint skips the drawing step
        return circles if circles else None

    # Class _on_hover
    # Changes the cursor to a crosshair when near an unfound difference region
    def _on_hover(self, event):
        # Ignore hover events if no image is loaded or the round has ended
        if self.proc.original_bgr is None or not self.state.active:
            return
        # Convert the canvas pixel position to original image coordinates
        ox, oy = self._canvas_to_img(event.x, event.y)
        # Check if the cursor is near any unfound region
        near = any(
            not r.found and r.contains_point(ox, oy, self.TOLERANCE + 8)
            for r in self.proc.differences
        )
        # Switch to a finer crosshair when near a difference, normal otherwise
        self.canvas_mod.config(cursor="tcross" if near else "crosshair")

    # Class _on_click
    # Handles a left-click on the modified canvas and checks for a correct hit
    def _on_click(self, event):
        # Ignore clicks if no image is loaded or the round is already over
        if self.proc.original_bgr is None or not self.state.active:
            return
        # Convert the canvas click position to original image coordinates
        ox, oy = self._canvas_to_img(event.x, event.y)

        # Check the click against every unfound difference region
        for region in self.proc.differences:
            # Skip regions the player has already found
            if region.found:
                continue
            # Condition: the click falls within the region's radius plus tolerance
            if region.contains_point(ox, oy, self.TOLERANCE):
                self._handle_correct(region, event.x, event.y)
                return
        # If no region was hit, count the click as a mistake
        self._handle_wrong(event.x, event.y)

    def _canvas_to_img(self, cx, cy):
        # Calculate the pixel offset used to centre the image on the canvas
        ox = (self.IMG_W - self._disp_w) // 2
        oy = (self.IMG_H - self._disp_h) // 2
        # Subtract the offset then divide by the scale to get original coordinates
        return (int((cx - ox) / self._scale_x),
                int((cy - oy) / self._scale_y))

    # Class _handle_correct
    # Called when a click successfully hits an unfound difference region
    def _handle_correct(self, region, cx, cy):
        # Mark this region as found and update the game state counters
        region.found = True
        self.state.correct()
        # Redraw both canvases with circles on all found regions
        self._repaint(self._gather_circles())
        # Play the expanding ring animation at the click position
        self._animate_success(cx, cy)
        self._refresh_status()

        # Condition: all 5 differences have been found - show the win message
        if self.state.round_complete:
            self._set_msg(
                f"All 5 found!  Total score: {self.state.total_found}",
                Theme.GOLD)
            self.after(350, lambda: messagebox.showinfo(
                "Round Complete!",
                f"You found all 5 differences!\n\n"
                f"Cumulative total: {self.state.total_found} differences found.\n\n"
                "Load a new image to keep playing."))
        # Condition: round still in progress - show remaining count
        else:
            self._set_msg(
                f"Found! {self.state.remaining} remaining  ·  "
                f"{self.state.mistakes_left} chances left",
                Theme.EMERALD)

    # Class _handle_wrong
    # Called when a click misses all difference regions
    def _handle_wrong(self, cx, cy):
        # Register the mistake and update the game state
        self.state.wrong()
        # Draw a red X at the click position to indicate a wrong guess
        self._animate_wrong(cx, cy)
        self._refresh_status()

        # Condition: player has used all 3 mistakes - end the round
        if self.state.game_over:
            # Reveal all unfound differences in orange
            self._repaint(self._gather_circles(reveal_unfound=True))
            self._set_msg(
                f"Too many mistakes -- found {self.state.found_this_round}/5",
                Theme.CRIMSON)
            self.after(350, lambda: messagebox.showwarning(
                "Too Many Mistakes",
                f"You made 3 mistakes!\n\n"
                f"You found {self.state.found_this_round} of 5 differences.\n\n"
                "Remaining differences are shown in orange.\n"
                "Load a new image to try again."))
        # Condition: round still active - show how many chances remain
        else:
            self._set_msg(
                f"Wrong!  {self.state.mistakes_left} "
                f"{'chance' if self.state.mistakes_left == 1 else 'chances'} remaining",
                Theme.CRIMSON)

    # Class _reveal_all
    # Called when the player clicks Reveal All - shows all unfound differences
    def _reveal_all(self):
        # Show an error if the player clicks reveal before loading an image
        if self.proc.original_bgr is None:
            self._set_msg("Load an image first.", Theme.CRIMSON)
            return
        # Ask the player to confirm before revealing the answers
        if not messagebox.askyesno("Reveal All",
                                    "Reveal all unfound differences?\n"
                                    "The round will end."):
            return
        # End the round and draw orange circles on all unfound regions
        self.state.game_over = True
        self._repaint(self._gather_circles(reveal_unfound=True))
        self._set_msg(
            "All differences revealed in orange -- load a new image to play.",
            Theme.COBALT)
        self._refresh_status()

    # Class _animate_success
    # Draws an expanding ring that fades out over several frames
    def _animate_success(self, cx, cy, step=0):
        TAG = "anim_ok"
        # Clear any previous frame of this animation from the canvas
        self.canvas_mod.delete(TAG)
        # Stop the animation after 8 frames
        if step > 7:
            return
        # Increase the ring radius with each frame to create the expansion effect
        r = 12 + step * 9
        # Define a sequence of darkening shades to simulate the ring fading out
        shades = ["#2ec4b6", "#29b0a3", "#228e83", "#1a6c64",
                  "#124c47", "#0b2e2b", "#051615", "#000000"]
        colour = shades[min(step, len(shades)-1)]
        # Draw the ring at the current radius
        self.canvas_mod.create_oval(cx-r, cy-r, cx+r, cy+r,
                                     outline=colour, width=2, tags=TAG)
        # Schedule the next frame to run after 40 milliseconds
        self.after(40, lambda: self._animate_success(cx, cy, step + 1))

    # Class _animate_wrong
    # Draws a red X at the click position and removes it after 0.5 seconds
    def _animate_wrong(self, cx, cy):
        TAG = "anim_no"
        s = 13
        # Remove any existing wrong animation before drawing the new one
        self.canvas_mod.delete(TAG)
        # Draw the two diagonal lines that form the X shape
        self.canvas_mod.create_line(cx-s, cy-s, cx+s, cy+s,
                                     fill=Theme.CRIMSON, width=3, tags=TAG)
        self.canvas_mod.create_line(cx+s, cy-s, cx-s, cy+s,
                                     fill=Theme.CRIMSON, width=3, tags=TAG)
        # Schedule the X to be removed from the canvas after 500 milliseconds
        self.after(500, lambda: self.canvas_mod.delete(TAG))

    # Class _refresh_status
    # Updates the three counter labels in the status bar
    def _refresh_status(self):
        # Show dashes if no image has been loaded yet
        if self.proc.original_bgr is None:
            self._var_remaining.set("--")
            self._var_mistakes.set("0 / 3")
            self._var_score.set(str(self.state.total_found))
            return
        # Update the remaining and mistakes counters from the current game state
        self._var_remaining.set(str(self.state.remaining))
        self._var_mistakes.set(f"{self.state.mistakes} / {GameState.MAX_MISTAKES}")
        self._var_score.set(str(self.state.total_found))

    def _set_msg(self, text, colour=None):
        # Update the status message text and change its colour for the feedback type
        self._var_msg.set(text)
        self.lbl_msg.config(fg=colour or Theme.TEXT_PRIMARY)

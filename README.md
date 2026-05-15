# Spot the Difference – HIT137 Group Assignment 3

Welcome to "Spot the Difference" – a Python application built with Tkinter and OpenCV. In this game, an image is loaded, and the program automatically generates 5 hidden alterations on a duplicate image. Your goal is to click the right-hand image to find the hidden differences without exceeding the maximum mistake limit!

## Features
- **Dynamic Alteration:** Programs inject random modifications to the image including colour shifts, brightness adjustments, and blurring.
- **Graphical User Interface:** Minimalistic, dark-themed UI built elegantly using Python's native `tkinter` library.
- **Score & Mistake Tracking:** Tracks running totals visually.

---

## 🛠️ Prerequisites & Setup

### 1. Requirements
This game requires **Python 3**. You will also need to install the extra image-processing libraries. We have provided a `requirements.txt` to make this easy.

### 2. Installation
Open your terminal/command prompt, traverse to the game directory, and run the following command to securely install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 🎮 How to Play

### Starting the Game
Run the following command within the project directory to launch the Graphical Interface:
```bash
python3 main.py
```

### Game Rules
1. Click the **Load Image** button at the top right to start a round. Choose any standard image file (e.g., .jpg, .png).
2. Two copies of the image will be displayed:
   - **Left Panel (ORIGINAL):** Your reference image.
   - **Right Panel (MODIFIED):** The altered copy containing the **5 hidden differences**.
3. Study the original, and **click on the Modified panel** where you spot a difference. 
   - A correct click will draw an expanding ring and be permanently marked!
   - An incorrect click yields a red 'X'.
4. **Mistakes:** You are only allowed **3 mistakes** per round. Proceed with caution.
5. Win by spotting all 5 changes! Load another image to keep the score rolling.

*(Note: At any time, you can click the `Reveal All` button to instantly force-show all missing answers.)*

---

## 📂 File Architecture
This application is designed in a highly modular, Object-Oriented structure:
- **`main.py`** – Clean entry point to run the program.
- **`app.py`** – Features the comprehensive `SpotTheDifferenceApp` holding all structural UI rules and events.
- **`processor.py`** – The OpenCV logic used to duplicate, slice, blur, and colour-shift the regions automatically.
- **`region.py`** – Tracks sizes and geometric coordinates of differences and determines if user clicks overlap correctly.
- **`state.py`** – Maintains internal scoring metrics during and between rounds.
- **`theme.py`** – Cleanly contains all colour hex codes allowing for swift design changes application-wide.

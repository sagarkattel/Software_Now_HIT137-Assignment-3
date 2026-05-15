# Class Theme - holds all colour and layout constants used across the application
class Theme:
    # Background colours for each section of the window
    BG_BASE    = "#0e1117"
    BG_PANEL   = "#161b27"
    BG_HEADER  = "#1a2133"
    BG_STATUS  = "#111827"

    # Accent colours used for feedback and highlights
    GOLD       = "#f5c842"
    CRIMSON    = "#e63946"
    EMERALD    = "#2ec4b6"
    COBALT     = "#4361ee"

    # Text colours from brightest to most faded
    TEXT_PRIMARY   = "#f0f4ff"
    TEXT_SECONDARY = "#8899b0"
    TEXT_MUTED     = "#3d4f68"

    # Circle colours for OpenCV drawing stored as BGR tuples
    CV_FOUND  = (182, 196, 46)
    CV_REVEAL = (238, 161, 67)

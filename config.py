config = {
    "monitor": {
        "width_cm": 31.26,
        "viewing_distance_cm": 57,
        "resolution_px": [1512, 982],
    },
    "display": {
        "screen": 0,
        "units": "deg",
        "bg_color": "black",
        "full_screen": True,
        "center_deg": [0, 0],
        "allow_gui": False,
        "mouse_visible": False,
    },
    "wolf": {
        "count": 8,
        "speed": 0.1,
        "color": "red",
        "size": 1.5,
        "vertices": [
            (-0.5, -0.5),  # Bottom-left
            (0, 0.5),  # Top-center (point of the chevron)
            (0.5, -0.5),  # Bottom-right
            (0, -0.2),  # Inner bottom-center
            (-0.5, -0.5),  # Back to start to close the shape
        ],
        "direction_noise": 0.1,
    },
    "sheep": {
        "color": "white",
        "radius": 0.5,
    },
    "keys": {
        "quit": ["escape"],
        "toggle_condition": ["space"],
    },
}

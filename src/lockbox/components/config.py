import sv_ttk

class Config:
    # Window settings
    WINDOW_TITLE = "LockBox"
    DEFAULT_WIDTH = 600
    DEFAULT_HEIGHT = 450
    RESIZABLE = (True, True)  # (width_resizable, height_resizable)

    # Themes and Styles
    THEME = {
        "background": "#f0f0f0",  # Light gray background
        "foreground": "#000000",  # Black text
        "button_background": "#0078D7",  # Blue button color
        "button_foreground": "#ffffff",  # White button text
        "entry_background": "#ffffff",  # Entry field background
        "entry_foreground": "#000000",  # Entry field text
        "theme": "light",
    }

    # Fonts
    FONTS = {
        "heading": ("Helvetica", 16, "bold"),
        "subheading": ("Helvetica", 14),
        "body": ("Helvetica", 12),
        "button": ("Helvetica", 12, "bold"),
    }

    @staticmethod
    def apply_config(window):
        """Apply the configuration settings to the given Tkinter window."""
        window.title(Config.WINDOW_TITLE)
        window.geometry(f"{Config.DEFAULT_WIDTH}x{Config.DEFAULT_HEIGHT}")
        window.resizable(*Config.RESIZABLE)
        window.configure(bg=Config.THEME["background"])
        sv_ttk.set_theme(Config.THEME["theme"])

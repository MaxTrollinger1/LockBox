import sv_ttk

class LBConfig:
    # Window settings
    WINDOW_TITLE = "LockBox"
    #ICON = "src/assets/m_icon.ico"
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
        window.title(LBConfig.WINDOW_TITLE)
        window.geometry(f"{LBConfig.DEFAULT_WIDTH}x{LBConfig.DEFAULT_HEIGHT}")
        window.resizable(*LBConfig.RESIZABLE)
        window.configure(bg=LBConfig.THEME["background"])
        #window.iconbitmap(LBConfig.ICON)
        sv_ttk.set_theme(LBConfig.THEME["theme"])

from pathlib import Path
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

# Get the absolute path to the UI directory regardless of where the script is run from
UI_DIR = Path(__file__).parent.absolute()
ICON_PATH_ROOT = UI_DIR / "Resources" / "Icon"

def safe_load_icon(icon_path):
    """
    Safely load an icon with fallback handling.
    
    Args:
        icon_path (str): Relative path to the icon file within the Icon directory
        
    Returns:
        QIcon: The loaded icon or an empty icon if loading failed
    """
    try:
        # Use pathlib for proper path handling across operating systems
        icon_full_path = ICON_PATH_ROOT / icon_path
        
        # Check if icon file exists
        if not icon_full_path.exists():
            print(f"WARNING: Icon file does not exist: {icon_full_path}")
            print(f"Icon directory: {ICON_PATH_ROOT}")
            if ICON_PATH_ROOT.exists():
                print(f"Available icons in directory:")
                for icon_file in ICON_PATH_ROOT.glob("**/*.svg"):
                    relative_path = icon_file.relative_to(ICON_PATH_ROOT)
                    print(f"  - {relative_path}")
            else:
                print(f"Icon directory does not exist!")
            return QIcon()  # Return empty icon
        
        # Check if icon file is readable
        if not icon_full_path.is_file():
            print(f"WARNING: Icon path exists but is not a file: {icon_full_path}")
            return QIcon()
            
        # Load and return the icon
        icon = QIcon(str(icon_full_path))
        
        # Verify the icon loaded successfully
        if icon.isNull():
            print(f"WARNING: Failed to load icon from {icon_full_path} (icon is null)")
            return QIcon()
        
        return icon
        
    except Exception as e:
        print(f"ERROR: Exception while loading icon {icon_path}: {e}")
        print(f"UI Directory: {UI_DIR}")
        print(f"Icon Root Directory: {ICON_PATH_ROOT}")
        return QIcon()

def add_new_button(buttons, icon_path=None, width=30, height=30, icon_size=20):
    """
    Add icon and size to a button with safe icon loading.
    
    Args:
        buttons: The QPushButton to configure
        icon_path (str): Relative path to the icon file
        size (int): Button size (width and height)
        icon_size (int): Icon size within the button
    """
    buttons.setFixedSize(width, height)
    setButtonIcon(buttons, icon_path, icon_size)

def setButtonIcon(buttons, icon_path, icon_size):
    """
    Set the icon for a button with safe icon loading.
    
    Args:
        buttons: The QPushButton to set icon for
        icon_path (str): Relative path to the icon file
        icon_size (int): Icon size within the button
    """
    icon = safe_load_icon(icon_path)
    buttons.setIcon(icon)
    buttons.setIconSize(QSize(icon_size, icon_size))


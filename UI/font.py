from pathlib import Path
from PyQt5.QtGui import QFont, QFontDatabase

# Get the absolute path to the UI directory regardless of where the script is run from
UI_DIR = Path(__file__).parent.absolute()
FONT_PATH_ROOT = UI_DIR / "Resources" / "Font"

def load_new_font(font_path):
    """
    Load a custom font from the Resources/Font directory.
    
    Args:
        font_path (str): Relative path to the font file within the Font directory
        
    Returns:
        QFont: The loaded font object, or None if loading failed
    """
    try:
        # Use pathlib for proper path handling across operating systems
        font_full_path = FONT_PATH_ROOT / font_path
        
        print(f"Attempting to load font from: {font_full_path}")
        
        # Check if font file exists
        if not font_full_path.exists():
            print(f"ERROR: Font file does not exist: {font_full_path}")
            print(f"Font directory contents: {list(FONT_PATH_ROOT.glob('**/*')) if FONT_PATH_ROOT.exists() else 'Directory does not exist'}")
            return None
        
        # Check if font file is readable
        if not font_full_path.is_file():
            print(f"ERROR: Path exists but is not a file: {font_full_path}")
            return None
            
        # Load the font
        font_id = QFontDatabase.addApplicationFont(str(font_full_path))
        
        if font_id == -1:
            print(f"ERROR: Failed to load font from {font_full_path}")
            print("This could be due to:")
            print("  - Corrupted font file")
            print("  - Unsupported font format")
            print("  - Insufficient permissions")
            return None
        else:
            # Get the font family name
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if not font_families:
                print(f"WARNING: Font loaded but no families found for {font_full_path}")
                return None
                
            font_family = font_families[0]
            print(f"✓ Successfully loaded font family: {font_family}")
            
            # Create and return the custom font
            custom_font = QFont(font_family, 16)
            return custom_font
            
    except Exception as e:
        print(f"ERROR: Exception while loading font {font_path}: {e}")
        print(f"UI Directory: {UI_DIR}")
        print(f"Font Root Directory: {FONT_PATH_ROOT}")
        return None

def get_fallback_font():
    """
    Get a fallback font in case custom fonts fail to load.
    
    Returns:
        QFont: A system font as fallback
    """
    fallback_font = QFont("Arial", 16)  # Common system font
    if not fallback_font.family():
        fallback_font = QFont("Sans Serif", 16)  # Generic fallback
    print(f"Using fallback font: {fallback_font.family()}")
    return fallback_font

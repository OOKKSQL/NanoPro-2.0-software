# Copyright Danial Lab (Siqi Liu and John Danial)
# UI Styling Constants
# Compatible with NanoPro 2.0 and ALBA
class Colors:
    """Light theme color palette - Based on Carbon Design System White Theme"""

    # Background colors
    BACKGROUND_MAIN = "#FFFFFF"
    BACKGROUND_BUTTON = "#F4F4F4"
    BACKGROUND_BUTTON_CLOSE = "#161616"
    BACKGROUND_BUTTON_CLOSE_HOVER = "#da1e28"
    BACKGROUND_BUTTON_MINIMISE = "#F4F4F4"
    BACKGROUND_BUTTON_HOVER = "#F4F4F4"
    BACKGROUND_BUTTON_SELECTED = "#161616"
    BACKGROUND_GROUP_BOX = "#F4F4F4"
    BACKGROUND_IMAGE = "#FFFFFF"
    
    # Text colors
    TEXT = "#161616"
    TEXT_LABEL = "#161616"

    BORDER = "#161616"
    BORDER_CHECKED = "#161616"

class Dimensions:
    """Size constants for UI elements"""

    # Base size
    BASE_SIZE = 40

    # Line width
    LINE_WIDTH = 1

    # Spacing
    MAJOR_SPACING = BASE_SIZE // 2
    MINOR_SPACING = BASE_SIZE // 4

    # Button and icon
    BUTTON_SIZE = BASE_SIZE
    ICON_SIZE = BASE_SIZE // 2

    # Text box
    TEXT_BOX_WIDTH = BASE_SIZE * 6
    TEXT_BOX_HEIGHT = BASE_SIZE

    # Label
    LABEL_HEIGHT = TEXT_BOX_HEIGHT

    # Group box
    GROUP_BOX_WIDTH = TEXT_BOX_WIDTH
    GROUP_BOX_HEIGHT = TEXT_BOX_HEIGHT + LABEL_HEIGHT

    # Margin
    MARGIN = BASE_SIZE // 2

    # Image / plot area
    SMALL_IMAGE_SIZE = (BASE_SIZE * 6) - (MINOR_SPACING // 2)
    LARGE_IMAGE_SIZE = BASE_SIZE * 12

    # Layout dimensions
    BAR_3_WIDTH = GROUP_BOX_WIDTH
    BAR_4_WIDTH = MAJOR_SPACING + LARGE_IMAGE_SIZE + MINOR_SPACING + SMALL_IMAGE_SIZE
    BAR_3_HEIGHT = LARGE_IMAGE_SIZE
    BAR_5_HEIGHT = MAJOR_SPACING + BUTTON_SIZE
    BAR_0_HEIGHT = BUTTON_SIZE

    # Window dimensions
    WINDOW_WIDTH = (2 * MARGIN) + BAR_3_WIDTH + BAR_4_WIDTH
    WINDOW_HEIGHT = (2 * MARGIN) + BAR_0_HEIGHT + MAJOR_SPACING + BAR_3_HEIGHT + BAR_5_HEIGHT
    WINDOW_X = 100
    WINDOW_Y = 100

class Typography:
    """Font and text styling constants"""
    # Font families (using the IBM Plex fonts you set up)
    FONT_FAMILY_REGULAR = "ibm-plex/IBMPlexSans-Regular.ttf"
    
    # Font size
    FONT_SIZE = "16px"
    FONT_SIZE_SMALL = "12px"
    
class Borders:
    """Border styling constants"""

    # Border radius
    RADIUS = "20px"

    # Border radius group box
    RADIUS_GROUP_BOX = "40px"

def get_style(component):
    """Generate button stylesheet for given theme"""

    if component == "button":
        return f"""
            QPushButton {{
                background-color: {Colors.BACKGROUND_BUTTON};
                border-radius: {Borders.RADIUS};
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BACKGROUND_BUTTON_HOVER};
                border: {Dimensions.LINE_WIDTH} solid {Colors.BORDER};
                border-radius: {Borders.RADIUS};
                padding: 0px;
            }}
            QPushButton:checked {{
                background-color: {Colors.BACKGROUND_BUTTON_SELECTED};
                border: {Dimensions.LINE_WIDTH} solid {Colors.BORDER_CHECKED};
                border-radius: {Borders.RADIUS};
                padding: 0px;
            }}
        """
    if component == "power_button":
        return f"""
            QPushButton {{
                background-color: {Colors.BACKGROUND_BUTTON};
                border-radius: {Borders.RADIUS};
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BACKGROUND_BUTTON_HOVER};
                border: {Dimensions.LINE_WIDTH} solid {Colors.BORDER};
                border-radius: {Borders.RADIUS};
                padding: 0px;
            }}
            QPushButton:checked {{
                background-color: {Colors.BACKGROUND_BUTTON_SELECTED};
                border-radius: {Borders.RADIUS};
                padding: 0px;
            }}
        """
    if component == "close_button":
        return f"""
            QPushButton {{
                background-color: {Colors.BACKGROUND_BUTTON_CLOSE};
                border-radius: {Borders.RADIUS};
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BACKGROUND_BUTTON_CLOSE_HOVER};
                border-radius: {Borders.RADIUS};
                padding: 0px;
            }}
        """
    if component == "minimise_button":
        return f"""
            QPushButton {{
                background-color: {Colors.BACKGROUND_BUTTON_MINIMISE};
                border-radius: {Borders.RADIUS};
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BACKGROUND_BUTTON_MINIMISE};
                border: {Dimensions.LINE_WIDTH} solid {Colors.BORDER};
                border-radius: {Borders.RADIUS};
                padding: 0px;
            }}
        """
    if component == "text_box":
        return f"""
            QLineEdit {{
                background-color: transparent;
                color: {Colors.TEXT};
                font-size: {Typography.FONT_SIZE};
                padding: 0px;
                border: 0px;
                margin: 0px;
            }}
        """
    if component == "label":
        return f"""
            QLabel {{
                background-color: transparent;
                color: {Colors.TEXT_LABEL};
                font-size: {Typography.FONT_SIZE_SMALL};
                padding: 0px;
                border: 0px;
                margin: 0px;
            }}
        """
    if component == "group_box":
        return f"""
            QGroupBox {{
                background-color: {Colors.BACKGROUND_GROUP_BOX};
                border: {Dimensions.LINE_WIDTH} solid transparent;
                border-radius: {Borders.RADIUS_GROUP_BOX};
                padding: 0px;
                margin: 0px;
            }}
            QGroupBox:hover {{
                background-color: {Colors.BACKGROUND_GROUP_BOX};
                border: {Dimensions.LINE_WIDTH} solid {Colors.BORDER};
                border-radius: {Borders.RADIUS_GROUP_BOX};
                padding: 0px;
                margin: 0px;
            }}
        """
    if component == "image":
        return f"""
            QLabel {{
                background-color: {Colors.BACKGROUND_IMAGE};
                border: {Dimensions.LINE_WIDTH} solid {Colors.BORDER};
                border-radius: {Borders.RADIUS};
                padding: 0px;
                margin: 0px;
                overflow: hidden;
            }}
        """

def get_icon_path(icon_name):
    """Get icon path based on theme"""
    return f"light/{icon_name}"

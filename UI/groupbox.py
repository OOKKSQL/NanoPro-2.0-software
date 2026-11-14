from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QGroupBox
from styles import (Dimensions, Colors, Borders)

class HoverAwareGroupBox(QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)
        self.setStyleSheet(f"""
            QGroupBox {{
                background-color: {Colors.BACKGROUND_GROUP_BOX};
                border: {Dimensions.LINE_WIDTH} solid transparent;
                border-radius: {Borders.RADIUS_GROUP_BOX};
                padding: 0px;
                margin: 0px;
            }}
        """)

    def event(self, e):
        if e.type() == QEvent.HoverEnter:
            self.setStyleSheet(f"""
                QGroupBox {{
                    background-color: {Colors.BACKGROUND_GROUP_BOX};
                    border: {Dimensions.LINE_WIDTH} solid {Colors.BORDER};
                    border-radius: {Borders.RADIUS_GROUP_BOX};
                    padding: 0px;
                    margin: 0px;
                }}
            """)
        elif e.type() == QEvent.HoverLeave:
            self.setStyleSheet(f"""
                QGroupBox {{
                    background-color: {Colors.BACKGROUND_GROUP_BOX};
                    border: {Dimensions.LINE_WIDTH} solid transparent;
                    border-radius: {Borders.RADIUS_GROUP_BOX};
                    padding: 0px;
                    margin: 0px;
                }}
            """)
        return super().event(e)

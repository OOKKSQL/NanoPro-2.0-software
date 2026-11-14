import json
import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QPainter, QPainterPath, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QScrollArea, QStackedLayout,
    QVBoxLayout, QWidget,
)

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from button import add_new_button, setButtonIcon
from font import get_fallback_font, load_new_font
from groupbox import HoverAwareGroupBox
from image import add_new_image
from styles import Borders, Colors, Dimensions, Typography, get_icon_path, get_style
from Acquire.Microscope.Microscope_Functions import MICROSCOPE, MicroscopeOperationWorker


PARAMETERS_PATH = project_root / "Setting" / "Default_parameters.json"
SETTINGS_PATH = project_root / "Setting" / "Local_setting.json"
SIMPULL_FIELDS = (
    ("uv_laser_power", "UV laser power [%]", "laser_uv_power"),
    ("blue_laser_power", "Blue laser power [%]", "laser_blue_power"),
    ("green_laser_power", "Green laser power [%]", "laser_green_power"),
    ("red_laser_power", "Red laser power [%]", "laser_red_power"),
    ("exposure_time", "Exposure time [ms]", "camera_im_exp_time"),
    ("number_of_frames", "Number of frames", "camera_im_num_frames"),
    ("number_of_acquisitions", "Number of acquisitions", "camera_im_num_acquisitions"),
)
STAGE_BUTTONS = (
    ("increase_speed", "increase_speed", 0, 0),
    ("up", "move_up", 0, 1),
    ("left", "move_left", 0, 2),
    ("front", "move_front", 0, 3),
    ("decrease_speed", "decrease_speed", 1, 0),
    ("down", "move_down", 1, 1),
    ("right", "move_right", 1, 2),
    ("back", "move_back", 1, 3),
)


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.microscope = MICROSCOPE()
        self.microscope_connected = False
        self.simpull_parameters_valid = False
        self._drag_offset = None
        self.parameter_inputs = {}
        self._build_ui()
        self._load_parameters()
        self._load_export_path()
        self.apply_simpull_parameters()

    def _icon_button(self, name, checkable=False, style="button"):
        button = QPushButton()
        add_new_button(
            button, get_icon_path(f"{name}.svg"),
            width=Dimensions.BUTTON_SIZE, height=Dimensions.BUTTON_SIZE,
            icon_size=Dimensions.ICON_SIZE,
        )
        button.setCheckable(checkable)
        button.setStyleSheet(get_style(style))
        return button

    def _set_button_icon(self, button, name, active):
        suffix = "_white" if active else ""
        setButtonIcon(button, get_icon_path(f"{name}{suffix}.svg"), Dimensions.ICON_SIZE)

    def _parameter_group(self, label_text, input_widget):
        group = HoverAwareGroupBox()
        group.setFixedSize(Dimensions.GROUP_BOX_WIDTH, Dimensions.GROUP_BOX_HEIGHT)
        group.setStyleSheet(get_style("group_box"))
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(get_style("label"))
        label.setFixedHeight(label.sizeHint().height())
        input_widget.setStyleSheet(get_style("text_box"))
        input_widget.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addSpacing(Dimensions.MINOR_SPACING)
        layout.addWidget(input_widget)
        layout.addStretch(1)
        return group

    def _image(self, width, height):
        image = QLabel()
        image.setAlignment(Qt.AlignCenter)
        add_new_image(image, width=width, height=height)
        image.setStyleSheet(get_style("image"))
        return image

    def _image_panel(self, image, bottom_controls=None):
        panel = QWidget()
        panel.setFixedSize(image.size())
        stack = QStackedLayout(panel)
        stack.setContentsMargins(0, 0, 0, 0)
        stack.setStackingMode(QStackedLayout.StackAll)
        stack.addWidget(image)
        if bottom_controls is not None:
            overlay = QWidget()
            overlay.setStyleSheet("background: transparent;")
            layout = QVBoxLayout(overlay)
            layout.setContentsMargins(
                Dimensions.MINOR_SPACING, 0, Dimensions.MINOR_SPACING,
                Dimensions.MINOR_SPACING,
            )
            layout.addStretch()
            layout.addLayout(bottom_controls)
            stack.addWidget(overlay)
            stack.setCurrentWidget(overlay)
        return panel

    def _build_ui(self):
        self.setWindowTitle("ALBA")
        self.setGeometry(
            Dimensions.WINDOW_X, Dimensions.WINDOW_Y,
            Dimensions.WINDOW_WIDTH, Dimensions.WINDOW_HEIGHT,
        )
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        container = QWidget()
        container.setStyleSheet(
            f"background-color: {Colors.BACKGROUND_MAIN}; border-radius: {Borders.RADIUS};"
        )
        self.setCentralWidget(container)
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(
            Dimensions.MARGIN, Dimensions.MARGIN,
            Dimensions.MARGIN, Dimensions.MARGIN,
        )
        main_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedHeight(Dimensions.BAR_0_HEIGHT)
        header_widget.mousePressEvent = self._start_header_drag
        header_widget.mouseMoveEvent = self._move_header_drag
        header_widget.mouseReleaseEvent = self._stop_header_drag
        header = QHBoxLayout(header_widget)
        header.setContentsMargins(0, 0, 0, 0)
        header.addStretch()
        self.bar_0_power_button = self._icon_button("bar_0_power_button", True, "power_button")
        self.bar_0_minimise_button = self._icon_button("bar_0_minimise_button", style="minimise_button")
        self.bar_0_close_button = self._icon_button("bar_0_close_button", style="close_button")
        self.bar_0_power_button.toggled.connect(self._toggle_power)
        self.bar_0_minimise_button.clicked.connect(self.showMinimized)
        self.bar_0_close_button.clicked.connect(self.close)
        for button in (
            self.bar_0_power_button, self.bar_0_minimise_button, self.bar_0_close_button,
        ):
            header.addWidget(button)
        header.setSpacing(Dimensions.MINOR_SPACING)
        main_layout.addWidget(header_widget)
        main_layout.addSpacing(Dimensions.MAJOR_SPACING)

        content = QHBoxLayout()
        content.setSpacing(0)
        parameters_scroll = QScrollArea()
        parameters_scroll.setFixedSize(Dimensions.BAR_3_WIDTH, Dimensions.BAR_3_HEIGHT)
        parameters_scroll.setWidgetResizable(True)
        parameters_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        parameters_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        parameters_scroll.setStyleSheet("border: none; background: transparent;")
        parameters_widget = QWidget()
        parameters_layout = QVBoxLayout(parameters_widget)
        parameters_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        parameters_layout.setContentsMargins(0, 0, 0, 0)
        parameters_layout.setSpacing(Dimensions.MINOR_SPACING)

        self.export_path_display = QLineEdit()
        self.export_path_display.setReadOnly(True)
        self.export_path_display.setCursor(Qt.PointingHandCursor)
        self.export_path_display.mousePressEvent = lambda _event: self.choose_export_folder()
        parameters_layout.addWidget(self._parameter_group("Export folder", self.export_path_display))

        for key, label, _ in SIMPULL_FIELDS:
            field = QLineEdit()
            self.parameter_inputs[key] = field
            parameters_layout.addWidget(self._parameter_group(label, field))
        self.bar_3_acquire_save_button = self._icon_button("bar_3_acquire_save_button")
        self.bar_3_acquire_save_button.clicked.connect(self.save_current_parameters)
        parameters_layout.addWidget(self.bar_3_acquire_save_button, alignment=Qt.AlignHCenter)
        parameters_scroll.setWidget(parameters_widget)
        content.addWidget(parameters_scroll)
        content.addSpacing(Dimensions.MAJOR_SPACING)

        self.bar_4_main_image = self._image(Dimensions.LARGE_IMAGE_SIZE, Dimensions.LARGE_IMAGE_SIZE)
        self.bar_4_top_right_image = self._image(Dimensions.SMALL_IMAGE_SIZE, Dimensions.SMALL_IMAGE_SIZE)

        main_controls = QHBoxLayout()
        main_controls.setSpacing(Dimensions.MINOR_SPACING)
        self.bar_4_acquire_live_button = self._icon_button("bar_4_acquire_live_button", True)
        self.bar_4_acquire_record_button = self._icon_button("bar_4_acquire_record_button", True)
        self.bar_4_acquire_live_button.toggled.connect(self._toggle_live)
        self.bar_4_acquire_record_button.toggled.connect(self._toggle_record)
        main_controls.addWidget(self.bar_4_acquire_live_button, alignment=Qt.AlignBottom)
        main_controls.addWidget(self.bar_4_acquire_record_button, alignment=Qt.AlignBottom)
        main_controls.addStretch()
        stage_grid = QGridLayout()
        stage_grid.setSpacing(Dimensions.MINOR_SPACING)
        self.stage_buttons = []
        for short_name, microscope_attr, row, column in STAGE_BUTTONS:
            name = f"bar_4_acquire_{short_name}_button"
            button = self._icon_button(name)
            button.pressed.connect(
                lambda attr=microscope_attr, b=button, n=name: self._stage_press(attr, b, n)
            )
            button.released.connect(
                lambda attr=microscope_attr, b=button, n=name: self._stage_release(attr, b, n)
            )
            stage_grid.addWidget(button, row, column)
            self.stage_buttons.append(button)
        main_controls.addLayout(stage_grid)
        main_panel = self._image_panel(self.bar_4_main_image, main_controls)

        focus_controls = QHBoxLayout()
        self.bar_4_acquire_lock_focus_button = self._icon_button(
            "bar_4_acquire_lock_focus_button", True,
        )
        self.bar_4_acquire_lock_focus_button.toggled.connect(self._toggle_focus)
        focus_controls.addWidget(self.bar_4_acquire_lock_focus_button)
        focus_controls.addStretch()
        right_panels = QVBoxLayout()
        right_panels.setContentsMargins(0, 0, 0, 0)
        right_panels.setAlignment(Qt.AlignTop)
        right_panels.addWidget(self._image_panel(self.bar_4_top_right_image, focus_controls))
        images = QHBoxLayout()
        images.setSpacing(Dimensions.MINOR_SPACING)
        images.addWidget(main_panel)
        images.addLayout(right_panels)
        content.addLayout(images)
        content.addStretch()
        main_layout.addLayout(content)

        status_widget = QWidget()
        status_widget.setFixedHeight(Dimensions.BAR_5_HEIGHT)
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setAlignment(Qt.AlignBottom)
        self.message_label = QLabel("Welcome to ALBA. Switch on the microscope to start.")
        self.message_label.setStyleSheet(
            f"font-size: {Typography.FONT_SIZE}; color: {Colors.TEXT_LABEL};"
        )
        status_layout.addWidget(self.message_label)
        main_layout.addWidget(status_widget)
        self._update_controls()

    def _load_parameters(self):
        try:
            data = json.loads(PARAMETERS_PATH.read_text(encoding="utf-8"))
            parameters = data["simpull"]
            for key, _, _ in SIMPULL_FIELDS:
                self.parameter_inputs[key].setText(str(parameters[key]))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self.display_message(f"Could not load SiMPULL parameters: {exc}")

    def apply_simpull_parameters(self):
        try:
            values = {key: int(self.parameter_inputs[key].text()) for key, _, _ in SIMPULL_FIELDS}
        except ValueError:
            self.simpull_parameters_valid = False
            self._update_controls()
            self.display_message("Error: Invalid SiMPULL parameters")
            return False
        for key, _, microscope_attr in SIMPULL_FIELDS:
            setattr(self.microscope, microscope_attr, values[key])
        self.simpull_parameters_valid = True
        self._update_controls()
        return True

    def save_current_parameters(self):
        if not self.apply_simpull_parameters():
            return
        parameters = {key: self.parameter_inputs[key].text() for key, _, _ in SIMPULL_FIELDS}
        try:
            PARAMETERS_PATH.write_text(
                json.dumps({"simpull": parameters}, indent=2), encoding="utf-8",
            )
        except OSError as exc:
            self.display_message(f"Could not save SiMPULL parameters: {exc}")
            return
        self.display_message("Saved SiMPULL defaults")

    def _read_settings(self):
        try:
            return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}

    def _load_export_path(self):
        try:
            settings = self._read_settings()
            folder = str(settings.get("export_path", ""))
        except (OSError, ValueError, AttributeError) as exc:
            self.display_message(f"Could not load export folder: {exc}")
            folder = ""
        self.microscope.save_folder_path = folder
        self.export_path_display.setText(Path(folder).name or folder)
        self.export_path_display.setToolTip(folder)
        self._update_controls()
        if not self._export_folder_valid():
            self.display_message("Choose a valid export folder before recording")

    def _export_folder_valid(self):
        folder = self.microscope.save_folder_path
        return bool(folder) and Path(folder).is_dir()

    def choose_export_folder(self):
        previous = self.microscope.save_folder_path
        folder = QFileDialog.getExistingDirectory(self, "Choose Export Folder", previous)
        if not folder:
            return
        if not Path(folder).is_dir():
            self.display_message("Export folder does not exist")
            return
        try:
            settings = self._read_settings()
            settings["export_path"] = folder
            pending = SETTINGS_PATH.with_name(SETTINGS_PATH.name + ".tmp")
            pending.write_text(json.dumps(settings, indent=2), encoding="utf-8")
            pending.replace(SETTINGS_PATH)
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            self.display_message(f"Could not save export folder: {exc}")
            return
        self.microscope.save_folder_path = folder
        self.export_path_display.setText(Path(folder).name or folder)
        self.export_path_display.setToolTip(folder)
        self._update_controls()
        self.display_message("Export folder saved")

    def _update_controls(self):
        enabled = self.microscope_connected and self.simpull_parameters_valid
        self.bar_4_acquire_live_button.setEnabled(enabled)
        self.bar_4_acquire_lock_focus_button.setEnabled(enabled)
        for button in self.stage_buttons:
            button.setEnabled(enabled)
        self.bar_4_acquire_record_button.setEnabled(
            enabled and (self._export_folder_valid() or self.bar_4_acquire_record_button.isChecked())
        )

    def _toggle_power(self, checked):
        self._set_button_icon(self.bar_0_power_button, "bar_0_power_button", checked)
        if checked:
            self.open_microscope()
        else:
            self.close_microscope()

    def _toggle_live(self, checked):
        self._set_button_icon(self.bar_4_acquire_live_button, "bar_4_acquire_live_button", checked)
        self.microscope.display = checked
        self.display_message("Live display" if checked else "Ready")

    def _toggle_record(self, checked):
        if checked and not self._export_folder_valid():
            self.bar_4_acquire_record_button.setChecked(False)
            self.display_message("Choose a valid export folder before recording")
            return
        self._set_button_icon(self.bar_4_acquire_record_button, "bar_4_acquire_record_button", checked)
        self.microscope.acquire = checked
        self.display_message("Recording" if checked else "Ready")

    def _toggle_focus(self, checked):
        if checked:
            current = self.microscope.focus_current
            if current is None or isinstance(current, bool) or len(current) == 0:
                self.bar_4_acquire_lock_focus_button.setChecked(False)
                self.display_message("Focus reading is not available")
                return
            self.microscope.focus_set_point = current[0]
        self._set_button_icon(
            self.bar_4_acquire_lock_focus_button, "bar_4_acquire_lock_focus_button", checked,
        )
        self.microscope.focus = checked

    def _stage_press(self, attr, button, name):
        setattr(self.microscope, attr, True)
        self._set_button_icon(button, name, True)

    def _stage_release(self, attr, button, name):
        setattr(self.microscope, attr, False)
        self._set_button_icon(button, name, False)

    def open_microscope(self):
        self.display_message("Switching on microscope")
        message = self.microscope.open_connection()
        self.display_message(message)
        if message != "Microscope connected":
            return
        self.microscope.initialise()
        self.microscope.close = False
        self.operate_microscope()
        self.microscope_connected = True
        self._update_controls()
        if not self._export_folder_valid():
            self.display_message("Choose a valid export folder before recording")

    def close_microscope(self):
        self.microscope_connected = False
        self.microscope.display = False
        self.microscope.acquire = False
        self.microscope.focus = False
        self.bar_4_acquire_live_button.setChecked(False)
        self.bar_4_acquire_record_button.setChecked(False)
        self.bar_4_acquire_lock_focus_button.setChecked(False)
        self._update_controls()
        self.stop_microscope()
        self.display_message(self.microscope.close_connection())

    def operate_microscope(self):
        self.microscope_operation_thread = QThread()
        self.microscope_operation_worker = MicroscopeOperationWorker(self.microscope)
        self.microscope_operation_worker.moveToThread(self.microscope_operation_thread)
        self.microscope_operation_thread.started.connect(self.microscope_operation_worker.run)
        self.microscope_operation_worker.image_ir_ready.connect(self.update_camera_ir_display)
        self.microscope_operation_worker.image_im_ready.connect(self.update_camera_im_display)
        self.microscope_operation_worker.finished.connect(self.microscope_operation_thread.quit)
        self.microscope_operation_thread.finished.connect(self.microscope_operation_worker.deleteLater)
        self.microscope_operation_thread.start()

    def stop_microscope(self):
        worker = getattr(self, "microscope_operation_worker", None)
        thread = getattr(self, "microscope_operation_thread", None)
        if worker is not None:
            worker.stop()
        if thread is not None:
            thread.quit()
            thread.wait()
            thread.deleteLater()
        self.microscope_operation_worker = None
        self.microscope_operation_thread = None

    def update_camera_ir_display(self, qimg):
        self.set_rounded_pixmap(self.bar_4_top_right_image, qimg)

    def update_camera_im_display(self, qimg):
        self.set_rounded_pixmap(self.bar_4_main_image, qimg)

    def set_rounded_pixmap(self, label, qimg, radius=20):
        pixmap = QPixmap.fromImage(qimg).scaled(
            label.width(), label.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
        )
        rounded = QPixmap(label.size())
        rounded.fill(Qt.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, label.width(), label.height(), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        label.setPixmap(rounded)

    def display_message(self, message):
        self.message_label.setText(message)
        QApplication.processEvents()

    def _start_header_drag(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def _move_header_drag(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_offset)
            event.accept()

    def _stop_header_drag(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_offset = None
            event.accept()

    def closeEvent(self, event):
        if self.bar_0_power_button.isChecked():
            self.bar_0_power_button.setChecked(False)
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(
        load_new_font(Typography.FONT_FAMILY_REGULAR) or get_fallback_font()
    )
    app.setStyle("Windows")
    window = UI()
    window.show()
    sys.exit(app.exec_())

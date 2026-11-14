import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).parent / "UI"))

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QScrollArea

import main as acquire_ui
from Acquire.Microscope.Microscope_Functions import MICROSCOPE


class FakeMicroscope:
    def __init__(self):
        self.save_folder_path = ""
        self.focus_current = []
        self.acquire = False
        self.display = False
        self.focus = False

    def open_connection(self):
        return "Microscope connected"

    def initialise(self):
        pass

    def close_connection(self):
        return "Microscope disconnected"


class AcquireOnlyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.first_folder = self.root / "first"
        self.first_folder.mkdir()
        self.second_folder = self.root / "second"
        self.second_folder.mkdir()
        self.parameters_path = self.root / "Default_parameters.json"
        self.parameters_path.write_text(
            json.dumps({"simpull": {
                "uv_laser_power": "0",
                "blue_laser_power": "100",
                "green_laser_power": "100",
                "red_laser_power": "50",
                "exposure_time": "100",
                "number_of_frames": "4000",
                "number_of_acquisitions": "1",
            }}), encoding="utf-8",
        )
        self.settings_path = self.root / "Default_setting.json"
        self.settings_path.write_text(
            json.dumps({
                "master_level": "pro",
                "instrument": {"stage_x_com_port": "COM4"},
            }), encoding="utf-8",
        )
        self.local_settings_path = self.root / "Local_setting.json"
        self.local_settings_path.write_text(
            json.dumps({"export_path": str(self.first_folder)}), encoding="utf-8",
        )
        self.patches = [
            patch.object(acquire_ui, "PARAMETERS_PATH", self.parameters_path),
            patch.object(acquire_ui, "SETTINGS_PATH", self.local_settings_path),
            patch.object(acquire_ui, "MICROSCOPE", FakeMicroscope),
        ]
        for active_patch in self.patches:
            active_patch.start()
            self.addCleanup(active_patch.stop)
        self.window = acquire_ui.UI()
        self.addCleanup(self.window.close)

    def test_startup_keeps_only_simpull_and_loads_export_folder(self):
        self.assertEqual(set(self.window.parameter_inputs), {
            key for key, _, _ in acquire_ui.SIMPULL_FIELDS
        })
        self.assertEqual(self.window.microscope.save_folder_path, str(self.first_folder))
        self.assertEqual(self.window.microscope.camera_im_num_frames, 4000)
        self.assertEqual(
            self.window.export_path_display.parentWidget().height(),
            self.window.parameter_inputs["uv_laser_power"].parentWidget().height(),
        )
        self.assertFalse(hasattr(self.window, "choose_export_button"))
        self.assertEqual(
            self.window.findChild(QScrollArea).verticalScrollBarPolicy(),
            Qt.ScrollBarAlwaysOff,
        )
        self.assertFalse(hasattr(self.window, "bar_1_process_button"))
        self.assertFalse(hasattr(self.window, "bar_1_analyse_button"))
        self.window.microscope_connected = True
        self.window._update_controls()
        self.assertTrue(self.window.bar_4_acquire_live_button.isEnabled())
        self.assertTrue(self.window.bar_4_acquire_record_button.isEnabled())

    def test_remaining_icons_match_acquire_controls(self):
        toggles = (
            "bar_0_power_button",
            "bar_4_acquire_live_button",
            "bar_4_acquire_record_button",
            "bar_4_acquire_lock_focus_button",
        ) + tuple(
            f"bar_4_acquire_{short_name}_button"
            for short_name, _, _, _ in acquire_ui.STAGE_BUTTONS
        )
        fixed = (
            "bar_0_minimise_button",
            "bar_0_close_button",
            "bar_3_acquire_save_button",
        )
        expected = {f"light/{name}.svg" for name in toggles + fixed}
        expected.update(f"light/{name}_white.svg" for name in toggles)
        icon_root = Path(acquire_ui.__file__).parent / "Resources" / "Icon"
        actual = {path.relative_to(icon_root).as_posix() for path in icon_root.rglob("*.svg")}
        self.assertEqual(actual, expected)

    def test_power_live_record_focus_and_stage_controls(self):
        with (
            patch.object(self.window, "operate_microscope"),
            patch.object(self.window, "stop_microscope"),
        ):
            self.window.bar_0_power_button.setChecked(True)
            self.assertTrue(self.window.bar_4_acquire_live_button.isEnabled())
            self.window.bar_4_acquire_live_button.setChecked(True)
            self.window.bar_4_acquire_record_button.setChecked(True)
            self.window.microscope.focus_current = [7]
            self.window.bar_4_acquire_lock_focus_button.setChecked(True)
            self.assertTrue(self.window.microscope.display)
            self.assertTrue(self.window.microscope.acquire)
            self.assertTrue(self.window.microscope.focus)
            self.assertEqual(self.window.microscope.focus_set_point, 7)
            self.window.stage_buttons[0].pressed.emit()
            self.assertTrue(self.window.microscope.increase_speed)
            self.window.stage_buttons[0].released.emit()
            self.assertFalse(self.window.microscope.increase_speed)
            self.window.bar_0_power_button.setChecked(False)
            self.assertFalse(self.window.bar_4_acquire_record_button.isEnabled())
            self.assertFalse(self.window.microscope.acquire)

    def test_saving_parameters_keeps_only_simpull(self):
        self.window.parameter_inputs["number_of_frames"].setText("42")
        self.window.save_current_parameters()
        data = json.loads(self.parameters_path.read_text(encoding="utf-8"))
        self.assertEqual(list(data), ["simpull"])
        self.assertEqual(data["simpull"]["number_of_frames"], "42")
        self.assertEqual(self.window.microscope.camera_im_num_frames, 42)

    def test_export_folder_is_saved_locally_without_changing_defaults(self):
        with patch.object(
            acquire_ui.QFileDialog, "getExistingDirectory", return_value=str(self.second_folder),
        ):
            QTest.mouseClick(self.window.export_path_display, Qt.LeftButton)
        settings = json.loads(self.local_settings_path.read_text(encoding="utf-8"))
        self.assertEqual(settings["export_path"], str(self.second_folder))
        self.assertEqual(json.loads(self.settings_path.read_text(encoding="utf-8")), {
            "master_level": "pro",
            "instrument": {"stage_x_com_port": "COM4"},
        })
        self.assertEqual(self.window.microscope.save_folder_path, str(self.second_folder))
        self.assertEqual(self.window.export_path_display.text(), self.second_folder.name)

    def test_cancel_or_save_failure_keeps_previous_export_folder(self):
        with patch.object(acquire_ui.QFileDialog, "getExistingDirectory", return_value=""):
            self.window.choose_export_folder()
        self.assertEqual(self.window.microscope.save_folder_path, str(self.first_folder))
        with (
            patch.object(acquire_ui.QFileDialog, "getExistingDirectory", return_value=str(self.second_folder)),
            patch.object(Path, "replace", side_effect=OSError("denied")),
        ):
            self.window.choose_export_folder()
        self.assertEqual(self.window.microscope.save_folder_path, str(self.first_folder))
        settings = json.loads(self.local_settings_path.read_text(encoding="utf-8"))
        self.assertEqual(settings["export_path"], str(self.first_folder))
        self.assertIn("denied", self.window.message_label.text())

    def test_fresh_copy_can_choose_export_folder(self):
        self.local_settings_path.unlink()
        self.window._load_export_path()
        self.assertEqual(self.window.microscope.save_folder_path, "")
        self.window.microscope_connected = True
        self.window._update_controls()
        self.assertTrue(self.window.bar_4_acquire_live_button.isEnabled())
        self.assertFalse(self.window.bar_4_acquire_record_button.isEnabled())
        with patch.object(
            acquire_ui.QFileDialog, "getExistingDirectory", return_value=str(self.second_folder),
        ):
            self.window.choose_export_folder()
        self.assertEqual(self.window.microscope.save_folder_path, str(self.second_folder))
        self.assertTrue(self.window.bar_4_acquire_record_button.isEnabled())
        self.assertEqual(
            json.loads(self.local_settings_path.read_text(encoding="utf-8")),
            {"export_path": str(self.second_folder)},
        )

    def test_invalid_export_folder_blocks_record_but_keeps_live(self):
        self.window.microscope.save_folder_path = str(self.root / "missing")
        self.window.microscope_connected = True
        self.window._update_controls()
        self.assertTrue(self.window.bar_4_acquire_live_button.isEnabled())
        self.assertFalse(self.window.bar_4_acquire_record_button.isEnabled())
        self.window.bar_4_acquire_record_button.setChecked(True)
        self.assertFalse(self.window.microscope.acquire)
        self.assertIn("export folder", self.window.message_label.text())

    def test_recording_path_uses_selected_folder(self):
        class Camera:
            def __init__(self):
                self.record_path = None
                self.recording = False

            def set_parameters(self, **_settings):
                pass

            def start_acquire(self, _count, path):
                self.record_path = path
                self.recording = True

            def is_recording(self):
                return self.recording

        microscope = MICROSCOPE.__new__(MICROSCOPE)
        microscope.camera_ir = SimpleNamespace(display=lambda: (None, []))
        microscope.camera_im = Camera()
        microscope.laser = SimpleNamespace(set_power=lambda *_: None, enable=lambda *_: None)
        microscope.save_folder_path = str(self.second_folder)
        microscope.save_base_file_name = "Stack"
        microscope.camera_im_exp_time = 100
        microscope.camera_im_num_frames = 4
        microscope.laser_uv_power = 0
        microscope.laser_blue_power = 0
        microscope.laser_green_power = 0
        microscope.laser_red_power = 0
        microscope.acquire = True
        microscope.display = microscope.focus = microscope.recording = microscope.moving = False
        for name in (
            "move_up", "move_down", "move_front", "move_back", "move_left", "move_right",
            "increase_speed", "decrease_speed",
        ):
            setattr(microscope, name, False)
        microscope.operate()
        self.assertEqual(Path(microscope.camera_im.record_path).parent, self.second_folder)
        self.assertTrue(Path(microscope.camera_im.record_path).name.startswith("Stack_"))


if __name__ == "__main__":
    unittest.main()

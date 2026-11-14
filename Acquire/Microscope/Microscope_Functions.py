# Copyright Danial Lab (John Danial and Sabrina Keating)
# Microscope control function

# Importing core modules to locate other classes
import os
import sys
import cv2
from pathlib import Path
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QImage

# Adding parent directory to Python path for imports
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

# Importing required modules for microscope
import time
from Acquire.Laser.Laser_Functions import LASER
from Acquire.IM_Camera.IM_Camera_Functions import IMCamera
from Acquire.Stage.Stage_Functions import STAGE
from Acquire.IR_Camera.IR_Camera_Functions import IRCamera

# ==========================
class MICROSCOPE:
    """
    Class to control microscope.
    """

    def __init__(self):
        """
        Initialises a new microscope instance.
        """

        # initialise devices
        self.stage_x = STAGE()
        self.stage_y = STAGE()
        self.stage_z = STAGE()
        self.camera_im = IMCamera()
        self.camera_ir = IRCamera()
        self.laser = LASER()

        # initialise action variables
        self.close = False
        self.display = False
        self.acquire = False
        self.focus = False
        self.failed_focus = False
        self.stabilised = True

        # initialise state variables
        self.recording = False
        self.moving = False
        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False
        self.move_front = False
        self.move_back = False
        self.increase_speed = False
        self.decrease_speed = False

        # initialise save variables
        self.save_folder_path = ''
        self.save_file_path = ''
        self.save_base_file_name = 'Stack'
        self.save_file_name = 'Stack'

        # initialise timing variables
        self.interval_focus = 0.25
        self.interval_display = 0.1

        # initialise autofocus variables
        self.focus_set_point = 0
        self.focus_current = []
        self.focus_positive_fine_tolerance = 1
        self.focus_negative_fine_tolerance = -1
        self.focus_positive_coarse_tolerance = 2
        self.focus_negative_coarse_tolerance = -2
        self.focus_scan_center = 40
        self.focus_scan_max = 80
        self.focus_scan_min = 0
        self.focus_scan_current_position = self.focus_scan_center
        self.focus_offset = -1
        self.focus_diff = 0
        self.initial_focus = False

        # initialise stage variables
        self.stage_x_com_port = 'COM9'
        self.stage_y_com_port = 'COM6'
        self.stage_z_com_port = 'COM4'
        self.stage_x_jog_mode = 2
        self.stage_y_jog_mode = 2
        self.stage_z_jog_mode = 1
        self.stage_speed_current = 2
        self.stage_speed_min = 1
        self.stage_speed_max = 2
        self.stage_step_size = 100

        # initialise laser variables
        self.laser_com_port = 'COM3'
        self.laser_uv_power = 0
        self.laser_blue_power = 0
        self.laser_green_power = 0
        self.laser_red_power = 0

        # initialise imaging camera variables
        self.camera_im_exp_time = 20
        self.camera_im_num_frames = 3000
        self.camera_im_num_acquisitions = 1
        self.camera_im_num_current_acquisition = 1
        self.camera_im_pixel_binning = 2
        self.camera_im_settings = {
            "roi": (257, 256, 768, 768),
            "exposure time": self.camera_im_exp_time / 1000
        }

        # initialise IR camera variables
        self.camera_ir_exp_time = 100000

    # ==========================
    def open_connection(self):
        """
        Establishes microscope connection.

        Input variables:
        none.

        Return:
        success (bool): microscope opened successfully
        """

        # Opening connection to devices
        error_code = 'X stage not connected'
        if self.stage_x.open_connection(self.stage_x_com_port):
            error_code = 'Y stage not connected'
            if self.stage_y.open_connection(self.stage_y_com_port):
                error_code = 'Z stage not connected'
                if self.stage_z.open_connection(self.stage_z_com_port):
                    error_code = 'Laser not connected'
                    if self.laser.open_connection(self.laser_com_port):
                        error_code = 'Imaging camera not connected'
                        if self.camera_im.open_connection():
                            error_code = 'Autofocus camera not connected'
                            if self.camera_ir.open_connection():
                                error_code = 'Microscope connected'

        # Returning error code
        return error_code

    # ==========================
    def close_connection(self):
        """
        Closes microscope connection.

        Input variables:
        none

        Return:
        success (bool): microscope closed successfully
        """

        # Closing connection to devices
        error_code = 'X stage not disconnected'
        if self.stage_x.close_connection():
            error_code = 'Y stage not disconnected'
        if self.stage_y.close_connection():
            error_code = 'Z stage not disconnected'
        if self.stage_z.close_connection():
            error_code = 'Laser not disconnected'
        if self.laser.close_connection():
            error_code = 'Imaging camera not disconnected'
        if self.camera_im.close_connection():
            error_code = 'Infrared camera not disconnected'
        self.camera_ir.stop_display()
        if self.camera_ir.close_connection():
            error_code = 'Microscope disconnected'

        # Returning error code
        return error_code

    # ==========================
    def initialise(self):
        """
        Initialises microscope.

        Input variables:
        none

        Return:
        none
        """

        # Disabling laser
        self.laser.disable_all_lasers()

        # Initialising IR camera
        self.camera_ir.initialise()

        # Starting display from IR camera
        self.camera_ir.start_display()

        # Setting stage step size (for jogging)
        self.stage_x.set_step_size(self.stage_step_size, self.stage_step_size)
        self.stage_y.set_step_size(self.stage_step_size, self.stage_step_size)
        self.stage_z.set_step_size(int(self.stage_step_size / 5), self.stage_step_size)

    # ==========================
    def lock_focus(self):
        """
        Locks microscope focus.

        Input variables:
        none

        Return:
        none
        """

        # Checking if focus can be measured
        if self.focus_current is not None and not isinstance(self.focus_current, bool):

            # Calculating difference between current and set point focus
            self.focus_diff = self.focus_set_point - self.focus_current[0]

            if (self.acquire and self.recording) or self.initial_focus:
                print("MM")
                print(self.focus_diff)
                print(self.focus_scan_current_position)
                # Moving state if focus difference is outside of tolerance
                if self.focus_diff > self.focus_positive_fine_tolerance:
                    self.focus_scan_current_position = self.focus_scan_current_position - 1
                    if self.focus_scan_min <= self.focus_scan_current_position <= self.focus_scan_max:
                        self.stage_z.scan(self.focus_scan_current_position)
                elif self.focus_diff < self.focus_negative_fine_tolerance:
                    self.focus_scan_current_position = self.focus_scan_current_position + 1
                    if self.focus_scan_min <= self.focus_scan_current_position <= self.focus_scan_max:
                        self.stage_z.scan(self.focus_scan_current_position)

            elif self.acquire and not self.recording:
                if self.focus_diff > self.focus_positive_coarse_tolerance:
                    self.stabilised = False
                    if not self.stage_z.is_moving():
                        self.stage_z.move(-1)
                elif self.focus_diff < self.focus_negative_coarse_tolerance:
                    self.stabilised = False
                    if not self.stage_z.is_moving():
                        self.stage_z.move(1)
                else:
                    self.stabilised = True

    # ==========================
    def operate(self):
        image_ir = None
        image_im = None
        image_ir, self.focus_current = self.camera_ir.display()

        if self.move_up:
            if self.stage_speed_current == self.stage_speed_max:
                self.stage_z.jog(self.stage_z_jog_mode)
            else:
                self.stage_z.move(1)
            self.moving = True

        if self.move_down:
            if self.stage_speed_current == self.stage_speed_max:
                self.stage_z.jog(-self.stage_z_jog_mode)
            else:
                self.stage_z.move(-1)
            self.moving = True

        if self.move_back:
            if self.stage_speed_current == self.stage_speed_max:
                self.stage_y.jog(-self.stage_y_jog_mode)
            else:
                self.stage_y.move(-1)
            self.moving = True

        if self.move_front:
            if self.stage_speed_current == self.stage_speed_max:
                self.stage_y.jog(self.stage_y_jog_mode)
            else:
                self.stage_y.move(1)
            self.moving = True

        if self.move_left:
            if self.stage_speed_current == self.stage_speed_max:
                self.stage_x.jog(self.stage_x_jog_mode)
            else:
                self.stage_x.move(1)
            self.moving = True

        if self.move_right:
            if self.stage_speed_current == self.stage_speed_max:
                self.stage_x.jog(-self.stage_x_jog_mode)
            else:
                self.stage_x.move(-1)
            self.moving = True

        if not self.move_up and not self.move_down and not self.move_front and not self.move_back and not self.move_left and not self.move_right and self.moving:
            self.stage_x.stop()
            self.stage_y.stop()
            self.stage_z.stop()
            self.moving = False

        if self.increase_speed:
            self.stage_speed_current = self.stage_speed_current + 1
            self.stage_speed_current = max(self.stage_speed_min, min(self.stage_speed_current, self.stage_speed_max))

        if self.decrease_speed:
            self.stage_speed_current = self.stage_speed_current - 1
            self.stage_speed_current = max(self.stage_speed_min, min(self.stage_speed_current, self.stage_speed_max))

        if not self.display and not self.acquire and self.recording:
            self.laser.disable()
            self.camera_im.stop_display()
            self.recording = False

        if self.display and not self.recording:
            self.laser.set_power(self.laser_uv_power, self.laser_blue_power, self.laser_green_power, self.laser_red_power)
            self.laser.enable(self.laser_uv_power, self.laser_blue_power, self.laser_green_power, self.laser_red_power)
            self.camera_im_settings = {
                "roi": (257, 256, 768, 768),
                "exposure time": self.camera_im_exp_time / 1000
            }
            self.camera_im.set_parameters(**self.camera_im_settings)
            self.camera_im.start_display()
            self.recording = True

        if self.display and self.recording:
            image_im = self.camera_im.display()

        if self.acquire and self.recording:
            image_im = self.camera_im.display()
            if self.focus:
                self.lock_focus()

        if self.acquire and not self.recording:
            self.failed_focus = False
            unique_id_temp = datetime.now()
            unique_id = unique_id_temp.strftime("%y-%m-%d_%H_%M-%S")
            self.save_file_name = f"{self.save_base_file_name}_{unique_id}.tif"
            self.save_file_path = os.path.join(self.save_folder_path, self.save_file_name)
            if self.focus:
                self.stage_x.move(50)
                while self.stage_x.is_moving():
                    pass
                self.stabilised = False
                self.focus_diff = abs(self.focus_set_point - self.focus_current[0])
                while not self.stabilised:
                    image_ir, self.focus_current = self.camera_ir.display()
                    self.lock_focus()
                while self.stage_z.is_moving():
                    pass
                self.stage_z.move(self.focus_offset)
                while self.stage_z.is_moving():
                    pass
                self.stage_z.set_scan(self.focus_scan_center)
                self.focus_scan_current_position = self.focus_scan_center
                image_ir, self.focus_current = self.camera_ir.display()
                self.focus_diff = self.focus_set_point - self.focus_current[0]
                self.initial_focus = True
                while self.focus_diff < self.focus_negative_fine_tolerance or self.focus_diff > self.focus_positive_fine_tolerance:
                    image_ir, self.focus_current = self.camera_ir.display()
                    self.lock_focus()
                    print(self.focus_scan_current_position)
                    if self.focus_scan_current_position > self.focus_scan_max or self.focus_scan_current_position < self.focus_scan_min:
                        self.failed_focus = True
                        break
                zero_count = 0
                loop_count = 0
                while zero_count < 10:
                    loop_count += 1
                    image_ir, self.focus_current = self.camera_ir.display()
                    self.lock_focus()
                    if self.focus_diff < 1:
                        zero_count += 1
                    if loop_count == 100:
                        self.failed_focus = True
                        break
                pause_count = 0
                while pause_count < 2:
                    pause_count += 1
                    image_ir, self.focus_current = self.camera_ir.display()
                    self.lock_focus()
                    time.sleep(1)
                self.initial_focus = False
            if not self.failed_focus:
                self.laser.set_power(self.laser_uv_power, self.laser_blue_power, self.laser_green_power, self.laser_red_power)
                self.laser.enable(self.laser_uv_power, self.laser_blue_power, self.laser_green_power, self.laser_red_power)
                self.camera_im_settings = {
                    "roi": (257, 256, 768, 768),
                    "exposure time": self.camera_im_exp_time / 1000
                }
                self.camera_im.set_parameters(**self.camera_im_settings)
                self.camera_im.start_acquire(
                    self.camera_im_num_frames,
                    self.save_file_path
                )
                self.recording = True

        if self.acquire and not self.camera_im.is_recording():
            if self.camera_im_num_current_acquisition < self.camera_im_num_acquisitions:
                self.laser.disable()
                self.camera_im.stop_display()
                self.stage_z.stop()
                self.camera_im_num_current_acquisition = self.camera_im_num_current_acquisition + 1
                self.recording = False
            else:
                self.camera_im_num_current_acquisition = 1
                self.acquire = False
            if self.focus:
                while self.stage_z.is_moving():
                    pass
                self.stage_z.move(-self.focus_offset)
                while self.stage_z.is_moving():
                    pass

        return image_ir, image_im

# ==========================
class MicroscopeOperationWorker(QObject):
    """
    Class to operate microscope.
    """

    image_ir_ready = pyqtSignal(object)
    image_im_ready = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, microscope):
        super().__init__()
        self.microscope = microscope
        self.running = True

    def run(self):
        try:
            while self.running and not self.microscope.close:
                image_ir, image_im = self.microscope.operate()
                if image_ir is not None:
                    rgb_image = cv2.cvtColor(image_ir, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    qimg = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888).copy()
                    self.image_ir_ready.emit(qimg)
                if image_im is not None:
                    rgb_image = cv2.cvtColor(image_im, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    qimg = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888).copy()
                    self.image_im_ready.emit(qimg)
            self.finished.emit()
        except Exception:
            return False

    def stop(self):
        self.running = False

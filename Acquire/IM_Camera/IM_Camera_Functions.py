# Copyright Danial Lab (John Danial and Sabrina Keating)
# Camera (PCO edge) function

# Importing required modules for camera control system
import time
import pco
import cv2
from pco.defs import PCO_RECORDER_LATEST_IMAGE

# ==========================
class IMCamera:
    """
    Class to control camera.
    """

    # ==========================
    def __init__(self):
        """
        Initialises a new camera instance.
        """

        # camera handle
        self.camera = None

    # ==========================
    def open_connection(self):
        """
        Establishes camera connection.

        Input variables:
        none

        Return:
        success (bool): camera opened successfully
        """

        try:

            # Assigns camera handle
            self.camera = pco.Camera()
            self.camera.sdk.set_cooling_setpoint_temperature(-25)
            self.camera.sdk.set_fan_control_parameters("user", 0)

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def close_connection(self):
        """
        Closes camera connection.

        Input variables:
        none

        Return:
        success (bool): camera closed successfully.
        """

        try:

            # Closing camera
            self.camera.close()

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def start_record(self):
        """
        Starting to record.

        Input variables:
        none

        Return:
        success (bool): camera recording successfully started.
        """

        try:

            # Recording
            self.camera.record()

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def set_parameters(self, **kwargs):
        """
        Setting camera parameters.

        Input variables (as keyword arguments):
        exposure_time (float): exposure duration in seconds
        roi (tuple): region of interest as (x0,y0,x1,y1)
        trigger (str): trigger mode for acquisition
        binning (tuple): binning factors as (horizontal, vertical, method)
        noise_filter (str): noise filter setting ('on'/'off')
        timestamp (str): timestamp mode ('off'/'ascii')
        metadata (str): metadata recording mode ('on'/'off')
        acquire (str): acquire mode ('auto'/'external')
        auto_exposure (tuple): auto exposure settings (region, min_exp, max_exp)

        Return:
        success (bool): camera parameters are successfully set.
        """

        # try:

        settings = {}

        # Populating a settings array
        for param_name, value in kwargs.items():
            if value is not None:
                settings[param_name] = value

        # Setting camera parameters
        self.camera.configuration = settings

        # Returning successful
        return True

        # except Exception:

        # Returning unsuccessful
        return False

    # ==========================
    def start_display(self):
        """
        Starting live display.

        Input variables:
        window_size (tuple): display window dimensions (width, height)

        Return:
        success (bool): live display successfully started.
        """

        try:

            # Recording in ring buffer mode with minimum buffer size
            self.camera.record(number_of_images = 4, mode = 'ring buffer')

            # Waiting to fill buffer with minimum number of images
            while self.camera.recorded_image_count < 4:
                time.sleep(0.1)

            # Returning successful
            return True

        except Exception:

            # Checking if camera is recording
            if self.camera.is_recording:

                # Stopping camera
                self.camera.stop()

            # Returning unsuccessful
            return False

    # ==========================
    def stop_display(self):
        """
        Stopping live display.

        Input variables:
        none

        Return:
        success (bool): live display successfully stopped.
        """

        try:

            # Stopping camera
            self.camera.stop()

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def display(self):
        """
        Displaying latest image.

        Input variables:
        none

        Return:
        success (bool): image successfully displayed.
        """

        try:

            # getting latest image
            image, meta_data = self.camera.image(PCO_RECORDER_LATEST_IMAGE)

            # normalising image
            normalised = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype = cv2.CV_8U)

            # Returning successful
            return normalised

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def start_acquire(self, num_frames: int, file_path) -> bool:
        """
        Starting acquisition.

        Input variables:
        num_frames (int): number of frames to acquire.
        file_path (str): file path to acquire.
        window_size (tuple): display window dimensions (width, height)

        Return:
        success (bool): live display successfully started.
        """

        # Recording a set number of frames and savin them as bigtiff in file path
        self.camera.record(number_of_images = num_frames, mode = "multitif", file_path = file_path)

        # Waiting to fill buffer with minimum number of images
        while self.camera.recorded_image_count < 4:
            time.sleep(0.001)

        # Returning successful
        return True

    # ==========================
    def is_recording(self):
        """
        Starting acquisition.

        Input variables:
        none

        Return:
        is_recording (bool): if camera is recording.
        """

        # Returning camera is recording
        return self.camera.is_recording

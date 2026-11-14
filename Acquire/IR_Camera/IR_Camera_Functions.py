# Copyright Danial Lab (John Danial and Sabrina Keating)
# Camera (FLIR) control functions

# Importing required modules for camera control system
import numpy as np
import PySpin
import cv2

# ==========================
class IRCamera:
    """
    Class to control camera.
    """

    # ==========================
    def __init__(self):
        """
        Initialises a new camera instance.
        """

        # camera handle
        self.system = None
        self.camera = None
        self.last_focus = None
        self.last_image = None

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
            # Getting camera list
            self.system = PySpin.System.GetInstance()
            self.system.UpdateInterfaceList()
            cam_list = self.system.GetCameras()

            # Selecting first camera
            self.camera = cam_list.GetByIndex(0)

            # Initialising camera
            self.camera.Init()

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    def close_connection(self):
        """
        Closes camera connection.

        Input variables:
        none

        Return:
        success (bool): camera closed successfully.
        """

        try:

            # De-initialising camera
            self.camera.DeInit()

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def initialise(self):
        """
        Initialising camera.

        Input variables:
        none

        Return:
        success (bool): camera initialised successfully
        """

        try:

            # Initialising camera
            self.camera.Init()

            # Turning off auto exposure
            self.camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

            # Setting exposure mode to timed
            self.camera.ExposureMode.SetValue(PySpin.ExposureMode_Timed)

            # Setting exposure time
            self.camera.ExposureTime.SetValue(100.0)

            # Getting camera node map
            node_map = self.camera.GetNodeMap()

            # Setting horizontal binning
            binning_h = PySpin.CIntegerPtr(node_map.GetNode("BinningHorizontal"))
            binning_h.SetValue(2)

            # Setting vertical binning
            binning_v = PySpin.CIntegerPtr(node_map.GetNode("BinningVertical"))
            binning_v.SetValue(2)

            # Enabling acquisition frame rate setting
            acquisition_frame_rate_enable = PySpin.CBooleanPtr(node_map.GetNode("AcquisitionFrameRateEnable"))
            acquisition_frame_rate_enable.SetValue(True)

            # Setting acquisition frame rate
            frame_rate_node = PySpin.CFloatPtr(node_map.GetNode("AcquisitionFrameRate"))
            frame_rate_node.SetValue(10)

            # Disabling automatic gain
            gain_auto = PySpin.CEnumerationPtr(node_map.GetNode("GainAuto"))
            gain_auto_off = gain_auto.GetEntryByName("Off")
            gain_auto.SetIntValue(gain_auto_off.GetValue())

            # Setting gain
            gain = PySpin.CFloatPtr(node_map.GetNode("Gain"))
            gain.SetValue(1.0)

            # Getting acquisition node map
            node_acquisition_mode = PySpin.CEnumerationPtr(node_map.GetNode('AcquisitionMode'))

            # Setting acquisition mode
            node_acquisition_mode.SetIntValue(node_acquisition_mode.GetEntryByName('Continuous').GetValue())

            # Getting buffer handling nope map
            node_buffer_handling = PySpin.CEnumerationPtr(self.camera.GetTLStreamNodeMap().GetNode('StreamBufferHandlingMode'))

            # Applying selected buffer handling mode
            node_buffer_handling.SetIntValue(node_buffer_handling.GetEntryByName('NewestOnly').GetValue())

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def start_display(self) -> None:
        """
        Starting live display.

        Input variables:
        window_size (tuple): display window dimensions (width, height)

        Return:
        success (bool): live display successfully started.
        """

        try:

            # Starting recording
            self.camera.BeginAcquisition()

            # Returning successful
            return True

        except Exception:

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
            self.camera.EndAcquisition()

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def display(self):
        """
        Capture and return the latest image as a QImage-ready array.
        """
        try:
            image = self.camera.GetNextImage(100)
            if image.IsIncomplete():
                image.Release()
                return None

            image_array = image.GetNDArray()
            normalised = cv2.normalize(image_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

            _, thresh = cv2.threshold(normalised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            max_area = 0
            current_focus = (0, 0)

            for contour in contours:
                moments = cv2.moments(contour)
                area = moments['m00']
                if area > 0:
                    cx = int(moments['m10'] / area)
                    cy = int(moments['m01'] / area)
                    if area > max_area:
                        max_area = area
                        current_focus = (cx, cy)

            # Draw the focus circle
            normalised_color = cv2.cvtColor(normalised, cv2.COLOR_GRAY2BGR)
            cv2.circle(normalised_color, current_focus, 20, (0, 0, 255), -1)

            image.Release()

            # Return both image and focus point
            self.last_image = normalised_color
            self.last_focus = current_focus
            return normalised_color, current_focus

        except Exception as e:
            print(f"Display error: {e}")
            return self.last_image, self.last_focus
# Copyright Danial Lab (John Danial and Sabrina Keating)
# Laser (Coherent Cobolt) control function

# Importing required modules for laser system
import time
import pycobolt

# ==========================
class LASER:
    """
    Class to control laser.
    """

    def __init__(self):
        """
        Initialises a new laser instance.
        """

        # initialize state variables
        self.laser = None

    # ==========================
    def open_connection(self, port: str):
        """
        Establishes laser connection.

        Input variables:
        port (str): laser COM port.

        Return:
        success (bool): laser opened successfully
        """

        try:

            # Connecting to laser
            self.laser = pycobolt.CoboltLaser(port = port)

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def close_connection(self):
        """
        Closes laser connection.

        Input variables:
        none

        Return:
        success (bool): laser closed successfully
        """

        try:

            # Disconnecting laser
            self.laser.disconnect()

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def enable(self, uv_laser_power: int, blue_laser_power: int, green_laser_power: int, red_laser_power: int):
        """
        Enables laser.

        Input variables:
        none

        Return:
        success (bool): laser enabled successfully
        """

        try:

            # Enabling laser
            if uv_laser_power > 0:
                self.laser.send_cmd("4l1")
            if blue_laser_power > 0:
                self.laser.send_cmd("3l1")
            if green_laser_power > 0:
                self.laser.send_cmd("1l1")
            if red_laser_power > 0:
                self.laser.send_cmd("2l1")

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def disable(self):
        """
        Enables laser.

        Input variables:
        none

        Return:
        success (bool): laser enabled successfully
        """

        try:

            # Disabling all lasers
            self.laser.send_cmd("1l0")
            self.laser.send_cmd("2l0")
            self.laser.send_cmd("3l0")
            self.laser.send_cmd("4l0")

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def disable_all_lasers(self):
        """
        Enables laser.

        Input variables:
        none

        Return:
        success (bool): laser enabled successfully
        """

        try:

            # Enabling laser
            self.laser.send_cmd("1l0")
            self.laser.send_cmd("2l0")
            self.laser.send_cmd("3l0")
            self.laser.send_cmd("4l0")

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def set_power(self, uv_laser_power: int, blue_laser_power: int, green_laser_power: int, red_laser_power: int):
        """
        Sets laser power.

        Input variables:
        power (float): laser power value.

        Return:
        success (bool): laser enabled successfully
        """

        try:

            # Setting power
            cmd = f"4p {uv_laser_power / 1000}"
            self.laser.send_cmd(cmd)
            cmd = f"3p {blue_laser_power / 1000}"
            self.laser.send_cmd(cmd)
            cmd = f"1p {green_laser_power / 1000}"
            self.laser.send_cmd(cmd)
            cmd = f"2p {red_laser_power / 1000}"
            self.laser.send_cmd(cmd)
            time.sleep(0.5)

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False
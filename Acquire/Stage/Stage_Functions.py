# Copyright Danial Lab (John Danial and Sabrina Keating)
# Stage (Newport Agilis) control function

# Importing required modules for laser system
import serial
import time

# ==========================
class STAGE:
    """
    Class to control stage.
    """

    # ==========================
    def __init__(self):
        """
        Initialises a new stage instance.
        """

        # set the serial connection to none (haven't set it)
        self.stage = None

        # command terminator required by controller
        self.terminator = '\r\n'

    # ==========================
    def open_connection(self, port: str):
        """
        Establishes stage connection.

        Input variables:
        port (str): stage COM port.

        Return:
        success (bool): stage opened successfully
        """

        try:
            # Creating serial connection with stage
            self.stage = serial.Serial(port = port)

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def close_connection(self):
        """
        Closing stage connection.

        Input variables:
        none.

        Return:
        success (bool): stage closed successfully
        """

        try:

            # Closing connection
            self.stage.close()

            # Returning successful
            return False

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def set_step_size(self, backward_step_size: int, forward_step_size: int):
        """
        Setting stage step size.

        Input variables:
        step_size (int): stage step size.

        Return:
        success (bool): step size set successfully
        """

        try:

            # Setting step size
            cmd = f"XU-{backward_step_size},{forward_step_size}" + self.terminator
            self.stage.write(cmd.encode())

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def jog(self, mode: int):
        """
        Commanding stage to jog.

        Input variables:
        mode (int): jogging mode.

        Return:
        success (bool): stage jogged successfully
        """

        try:

            # Checking if stage is moving
            cmd = f"MS?" + self.terminator
            self.stage.write(cmd.encode())

            # Commanding stage to jog
            if self.stage.readline().decode().strip() == "MS0":
                cmd = f"JA{mode}" + self.terminator
                self.stage.write(cmd.encode())

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def move(self, num_steps: int):
        """
        Commanding stage to move step-wise.

        Input variables:
        num_steps (int): number of steps to move.

        Return:
        success (bool): stage moved successfully
        """

        try:

            # Checking if stage is moving
            cmd = f"MS?" + self.terminator
            self.stage.write(cmd.encode())

            # Commanding stage to jog
            if self.stage.readline().decode().strip() == "MS0":
                # setting movement frequency
                cmd = f"XF{abs(num_steps)}" + self.terminator
                self.stage.write(cmd.encode())
                print(cmd)

                # moving stage
                cmd = f"XR{num_steps}" + self.terminator
                print(cmd)
                self.stage.write(cmd.encode())

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def is_moving(self):

        # Checking if stage is moving
        cmd = f"MS?" + self.terminator
        self.stage.write(cmd.encode())
        
        if self.stage.readline().decode().strip() == "MS0":
            return False
        else:
            return True

    # ==========================
    def set_scan(self, units: float):
        """
        Commanding stage to move step-wise.

        Input variables:
        num_steps (int): number of steps to move.

        Return:
        success (bool): stage moved successfully
        """

        try:

            # setting scan mode
            cmd = f"XS" + self.terminator
            self.stage.write(cmd.encode())
            time.sleep(1)

            # centering scanner
            cmd = f"XN{units}" + self.terminator
            self.stage.write(cmd.encode())
            time.sleep(1)

            # Returning successful
            return True

        except Exception:
            # Returning unsuccessful
            return False

    # ==========================
    def scan(self, units: float):
        """
        Commanding stage to move step-wise.

        Input variables:
        num_steps (int): number of steps to move.

        Return:
        success (bool): stage moved successfully
        """

        try:

            # scanning
            cmd = f"XN{units}" + self.terminator
            self.stage.write(cmd.encode())

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False

    # ==========================
    def stop(self):
        """
        Stopping stage.

        Input variables:
        none.

        Return:
        success (bool): stage stopped successfully
        """

        try:

            # stopping stage
            cmd = f"ST" + self.terminator
            self.stage.write(cmd.encode())

            # Returning successful
            return True

        except Exception:

            # Returning unsuccessful
            return False
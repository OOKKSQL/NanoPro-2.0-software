# NanoPro 2.0

## Before you begin

Before setting up the app, make sure you have:

- A computer running 64-bit Windows 10 or 11 and connected to the microscope.
- An internet connection for the first setup.
- [Python 3.10.11 for Windows, 64-bit](https://www.python.org/downloads/release/python-31011/). On that page, choose **Windows installer (64-bit)**. During installation, select **Add Python to PATH** if offered. You do not need to learn Python or install a programming editor.
- [Git for Windows](https://git-scm.com/install/win). The setup uses Git to download one required part. You do not need a Git account or any experience with Git.
- **FLIR Spinnaker 4.0.0.116** camera software installed on the computer. If it is not already installed, get the matching 64-bit version from [FLIR/Teledyne](https://www.teledynevisionsolutions.com/products/spinnaker-sdk?model=Spinnaker+SDK&segment=iis&vertical=machine+vision). The setup adds the part that lets the app communicate with the camera, but it does not install the full FLIR camera software or drivers.

## Set up the app once

1. Download this project as a ZIP file. In Windows, choose **Extract All**, then put the extracted folder somewhere you can keep it, such as **Documents**. Do not run the files from inside the ZIP.
2. Open the extracted folder and double-click **setup_environment.bat**.
3. Follow the prompts in the black window and keep your internet connection on. Setup may take several minutes. Look for **Setup completed successfully** at the end.
4. Press Enter or any key when prompted to close the window.

Keep the extracted folder in the same place after setup. If you move it, run setup again in the new location and choose **y** when asked to recreate the app files.

## Open and use the app

To open the app later, double-click **Launch_Application.bat** in the extracted folder. You do not need a programming editor or any extra commands.

## Troubleshooting

| Issue | Recommended action |
| --- | --- |
| Setup reports **Python 3.10 is not installed** | Install the 64-bit Python 3.10 version linked above, then run **setup_environment.bat** again. A newer Python version alone does not meet this requirement. |
| Setup stops or reports that a part could not be installed | Check your internet connection and confirm that Git for Windows is installed. Run **setup_environment.bat** again and read the final message. If the problem continues, provide a photo of the setup window to your lab's technical staff. |
| Setup mentions **PySpin**, **FLIR**, or **Spinnaker** | The autofocus camera requires the matching FLIR Spinnaker 4.0.0.116 software. Ask your lab's technical staff to confirm that it is installed, then run setup again. |
| The launcher reports **The application has not been set up yet** | Run **setup_environment.bat**. If setup does not finish successfully, follow the instructions in its error message and try again. |
| The app reports **X/Y/Z stage**, **Laser**, **Imaging camera**, or **Autofocus camera not connected** | Check that the microscope and the named device are powered on and connected. If you are using a different computer, ask your lab's technical staff to check its device connections and camera software. |
| The live, focus, stage, or record buttons are greyed out | Connect the microscope, enter whole numbers for the settings, and save them. Recording also requires a valid Export folder. |
| The app reports **Choose a valid export folder before recording** | Click **Export folder** and select an existing folder where you can save files. |
| The app reports **Invalid SiMPULL parameters** | Check all seven settings on the left. Enter whole numbers, then click the save symbol. |
| The live image remains blank | Make sure the play (triangle) symbol is on. Check the sample and illumination using your lab procedure. If the image is still blank, ask your lab's technical staff to check the camera. |
| No recording appears in the selected folder | Confirm that the Export folder is correct and allow the recording to finish. Look for a file beginning with `Stack_` and ending in `.tif`. |
| The app closes unexpectedly or displays an error in the black window | Provide a photo of the message to your lab's technical staff and describe what you clicked just before the error appeared. |

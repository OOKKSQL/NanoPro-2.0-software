# NanoPro 2.0: using the ALBA microscope app

This app lets you view the microscope image, move the sample stage, keep the image in focus, and save recordings. It is intended for people who have been trained to use the connected microscope. Use the laser settings approved for your experiment.

## Before you begin

You need:

- A Windows 10 or 11 computer (64-bit) connected to the microscope, cameras, stage, and laser. This app is set up for the original lab's device connections. A different computer or microscope may need help from your lab's technical staff.
- An internet connection for the first setup.
- [Python 3.10.11 for Windows, 64-bit](https://www.python.org/downloads/release/python-31011/). On that page, choose **Windows installer (64-bit)**. During installation, select **Add Python to PATH** if offered. You do not need to learn Python or install a programming editor.
- [Git for Windows](https://git-scm.com/install/win). The setup uses this to download one required part; you do not need a Git account or need to use Git yourself.
- The **FLIR Spinnaker 4.0.0.116** camera software installed on the computer. Ask your lab's technical staff to install the matching 64-bit version from [FLIR/Teledyne](https://www.teledynevisionsolutions.com/products/spinnaker-sdk?model=Spinnaker+SDK&segment=iis&vertical=machine+vision) if it is not already there. The setup file adds the app's camera connection part, but it does not install the full FLIR camera software or drivers.

If you use an already prepared microscope computer, some of these items may already be installed.

## Set up the app once

1. Download this project as a ZIP file and choose **Extract All** in Windows. Put the extracted folder somewhere you can keep it, such as **Documents**. Do not run the files from inside the ZIP.
2. Open the extracted folder and double-click **setup_environment.bat**.
3. Follow the prompts in the black window. Keep the internet connected. Setup can take several minutes. You should see **Setup completed successfully** at the end.
4. Press Enter or any key when prompted to close the window.

Keep the extracted folder in the same place after setup. If you move it, run setup again in its new location and choose **y** when asked to recreate the app files.

## Open and use the app

Each time you want to use it, double-click **Launch_Application.bat** in the extracted folder. No programming editor or extra commands are needed.

1. **Choose where recordings go.** Click the **Export folder** box on the left and choose an existing folder where you want your images saved. This copy of the app remembers your choice.
2. **Connect the microscope.** Click the power symbol at the top right. Wait for **Microscope connected** at the bottom of the window. If you see a message saying a device is not connected, see the table below.
3. **Check your experiment settings.** The boxes on the left show laser power (by color), exposure time (time per image), number of frames (images per recording), and number of acquisitions (how many recordings). Use the values specified by your lab protocol. Enter whole numbers, then click the **save (floppy disk) symbol** beneath the boxes. Your choices will be loaded again next time.
4. **View the image.** Click the **triangle/play symbol** below the large image to turn the live view on or off.
5. **Adjust the sample if needed.** The arrow controls move the stage while held. The speed controls change how quickly it moves. Use these only if you have been trained on this microscope.
6. **Keep focus if needed.** Click the focus symbol below the small image. If the app says **Focus reading is not available**, wait for the small camera image to appear and try again.
7. **Record.** Click the **video camera symbol** below the large image. Let the planned recording finish. The app saves files named like `Stack_26-11-17_14_30-00.tif` in your chosen Export folder. Each `.tif` file contains a stack of images. If the record button remains highlighted afterward, click it again to turn it off.
8. When finished, turn off live view and focus if they are on, click the power symbol to disconnect, and close the window.

## If something goes wrong

| What you see | What to do |
| --- | --- |
| Setup says **Python 3.10 is not installed** | Install the 64-bit Python 3.10 version linked above, then run **setup_environment.bat** again. A newer Python version alone will not satisfy this setup. |
| Setup stops or says a part failed to install | Check your internet connection. Make sure Git for Windows is installed. Run **setup_environment.bat** again and read the final message. If it still fails, share a photo of the black window with your lab's technical staff. |
| Setup mentions **PySpin**, **FLIR**, or **Spinnaker** | The autofocus camera needs the matching FLIR Spinnaker 4.0.0.116 software. Ask your lab's technical staff to check its installation, then run setup again. |
| The launcher says **The application has not been set up yet** | Run **setup_environment.bat** first. If setup did not finish successfully, resolve its message and run it again. |
| The app says **X/Y/Z stage**, **Laser**, **Imaging camera**, or **Autofocus camera not connected** | Check that the microscope and the named device are powered and connected. If you are using a different computer, ask your lab's technical staff to check its device connections and camera software. |
| The live, focus, stage, or record buttons are greyed out | Connect the microscope and save valid whole-number settings. Recording also needs a valid Export folder. |
| The app says **Choose a valid export folder before recording** | Click **Export folder** and select an existing folder that you can save files to. |
| The app says **Invalid SiMPULL parameters** | Check all seven settings on the left. Use whole numbers only, then click the save symbol. |
| The live image stays blank | Make sure the triangle/play symbol is on. Check the sample and illumination using your lab procedure. If the image is still blank, ask technical staff to check the camera. |
| No recording appears in your folder | Check that the Export folder is correct, let the recording finish, and look for a `Stack_` file with a `.tif` ending. |
| The app closes or shows an error in the black window | Take a photo of the message and share it with your lab's technical staff. Include what you clicked just before it happened. |

The setup checks that the app's parts can load; it cannot check whether a physical microscope is connected. If this is the first time the computer has been used with this microscope, ask your lab's technical staff to confirm the hardware setup before your experiment.

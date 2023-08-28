# raspi_terminal_button_interface
Script to interface LCD screen connected to Raspberry Pi (Video Player) with four buttons (Red, Blue, Yellow, Green). Terminal Output helps guide button presses to select .mp4/.mkv files to play. [COMPLETED PROJECT]

Currently working on new implementations such as choosing the size of subtitle text, displaying when the skip length is changed, power from battery, and 3D printed or wood case.

Did not end up finishing the hardware (creating a case, soldering everything together). Also, there is potential for omxplayer to be able to do the same thing as what I did with vlc (maybe even better). Also something that is pretty annoying about using a raspberry pi is 
1. The subtitle display (without hardcoding into the videos) can made the video stutter every time a new subtitle is displayed.
2. The videos have to be encoded as H.264, H.265 is too computationally intense. There's all sorts of other thing you can do to overload the raspberry pi as well, like having a high frame rate or resolution, or wasting disc space by trying to display 1080p on a lower resolution screen. Your videos need to be formatted correctly, and video encoding is a computationally intense process (especially with hundreds of videos 25 minutes each). I would leave my computer running all night re-encoding videos with my i7 10th gen laptop processor. It's not as bad with a better computer but this is all I have.
3. Putting the videos on the SD card is not possible if you're using a Windows computer, so you have to send everything through sftp or some equivallent remote access file transferring. I don't know if a linux computer can read the sd card formatted for the raspberry pi. 

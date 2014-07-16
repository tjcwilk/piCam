piCam
=====

piCam is a project for creating a security camera using the raspberry pi

This isnt an extensive howto of how to get this project working for you, however the key files are here. You should be able to work out the rest.

* mmalcam.conf - This is my config file for motion. I had to do some tweaking to stop the pi from crashing.

* motion-mmal - install motion (sudo apt-get install motion), however the original motion binary dosnt seem to like the official rasberri pi camera. Instead, run this one. I didnt do this so cudo's to the chap who did.

* startmotion.sh - script that starts motion

* stopmotion.sh - script that stops motion

* uploader.py - set as the script to auto run after completion of a video capture. Uploads the image to Amazon S3 and emails a list of people.





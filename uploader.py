#!/usr/bin/python
#
# Uploader.py
#  Script is set to auto run by the linux software 'motion' after video capture.
#  used to upload to AWS S3 and alert via email
#
# tjcwilk, http://wilkins.io, 16/07/14
#

import sys
import time
import os
import smtplib

import boto
import boto.s3
from boto.s3.key import Key
from boto.s3.connection import S3Connection

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

#
# GLOBALS - fill these in with your details
#

S3_KEYID = 'abcd' # key id of aws user with S3 permisshions
S3_KEY = '1234' # The users key
S3_BUCKETNAME = 'my_bucket' # The name of the bucket to upload to
S3_SUBFOLDER = "files/" # the subfolder in the bucket to put the files in

GMAIL_USERNAME = 'alice@gmail.com' # Gmail User to send alerts from
GMAIL_PASSWORD = 'S3cretz' # Password of the account
EMAIL_ALLERT_LIST = ['alice@gmail.com','bob@hotmail.co.uk'] # List of alerts go to these guys

DBG_LOGFILE = "/home/pi/uploader_log" # script logs to a file, specify here



def uploadToS3(videoFile):
  txtout = "S3Upload started on :: " + videoFile
  dbgout(txtout)
  
  AWS_ACCESS_KEY_ID = S3_KEYID
  AWS_SECRET_ACCESS_KEY = S3_KEY

  dbgout("Connecting & gettig bucket")
  conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
  bucket = conn.get_bucket(S3_BUCKETNAME) 

  dbgout("Creating key and setting content")
  k = Key(bucket)
  nameoffile = videoFile.split('/')[-1]
  k.key = S3_SUBFOLDER + nameoffile
  dbgout("Saving file to :: " + k.key)

  dbgout("Uploading contents from :: " + videoFile)
  k.set_contents_from_filename(videoFile)

  # Needs to be readable so the alerted users can see it
  k.set_acl('public-read')
  url = k.generate_url(expires_in=0, query_auth=False)

  dbgout("Upload complete")

  # Delete the file off the pi
  os.remove(videoFile)
  dbgout("Original file deleted")

  return url



def mail(to, subject, text, attach):
  dbgout("Mail() called for ::" + to)

  gmail_user = GMAIL_USERNAME
  gmail_pwd = GMAIL_PASSWORD

  msg = MIMEMultipart()

  msg['From'] = gmail_user
  msg['To'] = to
  msg['Subject'] = subject
  msg.attach(MIMEText(text))

  part = MIMEBase('application', 'octet-stream')
  part.set_payload(open(attach, 'rb').read())
  Encoders.encode_base64(part)
  part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
  msg.attach(part)

  mailServer = smtplib.SMTP("smtp.gmail.com", 587)
  mailServer.ehlo()
  mailServer.starttls()
  mailServer.ehlo()
  mailServer.login(gmail_user, gmail_pwd)
  mailServer.sendmail(gmail_user, to, msg.as_string())
  # Should be mailServer.quit(), but that crashes...
  mailServer.close()



def sendEmailAlert(url, picture):
  dbgout("Sending email alerts")

  for emailaddr in EMAIL_ALLERT_LIST:
    mail(emailaddr, "piCam1 Detected Motion", url, picture)


# When motion runs the script we dont se stdout, so log to a file
def dbgout(message):
  now = time.strftime("%c")
  debugmsg = now + ":: " + message + "\n"

  with open(DBG_LOGFILE, "a") as myfile:
    myfile.write(debugmsg)



if __name__ == "__main__":

  if len(sys.argv) !=1:
    string = "Usage: uploader.py <file.avi>"
    print string
    dbgout(string)

  file = sys.argv[1]

  dbgout("Uploader.py initiated on :: " + file) 
  url = uploadToS3(file)
  dbgout("URL of Uploaded file :: " + url)

  # TODO - hardcoded image to attatch to the email, this should be the .jpg motion
  # produces
  picture = "/home/pi/cam.jpg"
  sendEmailAlert(url, picture)
  
  dbgout("Uploader.py finished")





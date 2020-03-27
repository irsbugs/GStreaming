#!/usr/bin/env python3
#
# time_google_tts.py
#
# This uses the GStreamer (Gst) module playbin
#
# By using player.get_bus().poll() this avoids using a loop by and the 
# need for a call_back() function for EOS, etc.
#
# Demonstration of using a local mp3 file to provide part of the text. E.g.
# "The time is", and then, after determining the time, using google translates 
# text to speech feature to provide the time.
#
# mp3 files with recorded phrases are in the "phrase" sub-folder.
#
# Ian Stewart - 2020-03-25

# Importing...
import sys
import os.path
import datetime

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Brief uri as default when calling main().
uri_string =  'https://translate.google.com/translate_tts?'
uri_string += 'ie=UTF-8&client=tw-ob&tl={}&q={}'
URI = uri_string.format("en-au", "This is a test of googles text to speech.")

def main(uri=URI):
    """
    Requires the uri to be passed.   
    Initialize Gst, Instantiate playbin, and get rid of video.
    Set the uri property. 
    Start playing the text to google and receiving the mp3 audio stream.
    Poll for the End-of-Stream (EOS), or an Error.
    End by changing state to null.


    """
    # Init
    Gst.init(None)
    # Instantiate    
    player = Gst.ElementFactory.make("playbin")
    #player = Gst.ElementFactory.make("uridecodebin")
    # Remove video
    fakesink = Gst.ElementFactory.make("fakesink", "fakesink")

    player.set_property("video-sink", fakesink)

    # Set the uri to be sent to google. Puts + in place of spaces???
    player.set_property('uri', uri)

    # Send text to google, and start streaming the mp3 audio with playbin
    player.set_state(Gst.State.PLAYING)

    # wait until things stop
    player.get_bus().poll(Gst.MessageType.EOS | Gst.MessageType.ERROR, 
                          Gst.CLOCK_TIME_NONE)

    player.set_state(Gst.State.NULL)


if __name__=="__main__":

    if len(sys.argv) == 1:
        print("Please pass an argument on launching. E.g. test, or time or date.")

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Testing
        main()

        uri = uri_string.format("en-au", "Hello. I am an Australian.")
        main(uri)

        uri = uri_string.format("en-US", "This is with an USA accent.")
        main(uri)

        uri = uri_string.format("en-UK", "This is with a British accent.")
        main(uri)

    if len(sys.argv) > 1 and sys.argv[1].lower() == "time":
        # Time
        mp3_file = "phrase/the_time_is.mp3"
        uri_mp3 = Gst.filename_to_uri(mp3_file)
        main(uri_mp3)

        # print(datetime.datetime.now().strftime('%-I %M %p'))  # 1 32 PM
        time_now = datetime.datetime.now().strftime('%-I %M %p')
        uri = uri_string.format("en-au", time_now)
        main(uri)

    if len(sys.argv) > 1 and sys.argv[1].lower() == "date":   
        # Date
        mp3_file = "phrase/todays_date_is.mp3"
        uri_mp3 = Gst.filename_to_uri(mp3_file)
        main(uri_mp3)

        #>>> print(datetime.datetime.now().strftime('%A, %-d %B, %Y'))
        #Thursday, 26 March, 2020
        date_today = datetime.datetime.now().strftime('%A, %-d %B, %Y')
        uri = uri_string.format("en-au", date_today)
        main(uri)


"""
Notes:

# Linux syntax to remove leading 0 uses a "-". As in '%-I'
# print(datetime.datetime.now().strftime('%-I %M %p'))  # 1 32 PM
# Windows syntax: Change '-' to a '#', as in '%-I' changes to  '%#I'
# print(datetime.datetime.now().strftime('%#I %M %p'))  # 1 32 PM

"""

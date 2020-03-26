#!/usr/bin/env python3
#
# google_tts_poll.py
#
# This uses the GStreamer (Gst) module playbin
#
# Utilises player.get_bus().poll(). This avoids using a loop and the 
# need for a call_back() function for EOS, etc.
#
# Demonstration of using google translate text to speech feature.
# It will also play a local mp3 file.
#
# Note: The program can not be terminated with control-C.
#
# Requirements: 
# Connected tothe internet.
# yakety_yak.mp3 in the same folder as this program
#
# Ian Stewart - 2020-03-25

# Importing...
import sys, os

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# uri string that requiring language and text message.
uri_string =  'https://translate.google.com/translate_tts?'
uri_string += 'ie=UTF-8&client=tw-ob&tl={}&q={}'

# Insert language and message into uri_string as default for main()
URI = uri_string.format('en-au', 'Hello. I speak with an Australian accent.')

def main(uri=URI):
    """
    Requires the uri to be passed to this function.   
    Initialize Gst, Instantiate playbin, and get rid of video.
    Set the uri property. 
    Start playing the text to google and receiving the mp3 audio stream.
    Poll for the End-of-Stream (EOS), or an Error.
    End by changing state to null.
    """
    # Initialize
    Gst.init(None)

    # Instantiate    
    player = Gst.ElementFactory.make('playbin', 'player')

    # Remove video
    fakesink = Gst.ElementFactory.make('fakesink', 'fakesink')
    player.set_property('video-sink', fakesink)

    # Set the uri to be used
    player.set_property('uri', uri)

    # Send text to google, and start streaming the mp3 audio with playbin
    player.set_state(Gst.State.PLAYING)

    # Do polling until things stop. Note: Control-C will not stop this.
    player.get_bus().poll(Gst.MessageType.EOS | Gst.MessageType.ERROR, 
                          Gst.CLOCK_TIME_NONE)

    # Stop. 
    player.set_state(Gst.State.NULL)


if __name__=='__main__':

    # English tts with Australian, USA and British accents
    main()

    main(uri_string.format('en-UK', 'This is spoken with a British accent.'))

    main(uri_string.format('en-US', 'This is spoken with an USA accent.'))

    # French - Oh its pretty
    main(uri_string.format('fr', "Oh là là c'est trop jolie!"))
    
    # Japanese - Hello
    main(uri_string.format('ja', 'こんにちは'))

    # Streaming a local mp3 file in the current working directory
    mp3_file = 'yakety_yak.mp3'
    if os.path.isfile(mp3_file):
        uri_mp3 = Gst.filename_to_uri(mp3_file)
        #print(uri_mp3) # E.g. file:///home/ian/google_talk/yakety_yak.mp3
        main(uri_mp3)

    # Streaming an internet radio station.
    # WARNING: This program will also stream an internet radio station, but
    # control-C won't stop the program. 
    # It is necessary to kill off the process.

    #main('http://live-radio01.mediahubaustralia.com/2LRW/mp3/')


#!/usr/bin/env python3
#
# google_tts_loop.py
#
# This uses the GStreamer (Gst) module playbin
#
# This uses a loop and needs call_back() function(s) for EOS, etc.
# Loop may be aborted via Control-C
#
# Demonstration of using google translate text to speech feature.
# Also plays a local mp3 file and stream an internet radio station.
#
# Requirements:
# Connected to the internet. 
# yakety_yak.mp3 in the same folder as this program
#
# Ian Stewart - 2020-03-25

# Importing...
import sys, os

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GObject', '2.0')
from gi.repository import Gst, GObject

# uri string that requiring language and text message.
uri_string =  'https://translate.google.com/translate_tts?'
uri_string += 'ie=UTF-8&client=tw-ob&tl={}&q={}'

# Insert language and message into uri_string as default for main()
URI = uri_string.format('en-au', 'Hello. I speak with an Australian accent.')

def main(uri=URI):
    """
    Requires the uri to be passed.   
    Initialize: Gst, Instantiate playbin, and get rid of video. loop and bus.
    Set the uri property. 
    Start playing the text to google and receiving the mp3 audio stream.
    Run loop and accept bus_call() interupts, checking for EOS.
    By using try/except then Control-C can be used to stop the program.
    End by changing state to null.
    """
    # Init  - call initialize function.
    player, loop = initialize()

    # Set the uri to be sent to google
    player.set_property('uri', uri)

    # Send text to google, and start streaming the mp3 audio with playbin
    player.set_state(Gst.State.PLAYING)

    # Loop while waiting for audio to finish or interupted with Control-C
    try:
        loop.run()
    except KeyboardInterrupt:
        loop.quit()
        player.set_state(Gst.State.NULL)
        # Skip rest of audio and start next, OR uncomment to stop...
        #sys.exit('\nExit via Control-C')

    # On exiting loop() set playbin state to Null.
    player.set_state(Gst.State.NULL)


def initialize():
    """
    Initialize Gst, instantiate playbin and loop.
    Create a fakesink to bury any video.
    Bus is set up to perfom a call back to def bus_call(bus, message, loop)
    every time a playbin message is generated.
    """
    # Init
    #GObject.threads_init()
    Gst.init(None)

    # Instantiate    
    player = Gst.ElementFactory.make('playbin', 'player')

    # Stop video. Only sending audio to playbin
    fakesink = Gst.ElementFactory.make('fakesink', 'fakesink')
    player.set_property('video-sink', fakesink)

    # Instantiate the event loop.
    loop = GObject.MainLoop()

    # Instantiate and initialize the bus call-back 
    bus = player.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, loop)

    return player, loop


def bus_call(bus, message, loop):
    """
    Call back for messages generated when playbin is playing.
    The End-of-Stream, EOS, message indicates the audio is complete and the
    waiting loop is quit.
    Note: could havre multiple call_back()'s. One for EOS, one for ERROR, etc.
    """
    t = message.type
    #print(t)

    if t == Gst.MessageType.EOS:
        # End-of-Stream therefore quit loop which executes playbin state Null
        #sys.stdout.write('End-of-stream\n')
        #print(t) # <flags GST_MESSAGE_EOS of type Gst.MessageType>
        loop.quit()

    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write('\nError: {}\n{}\n'.format(err, debug))
        # 'Error: gst-resource-error-quark: Could not resolve server name.'
        # Need to be connected to the internet
        loop.quit()

    return True


if __name__=='__main__':

    print('\nType Control-C to skip on to next example...')
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
    print('\nStreaming an internet radio station. Type Control-C to stop...')   
    main('http://live-radio01.mediahubaustralia.com/2LRW/mp3/')


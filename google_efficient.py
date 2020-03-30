#!usr/bin/env python3
#
# google_efficient.py
#
# A more efficient way of using google translates tts.
#
# In previous program examples each time a text is to be converted to speech 
# it requires everything to be re-initialized and re-instantiated.
# 
# This program allows one setup to do text-to-speech, and then repeatedly 
# text can be sent to be converted to speech.
#
# Note: "Text" is the variable used to hold the text to be converted to speech. 
# Avoid using the variable "message" for this as "message" is used to refer
# to the object passed to the call back functions.
# 
# Ian Stewart - 2020-03-30
#
import sys, os
import time
import socket

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GObject', '2.0')
from gi.repository import Gst, GObject

start_text = """
A more efficient way to repeatedly send text for conversion to speech.
Note that Control-C will abort what is currently being spoken.
"""

def google_execute(pipeline, loop, text):
    """
    Called for each message to be converted from text-to-speech.
    """
    # Build the uri and set the uri as a pipline property
    uri = ('https://translate.google.com/translate_tts?'
           'ie=UTF-8&client=tw-ob&tl={}&q={}'
           .format('en-au', text))
    pipeline.set_property('uri', uri)

    pipeline.set_state(Gst.State.PLAYING)  
    
    try:
        loop.run()
    except KeyboardInterrupt:
        print('\n Detected Ctrl-C')

    finally:
        pipeline.set_state(Gst.State.NULL)


def google_setup():
    """ 
    Initialize: Gst, loop
    Build the pipeline template
    Gst.parse_launch() to establish the pipeline
    build the bus call backs.
    Return pipeline and loop. Don't need to return bus
    """
    Gst.init(None)
 
    pipeline_template = """
            playbin
            """
   
    pipeline = Gst.parse_launch(pipeline_template)

    # Instantiate and initialize the bus call-back 
    loop = GObject.MainLoop()

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message::eos", on_eos_message, loop)
    bus.connect("message::error", on_error_message)
    bus.connect("message", on_all_message)

    return pipeline, loop


def on_eos_message(bus, message, loop):
    """EOS - End of Stream"""
    #print("Bus name:", bus.get_name())
    #print(message.type)
    loop.quit()
    pass


def on_error_message(bus, message):
    """Error messages"""
    print("Bus name:", bus.get_name())
    err, debug = message.parse_error()
    print("Error: {}:\n{}".format(err, debug))
    sys.exit("Exited due to the above error.")


def on_all_message(bus, message):
    """Print all messages - If desired."""
    #print("Bus name:", bus.get_name())
    # Uncomment to view all messages for troubleshooting...
    #print(message.type)
    pass


if __name__ == "__main__":

    print(start_text)

    # Setup the pipeline and loop. Plus the bus callbacks
    pipeline, loop = google_setup()

    # Repeatedly send text to google_execute() function.
    for i in range(3):

        text = "This is text number {}".format(i + 1)
    
        google_execute(pipeline, loop, text)

    sys.exit("Exit - Finished speaking these text messages.")


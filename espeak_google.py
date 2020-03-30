#!usr/bin/env python3
#
# espeak_google.py
#
# Manually take the internet up and down while this program is running and see 
# if tts messages can continue to be spoken.
#
# If the network connection is up use google tts, if its down use espeak.
#
# Takes about 30ms to test if the internet is OK.
# Set timeout to 100ms. If internet hasn't responded then switch to espeak.
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

start_message = """
If the internet is available then google_tts will deliver the better sounding 
text-to-speech. If the internet conection drops out then the locally available 
espeak will be used for text-to-speech.

While this program is running repeatedly disconnect and connect to the internet 
to check if switching between the two methods of text-to-speech occurs.

"""


def speak_google(message):
    """ 
    Initialize: Gst, loop and bus.
    Build the pipeline template
    Gst.parse_launch() to establish the pipeline
    Start espeak
    Run loop and accept bus_call() interupts, checking for EOS.
    End by changing state to null.
    """
    start_time = time.time()

    Gst.init(None)

    def on_eos_message(bus, message, loop):
        """EOS - End of Stream"""
        #print("Bus name:", bus.get_name())
        #print(message.type)
        loop.quit()


    def on_error_message(bus, message, loop):
        """Error messages"""
        print("Bus name:", bus.get_name())
        err, debug = message.parse_error()
        print("Error: {}:\n{}".format(err, debug))
        loop.quit()
        sys.exit("Exited due to above error")


    def on_all_message(bus, message, loop):
        """Print all messages - If desired."""
        #print("Bus name:", bus.get_name())
        # Uncomment to view all messages for troubleshooting...
        #print(message.type)
        pass

 
    pipeline_template = """
            playbin
            """
   
    pipeline = Gst.parse_launch(pipeline_template)

    uri = ('https://translate.google.com/translate_tts?'
           'ie=UTF-8&client=tw-ob&tl={}&q={}'
           .format('en-au', message))

    pipeline.set_property('uri', uri)

    # Instantiate and initialize the bus call-back 
    loop = GObject.MainLoop()

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message::error", on_error_message, loop)
    bus.connect("message::eos", on_eos_message, loop)
    bus.connect("message", on_all_message, loop)

    # Get the show on the road.
    pipeline.set_state(Gst.State.PLAYING)  

    loop.run() 

    # On exiting loop() set state to Null.
    pipeline.set_state(Gst.State.NULL)
    loop.quit()

    print("Google time taken: {} milli-secs."
            .format(int((time.time()-start_time) * 1000)))


def speak_espeak(message):
    """ 
    Initialize: Gst, loop and bus.
    Build the pipeline template
    Gst.parse_launch() to establish the pipeline
    Start espeak
    Run loop and accept bus_call() interupts, checking for EOS.
    End by changing state to null.
    """
    start_time = time.time()

    Gst.init(None)

    def on_eos_message(bus, message, loop):
        """EOS - End of Stream"""
        #print("Bus name:", bus.get_name())
        #print(message.type)
        loop.quit()


    def on_error_message(bus, message, loop):
        """Error messages"""
        print("Bus name:", bus.get_name())
        err, debug = message.parse_error()
        print("Error: {}:\n{}".format(err, debug))
        loop.quit()
        sys.exit("Exited due to above error")


    def on_all_message(bus, message, loop):
        """Print all messages - If desired."""
        #print("Bus name:", bus.get_name())
        # Uncomment to view all messages for troubleshooting...
        #rint(message.type)
        pass

    # Instantiate
    pipeline_template = """
            espeak text="{text}" rate={rate} pitch={pitch} voice={voice} 
                   gap={gap} track={track} 
            ! autoaudiosink
            """.format(
                        text=message,
                        rate=0,         # -100 to + 100
                        pitch=0,        # -100 to + 100
                        voice="en-gb",  # See list below
                        gap=0,          # 0 to max Int. i.e. about 20.
                        track=0,        # Huh? What does track do?
                      )

    pipeline = Gst.parse_launch(pipeline_template)

    # Instantiate and initialize the bus call-back 
    loop = GObject.MainLoop()

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message::error", on_error_message, loop)
    bus.connect("message::eos", on_eos_message, loop)
    bus.connect("message", on_all_message, loop)

    # Start
    pipeline.set_state(Gst.State.PLAYING)  

    loop.run() 

    # On exiting loop() set state to Null.
    pipeline.set_state(Gst.State.NULL)
    loop.quit()

    print("Espeak Time taken: {} milli-secs."
            .format(int((time.time()-start_time) * 1000)))


def internet(host="8.8.8.8", port=53, timeout=0.1):
    """
    Check if the internet is avaialble. Allow up to 100 milli-secs to respond.
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


if __name__ == "__main__":

    print(start_message)

    for i in range(10):

        message = "This is message number {}".format(i + 1)
    
        internet_available = internet()

        if internet_available:
            speak_google(message)

        else:
            speak_espeak(message)
        

    sys.exit("Exit - Finished speaking messages")


"""
Notes:

# Bash network connection check
$ nc 8.8.8.8 53 -zv
Connection to 8.8.8.8 53 port [tcp/domain] succeeded!
"""

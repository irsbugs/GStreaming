#!/usr/bin/env python3
#
# mp3_to_wave_loop.py
#
# This uses the GStreamer (Gst) module with its parse_launch() function.
#
# This uses a loop and needs call_back() function(s) for EOS, etc.
#
# Requires a mp3 filename "hello.mp3" to be provided. 
# Creates a wav file with the same name. E.g. "hello.wav"
#
# A mp3 file may be provided as an argument. E.g.
# $ python3 mp3_to_wave_loop.py yakety_yak.mp3
#
#
# Ian Stewart - 2020-03-25

# Importing...
import sys
import os.path
import time
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GObject', '2.0')
from gi.repository import Gst, GObject

MP3_FILE = "hello.mp3"

def convert(mp3_file=MP3_FILE):
    """
    Requires a mp3 file to be passed.   
    Initialize: Gst, loop and bus.
    Build the pipeline template
    Gst.parse_launch() to establish the pipeline
    Start the convertion.
    Run loop and accept bus_call() interupts, checking for EOS.
    End by changing state to null.
    """
    # check the mp3 file
    if not os.path.isfile(mp3_file):
        print("Error: The input file {} does not exist".format(mp3_file))
        sys.exit()

    if not mp3_file.lower().endswith('.mp3'):
        print("Error: The input file {} does not have .mp3 extension".format(mp3_file))
        sys.exit()    

    # create the filename for the wav file
    path_filename = os.path.splitext(mp3_file)[0]
    wav_file = path_filename + ".wav"

    print("Converting: {} to {}.".format(mp3_file, wav_file))

    start_time = time.time()

    # Init
    Gst.init(None)
    loop = GObject.MainLoop()

    pipeline_template = """
            filesrc location={} 
            ! decodebin
            ! audioresample 
            ! audioconvert 
            ! audio/x-raw,format=S24LE,rate=48000 
            ! wavenc 
            ! filesink location={}
            """

    pipeline = Gst.parse_launch(pipeline_template.format(mp3_file, wav_file))

    # Instantiate and initialize the bus call-back 
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message::error", on_error_message, loop)
    bus.connect("message::eos", on_eos_message, loop)
    bus.connect("message", on_all_message, loop)

    #pipe.bus.add_signal_watch()
    pipeline.set_state(Gst.State.PLAYING)  
    loop.run() 

    # On exiting loop() set playbin state to Null.
    pipeline.set_state(Gst.State.NULL)
    loop.quit()

    print("Time taken: {} milli-secs."
            .format(int((time.time()-start_time) * 1000)))


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
    sys.exit()


def on_all_message(bus, message, loop):
    """Print all messages - If desired."""
    #print("Bus name:", bus.get_name())
    #print(message.type)
    pass


if __name__=="__main__":

    if len(sys.argv) < 2:
        print("Error: Please provide the mp3 input file name.")
        print("Continuing, but using default hello.mp3 file.")
        convert()

    else:
        filename = sys.argv[1]
        #print(filename)
        convert(filename)


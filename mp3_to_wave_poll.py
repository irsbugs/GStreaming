#!/usr/bin/env python3
#
# mp3_to_wave_poll.py
#
# This uses the GStreamer (Gst) module with its parse_launch() function.
#
# This uses pipe.get_bus().poll() for EOS and Error detection.
#
# Requires a mp3 filename "hello.mp3" to be provided. 
# Creates a wav file with the same name. E.g. "hello.wav"
#
# The mp3 file may be provided as an argument. E.g.
# $ python3 mp3_to_wave_poll.py yakety_yak.mp3
#
#
# Ian Stewart - 2020-03-25

# Importing...
import sys
import os.path
import time
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

MP3_FILE = "hello.mp3"

def convert(mp3_file=MP3_FILE):
    """
    Requires a mp3 file to be passed.   
    Initialize: Gst
    Build the pipeline template
    Gst.parse_launch() to establish the pipeline
    Start the convertion.
    bus.poll() for EOS or Error.
    End by changing state to null.
    """
    # Check the mp3 file exists
    if not os.path.isfile(mp3_file):
        print("Error: The input file {} does not exist".format(mp3_file))
        sys.exit()

    if not mp3_file.lower().endswith('.mp3'):
        print("Error: The input file {} does not have .mp3 extension".format(mp3_file))
        sys.exit()    

    # Create the filename for the wav file
    path_filename = os.path.splitext(mp3_file)[0]
    wav_file = path_filename + ".wav"

    start_time = time.time()

    # Init
    Gst.init(None)

    # Pipeline template
    pipeline_template = """
            filesrc location={} 
            ! decodebin
            ! audioresample 
            ! audioconvert 
            ! audio/x-raw,format=S24LE,rate=48000 
            ! wavenc 
            ! filesink location={}
            """

    # pipeline launch - pass mp3 and wav file path / names
    pipeline = Gst.parse_launch(pipeline_template.format(mp3_file, wav_file))

    # Start converion
    pipeline.set_state(Gst.State.PLAYING)  

    # wait until things stop
    pipeline.get_bus().poll(Gst.MessageType.EOS | Gst.MessageType.ERROR, 
                          Gst.CLOCK_TIME_NONE)

    # After EOS
    pipeline.set_state(Gst.State.NULL)

    print("Time taken: {} milli-secs."
            .format(int((time.time()-start_time) * 1000)))


if __name__=="__main__":

    if len(sys.argv) < 2:
        print("Error: Please provide the mp3 input file name.")
        print("Continuing, but using default hello.mp3 file.")
        convert()

    else:
        filename = sys.argv[1]
        #print(filename)
        convert(filename)



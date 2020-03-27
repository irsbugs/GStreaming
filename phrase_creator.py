#!/usr/bin/env python3
#
# phrase_creator.py
#
# This uses the GStreamer (Gst) module with its parse_launch() function.
# Uses pipe.get_bus().poll() for EOS and Error detection.
#
# Requires a phrase to be input as a sys.argv. E.g. "The time is"
# This is sent to google and the mp3 stream returned is saved to a file
# E.g. phrase/the_time_is.mp3
#
# This file can be played when returning the time, before google tts adds the
# actual time.
#
# Ian Stewart - 2020-03-25

# Importing...
import sys
import os.path
import time
import string
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

PHRASE = "The cat came back."

def phrase_mp3(phrase=PHRASE):
    """
    Requires a phrase. Check phrase. 
    Create filename from phrase with underscores instead of spaces.   
    Initialize: Gst
    Build the pipeline template
    Gst.parse_launch() to establish the pipeline
    Start the convertion.
    bus.poll() for EOS or Error.
    End by changing state to null.
    """

    phrase = phrase.strip()
    #print(phrase)

    # Create filename...
    # strip punctuation 
    table = str.maketrans('', '', string.punctuation)
    phrase_string = phrase.translate(table)
    # convert all of phrase to lower case
    phrase_string = phrase_string.lower()
    # Join phrase with underscores
    filepath_name = "phrase/" + "_".join(phrase_string.split(" ")) + ".mp3"
    print(filepath_name)

    # Create phrase/ folder if it doesnt exists. Stores the phrases as mp3 files
    if not os.path.isdir("phrase"):
        print("INFO: Creating the directory '{}'".format("phrase/"))
        os.mkdir("phrase")        

    # phrase - Replace spaces with plus signs for sending to google tts
    phrase = "+".join(phrase.split(" "))
    
    # Create the uri
    uri_string =  'https://translate.google.com/translate_tts?'
    uri_string += 'ie=UTF-8&client=tw-ob&tl={}&q={}'
    uri = uri_string.format("en-au", phrase)

    #print(uri)

    start_time = time.time()

    # Init
    Gst.init(None)

    # Pipeline template
    pipeline = """
            {}
            ! decodebin 
            ! audioconvert 
            ! lamemp3enc 
            ! filesink location=./{}
            """

    # pipeline launch - pass mp3 and wav file path / names
    pipe = Gst.parse_launch(pipeline.format(uri, filepath_name))

    # Start converion
    pipe.set_state(Gst.State.PLAYING)  

    # wait until things stop
    pipe.get_bus().poll(Gst.MessageType.EOS | Gst.MessageType.ERROR, 
                          Gst.CLOCK_TIME_NONE)

    # After EOS
    pipe.set_state(Gst.State.NULL)

    print("Time taken: {} milli-secs."
            .format(int((time.time()-start_time) * 1000)))


if __name__=="__main__":

    if len(sys.argv) < 2:
        print("Error: Please provide a quoted phrase.")
        print("Continuing. For testing purposes...")
        phrase_mp3()

    else:
        phrase = sys.argv[1]
        print(phrase)
        phrase_mp3(phrase)




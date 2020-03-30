#!/usr/bin/env python3
#!
# radio_efficient.py
#
# Console menu driven internet radio station streamer.
# Uses GStreamer and playbin plugin which is passed the uri of an internet 
# radio station.
#
# Only intitlizes and instantiates once on launch, not on every time a 
# different station is selected.
#
# Ian Stewart - 2020-03-31
#
# Notes:
#
# Note that AAC streamed internet stations need the Gstreamer "bad".
# $ sudo apt install gstreamer1.0-plugins-bad

# Importing...
import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# For BBC Station info: 
# https://www.astra2sat.com/radio/bbc-radio/bbc-aac-radio-streams/

# Edit this staton list if you wish to add or remove radio stations.
# Each tuple is the name of the radio station and the url.
station_list = [
        ( 
        "Radio New Zealand Concert Program",
        "http://radionz-ice.streamguys.com/concert",
        ),
        ( 
        "Radio New Zealand Nation Program",
        "http://radionz-ice.streamguys.com/national",
        ),
        ( 
        "ABC Sydney 702AM",
        "http://live-radio01.mediahubaustralia.com/2LRW/mp3/",
        ),
        (
        "BBC Radio One",
        "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_radio_one.m3u8",
        ),
        (
        "BBC Radio Two",
        "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_radio_two.m3u8",
        ),
        (
        "BBC Radio Three",
        "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_radio_three.m3u8",
        ),
        (
        "BBC Radio Four",
        "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_radio_fourfm.m3u8",
        ),
        (
        "Coast",
        "http://ais-nzme.streamguys1.com/nz_011_aac",
        ),
        ]


menu_1_heading = "Select Station"
menu_1_list = []  # create_menu_1 generates list from station_list
exit_message_1 = "Exit"


def create_menu(heading, menu_list, exit_message):
    'Create a menu. Accept keyboard input and validate. Return keyboard string'  
    while True:
        # Display a heading
        print("\n {}".format(heading))
        # Display the menu
        for index, item in enumerate(menu_list):
            print("{:>5}. {}".format(str(index + 1), item))
        # Display the exit option
        print("{:>5}. {}".format("0", exit_message))
        # Get input with prompting.
        response = input("\n * Enter your choice [0]: ")
        # Set default response
        if response == "":
            response = "0"

        try:
            # Does response convert to an integer?
            value = int(response)
            # Is the integer within the range?
            if value >= 0 and value <= len(menu_list):
                return response
            else:
                # An integer, but out of range.
                print("\nInvalid entry: {}. Enter a number between 0 and {}\n"
                        .format(response, len(menu_list)))
                continue
        except ValueError as e:
            # A string that cannot be convertded to an integer
            print("\nInvalid entry: {}. Enter a number between 0 and {}\n"
                    .format(response, len(menu_list)))
            continue


def create_menu_1():
    'Launch Menu to select radio station to play.'

    while True:
        # Pass: heading, list of items, exit message. Returns numeral string
        menu_1_list = []
        for index, item in enumerate(station_list):
            menu_1_list.append(item[0])
       
        response = create_menu(menu_1_heading, menu_1_list, exit_message_1)

        if response == "0":
            # Return to main menu
            return response # "0"

        if response != "0":
            # The response string is used to selected the radio station.
            # Select the station
            station_index = int(response) - 1

            print("\n Station selected: {}"
                    .format(station_list[station_index][0]))

            # Return the uri
            return station_list[station_index][1]


def radio(pipeline, loop, uri):
    'Use Gstreamer playbin to play the station based on the supplied uri'

    pipeline.set_property('uri', uri)

    print("\n Streaming... Type control-C to return to menu")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()

    except KeyboardInterrupt:
        print('\n Station deselected via Ctrl-C')

    finally:
        pipeline.set_state(Gst.State.NULL)
 

def radio_start():
    'Initialize and instantiate'
    # Init
    Gst.init(None)

    pipeline_template = """
            playbin
            """   
    pipeline = Gst.parse_launch(pipeline_template)

    # Instantiate and initialize the bus call-back 
    loop = GLib.MainLoop()

    # Binding End-of-Stream-Signal on source pipe
    pipeline.bus.add_signal_watch()
    pipeline.bus.connect("message::eos", on_eos, loop)
    pipeline.bus.connect("message::error", on_error)
    # Uncomment to view all messages.
    #pipeline.bus.connect("message", on_all_message)

    return pipeline, loop


def on_eos(bus, message, loop):
    'End of Stream - Huh? Should not happen with a radio station stream'
    print('Received End-of-Stream')
    loop.quit()


def on_error(bus, message):
    'Exit is error. E.g. Internet connection failed.'
    print("Bus name:", bus.get_name())
    error, debug = message.parse_error()
    print("Error: {}:\n{}".format(error.code, debug))
    sys.exit("Exited due to the above error.")


def on_all_message(bus, message):
    'Print all messages - May be desirable for troubleshooting.'
    #print("Bus name:", bus.get_name())
    print(message.type)
    pass


def main():
    'Call radio_start() to do setup. Call menu creation. Call to play radio.'

    pipeline, loop = radio_start()

    while True:
        uri = create_menu_1()
        #print(uri)
        if uri == "0":
            sys.exit("\n bye...")
        else:
            radio(pipeline, loop, uri)


if __name__ == "__main__":

    main()



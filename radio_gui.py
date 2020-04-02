#!/usr/bin/env python3
#!
# radio_gui.py
#
# Uses the Gstreamer plugin "playbin".
# Create a Gtk window and display a list of internet radio stations
# Includes mute and volume control
# Command line setting of initial station, mute and volume
#
# Ian Stewart 2020-04-03
#
import sys, os
import argparse
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, Gtk

# Station to play on launch. Enter the integer. Starts at 1
# Enter 0 for no station to be selected on launch.
START_STATION_NUMBER = 1
START_MUTED = False  # <-- Boolean True or False
START_VOLUME = 50  # <--- Range from 0 to 100

# Edit this list to add and remove stations. 
# Place your preferred station at the start of the list and it will play on launch.
# Tuples require a name and the url of the internet station
radio_station_list = [
        ( 
        "RNZ Concert Program",
        "http://radionz-ice.streamguys.com/concert",
        ),
        ( 
        "RNZ Nation Program",
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
        (
        "Radio Hauraki",
        "http://ais-nzme.streamguys1.com/nz_009_aac",
        ),
        (
        "NewTalk ZB",
        "http://ais-nzme.streamguys1.com/nz_002_aac",
        ),
        ]


def create_gui(radio_station_list):
        'Initialize and instantiate pipeline'
        pipeline = radio_start()

        # Create the window
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Internet Radio")
        window.set_default_size(100, 100)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        # 'CENTER', 'CENTER_ALWAYS', 'CENTER_ON_PARENT', 'MOUSE', 'NONE',
        
        vbox = Gtk.VBox()
        window.add(vbox)

        # Box to hold list of radio stations
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_left(20)
        box.set_margin_right(20)


        def cb_radio_button(radiobutton, index):
            'Call back to change radio stations'
            if radiobutton.get_active():
                # Change title to newly selected station
                #window.set_title("{}".format(radiobutton.get_label()))

                # Stop previous radio station
                pipeline.set_state(Gst.State.NULL)

                # Select and start playing new station.
                uri = radio_station_list[index][1]
                pipeline.set_property('uri', uri)
                pipeline.set_state(Gst.State.PLAYING)


        # Create the radio buttons based on radio_station_list
        # Radio buttons as a group so they are referenced by their index.
        rb = []

        # Create first radio button
        rb.append(Gtk.RadioButton.new_with_label_from_widget(
                None, radio_station_list[0][0]))        
        rb[0].connect("toggled", cb_radio_button, 0)
        box.pack_start(rb[0], False , False ,0)

        # Create remaining radio buttons
        for index, option in enumerate(radio_station_list[1:]):
            rb.append(Gtk.RadioButton.new_with_label_from_widget(
                    rb[0], radio_station_list[index + 1][0]))
            box.pack_start(rb[index + 1], False, False, 0)
            rb[index+1].connect(
                    "toggled", cb_radio_button, index + 1)
        
        # Add dummy - which is hidden
        rb.append(Gtk.RadioButton.new_with_label_from_widget(rb[0], "dummy")) 
        box.pack_start(rb[len(radio_station_list)], False, False, 0)  

        # Set initial station or the dummy station
        if args.station < 1 or args.station > len(radio_station_list):
            # Select dummy
            rb[len(radio_station_list)].set_active(True)
        else:
            # Station 0 needs a wiggle go to dummy first then the station.
            rb[len(radio_station_list)].set_active(True)        
            rb[args.station - 1].set_active(True)
            

        # Add a horizontal seperator line
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        #box.pack_start(separator, True, True, 0)

        # Add the muting
        def cb_checkbox(checkbox):
            'Mute toggle on / off'
            if checkbox.get_active():
                pipeline.set_property('mute', True)
            else:
                pipeline.set_property('mute', False)


        # Add a mute checkbox
        checkbox = Gtk.CheckButton(label = "Mute")
        checkbox.connect('toggled', cb_checkbox)
        checkbox.set_active(args.muting)
        box.pack_start(checkbox, True, True, 0)

        # Volume control using Scale widget
        def cb_scale_moved(scale):
            'Adjust the volume 0 to 100 to be in range 0 to 1'
            pipeline.set_property('volume', scale.get_value()/100)


        # Scale new_with_range(orientation, min, max, step) 0 to 100
        scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL, 
                min=0, max=100, step=1)
        scale.connect("value-changed", cb_scale_moved)
        # Set initial volume based on args.volume or default of START_VOLUME
        scale.set_value(args.volume)
        box.pack_start(scale, True, True, 0)

        vbox.add(box)

        # Get the show on the road.
        window.show_all()


        # Hide the dummy entry at the end of the list
        # This hide() needs to go after window.show_all()
        rb[len(radio_station_list)].hide()


        Gtk.main()
        pipeline.set_state(Gst.State.NULL)
        window.destroy()


def radio_start():
    'Initialize and instantiate'
    # Init
    Gst.init(None)

    pipeline_template = """
            playbin
            """   
    pipeline = Gst.parse_launch(pipeline_template)

    # Binding End-of-Stream-Signal on source pipe
    pipeline.bus.add_signal_watch()
    pipeline.bus.connect("message::eos", on_eos)
    pipeline.bus.connect("message::error", on_error)
    # Uncomment to view all messages.
    #pipeline.bus.connect("message", on_all_message)

    return pipeline


def on_eos(bus, message):
    'End of Stream - Huh? Should not happen with a radio station stream'
    print('Received End-of-Stream')
    #loop.quit()


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


if __name__ == "__main__":

    # Use argparse for station number, volume and muting
    
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--station", 
                        type=int, 
                        default=START_STATION_NUMBER,
                        help="Number of the initial station. 0 is no station.")

    parser.add_argument("-v", "--volume", 
                        type=int, 
                        default=START_VOLUME,
                        help="Set initial Volume level. Range 0 to 100")

    parser.add_argument('--muting', dest='muting', action='store_true')
    parser.add_argument('--no-muting', dest='muting', action='store_false')
    parser.set_defaults(muting=START_MUTED)

    args = parser.parse_args()

    create_gui(radio_station_list)





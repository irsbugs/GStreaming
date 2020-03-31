#!/usr/bin/env python3
#!
# radio_gui.py
#
# Uses the Gstreamer plugin "playbin".
# Create a Gtk window and display a list of internet radio stations
#
# Ian Stewart 2020-03-31
#
import sys, os
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, Gtk

# Edit this list to add and remove stations. 
# Place you preferred station at the end of the list.
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
        ]


def create_gui(radio_station_list):
        'Initialize and instantiate pipeline'
        pipeline = radio_start()

        # Create the window
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Internet Streaming Radio")
        window.set_default_size(300, 0)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        # 'CENTER', 'CENTER_ALWAYS', 'CENTER_ON_PARENT', 'MOUSE', 'NONE',
        
        # Box to hold list of radio stations
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_left(20)
        box.set_margin_right(20)

        def cb_radiobutton(radiobutton, index):
            'Call back to change radio stations'
            if radiobutton.get_active():
                # Change title to newly selected station
                window.set_title("{}".format(radiobutton.get_label()))

                # Stop previous radio station
                pipeline.set_state(Gst.State.NULL)

                # Select and start playing new station.
                uri = radio_station_list[index][1]
                pipeline.set_property('uri', uri)
                pipeline.set_state(Gst.State.PLAYING)

        # Create the radio buttons based on radio_station_list
        radiobutton1 = Gtk.RadioButton(label = radio_station_list[0][0])
        radiobutton1.connect('clicked', cb_radiobutton, 0)
        box.pack_start(radiobutton1, True, True, 0)

        for i in range(1, len(radio_station_list)):
            radiobutton = Gtk.RadioButton(label = radio_station_list[i][0])
            radiobutton.connect('clicked', cb_radiobutton, i)
            radiobutton.join_group(radiobutton1)
            box.pack_start(radiobutton, True, True, 0)

        window.add(box)

        # Force the last item on the list be selected.
        radiobutton.set_active(1)

        # Get the show on the road.
        window.show_all()
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

    create_gui(radio_station_list)





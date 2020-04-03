#!/usr/bin/env python3
#
# camera_local.py
#
# Open a Gtk Window and display view from your laptop webcam. 
#
# Warning: Unstable. May fail on starting. Timing issues?
#
# Ian Stewart 2020-04-02
#
import time
import sys, os
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject, Gtk

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
gi.require_version('GstVideo', '1.0')
from gi.repository import GdkX11, GstVideo


class Camera_Window(object):
    def __init__(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Camera")
        window.set_default_size(400, 330)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        vbox = Gtk.VBox()
        window.add(vbox)

        # Add a movie window and a start button
        self.movie_window = Gtk.DrawingArea()
        vbox.add(self.movie_window)

        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)
        self.button = Gtk.Button("Start")
        self.button.connect("clicked", self.start_stop)
        hbox.pack_end(self.button, False, False, 0)

        # Pipline for webcam with a clock overlay
        pipeline_template = """
            v4l2src device=/dev/video0
            ! videoconvert 
            ! videoscale 
            ! video/x-raw,width=320,height=240
            ! clockoverlay shaded-background=true font-desc="Sans 16" 
            ! autovideosink
            """
        self.pipeline = Gst.parse_launch(pipeline_template) 

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

        window.show_all()

        # Cant start here. Needs GUI all up and running first.
        #self.pipeline.set_state(Gst.State.PLAYING)


    def start_stop(self, w):
        if self.button.get_label() == "Start":
            self.button.set_label("Exit")
            self.pipeline.set_state(Gst.State.PLAYING)
        else:
            self.pipeline.set_state(Gst.State.NULL)
            sys.exit()


    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.button.set_label("Start")

    def on_sync_message(self, bus, message):
        #print("on_sync_message")
        if message.get_structure().get_name() == 'prepare-window-handle':
            #print("Detected: 'prepare-window-handle'")
            imagesink = message.src
            #imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_window_handle(self.movie_window.get_property('window').get_xid())
        else:
            #print("Message structure name:", message.get_structure().get_name())
            pass

GObject.threads_init()
Gst.init(None)     
# Call the class, then run the loop ~ Gtk.main()   
Camera_Window()
Gtk.main()

"""
Note: 
If try to start on launching the Camera_Window() then...

$ python3 camera_local.py 
[xcb] Unknown request in queue while dequeuing
[xcb] Most likely this is a multi-threaded client and XInitThreads has not been called
[xcb] Aborting, sorry about that.
python3: ../../src/xcb_io.c:165: dequeue_pending_request: Assertion `!xcb_xlib_unknown_req_in_deq' failed.
Aborted (core dumped)

Seems to need to get GUI window displayed and then use the "Start" button.
"""


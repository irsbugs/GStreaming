#!/usr/bin/env python3
#
# camera_browser.py
#
# Launch a Gtk Window with description of how this program works.
# Open a tab on you web-browser.
# Enable camera and stream to tcp port
# Camera is displayed on the web-browser.
#
# Ian Stewart 2020-04-03
#
import sys, os
import webbrowser
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject, Gtk

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
gi.require_version('GstVideo', '1.0')
from gi.repository import GdkX11, GstVideo

text_message= """
<b>Camera Browser</b>

This program will launch a web-browser window and open: 

http://127:0.0.1:8080. 

The program will turn on the camera on your laptop and broadcast the camera's images using a tcp server broadcasting on the 127.0.0.1 port 8080 address.

The GStreamer pipeline code is:

pipeline_template = '''
    v4l2src device=/dev/video0
    ! videoconvert 
    ! videoscale 
    ! video/x-raw,width=400,height=400
    ! clockoverlay shaded-background=true font-desc="Sans 16" 
    ! theoraenc 
    ! oggmux 
    ! tcpserversink host=127.0.0.1 port=8080
    '''

self.pipeline = Gst.parse_launch(pipeline_template) 

clockoverlay adds the wall clock time to the video being displayed.

"""

class Camera_Window(object):
    def __init__(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Camera Browser")
        window.set_default_size(450, 550)
        window.connect("destroy", Gtk.main_quit, "WM destroy")

        vbox = Gtk.VBox()
        window.add(vbox)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)

        self.textview = Gtk.TextView()
        self.textview.set_border_width(10)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.insert_markup(self.textbuffer.get_end_iter(),
                text_message, -1)
        scrolledwindow.add(self.textview)
        vbox.add(scrolledwindow)

        hbox = Gtk.HBox()
        self.button = Gtk.Button("Exit")
        self.button.connect("clicked", self.exit)
        hbox.pack_end(self.button, False, False, 0)

        vbox.pack_start(hbox, False, False, 0)


        pipeline_template = """
            v4l2src device=/dev/video0
            ! videoconvert 
            ! videoscale 
            ! video/x-raw,width=400,height=400
            ! clockoverlay shaded-background=true font-desc="Sans 16" 
            ! theoraenc 
            ! oggmux 
            ! tcpserversink host=127.0.0.1 port=8080
            """

        self.pipeline = Gst.parse_launch(pipeline_template) 

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

        window.show_all()

        webbrowser.open_new_tab('http://127.0.0.1:8080')

        self.pipeline.set_state(Gst.State.PLAYING)

    
    def exit(self, w):
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
Camera_Window()
Gtk.main()


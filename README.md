# GStreamer - Gst

## An Introduction to using GStreamer in Python3 Programs

This is a collection of Python3 programs to demonstate features of the **GStreamer** (Gst) module from the **GObject Introspection** (gi) repository. The focus is on streaming audio and the use of *google translates text-to-speech* (tts) facility. These programs were developed on a Ubuntu/Mate 18.04 Linux laptop.

Previously my Python approach to using *google translates tts* included the use of the urllib module to send text to google translate which was received back in spoken form as a stream of mp3 data. This data was fed into a mp3 player. Refer to the program `google_tts_urllib.py` as an example. 

This collection of programs uses GStreamer and its plugin's as an alternative to this urllib/mp3 player solution. 

In Python the GStreamer library is imported as follows:
```
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
```

When a program requests data to be streamed it needs to have a way to continue running until it has received all of the stream. With Gstreamer the ways of doing this are by the simple *polling* method or by the more complex method of *looping* and using *call backs*.

Refer to the programs:

* **google_tts_poll.py**
* **google_tts_loop.py**

In these programs modify the code below the line `if __name__ == "__main__:"` to experiment with your own text to speech messages, playing mp3 files or streaming an internet radio station. Also place the demo mp3 file `yakety_yak.mp3` into the same folder as these programs to hear a demonstration of playing from a uri that is a local file.

When *polling* is used then Control-C will not abort what is currently being streamed. It is necessary to wait until completion. In the case of streaming an internet radio staion it never completes. Therefore it requires killing the process.

However, with *looping*, the loop may be broken with a Control-C and this can stop the program. The looping may be implemented as follows:
```
try:
    loop.run()
except KeyboardInterrupt:
    loop.quit()
    player.set_state(Gst.State.NULL)
    sys.exit('\nExit via Control-C')
```
Thus a Control-C will interupt the streaming and exit the program. 

Note that the loop method is not contained in the *Gst* library. It is however in the *GObject* or *GLib* libraries. Thus it needs to be imported, instantiated and controlled with either of the following:

```
import gi
gi.require_version('GLib', '2.0')
from gi.repository import GLib
loop = GLib.MainLoop()
loop.run()
loop.quit()
```
or...
```
import gi
gi.require_version('GObject', '2.0')
from gi.repository import GObject
loop = GObject.MainLoop()
loop.run()
loop.quit()
```

In both of these *poll* and *loop* programs one line of the code is:
```
player = Gst.ElementFactory.make('playbin', 'player')
```

Of the four catagories of plugins, **playback** is one of the plugins for the *base* set for GStreamer. [Playback](https://gstreamer.freedesktop.org/documentation/playback/index.html?gi-language=c) has eleven features of which one of them is **playbin**. [Playbin](https://gstreamer.freedesktop.org/documentation/playback/playbin.html?gi-language=c) provides a stand-alone everything-in-one abstraction for an audio and/or video player. Thus playbin is the only plugin required for the *google_tts_poll.py* and *google_tts_loop.py* programs. This makes the code simple and perhaps faster in its execution than with the *google_tts_urllib.py*.

## Background to GStreamer

Before moving on to more Python programs it helps to have an understanding of the backgound to GStreamer and its Python bindings.

Code examples that use GStreamer in a program will most often be found to be in the C programming language. When using these examples they need to be converted to Python. For example in the C language a line of code may be:
```
player = gst_element_factory_make ("playbin", "player");
```
In Python this is written as:
```
player = Gst.ElementFactory.make('playbin', 'player')
```
Computer programs are often written in C in order to have good performance. When a C library of source code is compiled to produce the native executable C file, it can also generate a metadata file. Different languages have a middleware layer called **GObject Introspection** (gi) which read this metadata and automatically provide bindings to call into the C executable code. Thus Python bindings are automatically generated. This means that if the C program is changed, it is an easy and automated process to change the Python bindings. Other languages that can automatically create these bindings are C++, Java, Ruby, Common Lisp, and .NET/Mono. 

There are over one hundred C programs that have the **Python GObject Introspection** (PyGObject) bindings. GStreamer is one of them. In the case of GStreamer it also has hundreds of plugins that enhance its features.

A [Python GStreamer API reference manual](https://lazka.github.io/pgi-docs/#Gst-1.0) has been automatically created and posted on a github website. For a documentation example for the above code, there is a description of the API for the [Gst.ElementFactory.make()](https://lazka.github.io/pgi-docs/Gst-1.0/classes/ElementFactory.html#Gst.ElementFactory.make) function. This [PyGObject API reference](http://lazka.github.io/pgi-docs/) also describes the bindings for more than one hundred other C libraries. 

While most of the tutorials for using GStreamer are not specifically for the Python language, there is [Python GStreamer Tutorial](https://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.html), however it is from 2015 and examples use Python2. Thus it may require minor modifications to the code be run under Python3.

See Links section below for references to more documentation.

## Gst.parse_launch()

In the above programs the "all-in-one" plugin **playbin** was used. Thus playbin was a **pipeline** of *one* plugin. The code...
```
player = Gst.ElementFactory.make('playbin', 'player')
```
could instead have been built in a pipleine...
```
player = Gst.parse_launch('playbin')
```
and, instead of *player*, we could use the more applicable word *pipeline*...
```
pipeline = Gst.parse_launch('playbin')
pipeline.set_property('uri', uri)
pipeline.set_state(Gst.State.PLAYING) 
```

There will be cases where a pipeline of multiple plugins needs to be built to meet the requirements of the Python program. In this case the Python program will use the **Gst.parse_launch()** function. The arguments for each plugin in the pipeline are  exclamation mark (!) delimited. Thus the Python code for a program that converts a mp3 file to a wav file will be like this:
```
pipeline = Gst.parse_launch("filesrc location=hello.mp3 ! decodebin ! audioresample ! audioconvert ! audio/x-raw,format=S24LE,rate=48000 ! wavenc ! filesink location=hello.wav")
```
The above is somewhat difficult to read. The code may be re-written so its easier to comprehend as follows...
```
mp3_file = "hello.mp3"
wav_file = "hello.wav"

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
```
Two programs provided that use the Gst.parse_launch() function are:

* **mp3_to_wave_loop.py**
* **mp3_to_wave_poll.py**

Note that the *hello.mp3* file will need to be in the same folder as these program to test the default conversion of mp3 to wave file. If the *yakety_yak.mp3* file is in the folder then use it to create the *yakety_yak.wav* file with:
```
$ python3 mp3_to_wave_loop.py yakety_yak.mp3
```

## gst-launch-1.0 and gst-inspect-1.0

With a computer using a Ubuntu distro, then it includes two GStreamer utilities that run from the bash prompt. The **gst-launch-1.0** performs in a similar way to the Python code *Gst.parse_launch()*. It is used to build and test pipelines. For example the following will build a pipeline that starts mp3 data streaming from a radio station and playing on your computer.
```
$ gst-launch-1.0 playbin uri=http://live-radio01.mediahubaustralia.com/2LRW/mp3/
```
As mentioned above the Python code using the poll() method of playing a radio station could not be stopped with Control-C. The above gst-launch-1.0 utility will stop with a Control-C. However using the *-e* option in the command string is considered a more graceful way of stopping.
```
$ gst-launch-1.0 -e playbin uri=http://live-radio01.mediahubaustralia.com/2LRW/mp3/
```
The *-e* is not supported in the Python *Gst.parse_launch()* function.

The **gst-inspect-1.0** utility allows you to review what plugins are installed for GStreamer. Your distro will probably have shipped with two categories of plugins. The *base* and the *good*. Run the utility to review the total number of plugins installed:
```
$ gst-inspect-1.0
gio:  giosink: GIO sink
gio:  giosrc: GIO source
gio:  giostreamsink: GIO stream sink
... cut ...
cluttergst3:  clutterautovideosink: Generic bin
staticelements:  bin: Generic bin
staticelements:  pipeline: Pipeline object

Total count: 108 plugins, 561 features
```

Of these 108 plugins one is *playback* which has 11 features of which one of these is *playbin*:
```
playback:  parsebin: Parse Bin
playback:  urisourcebin: URI reader
playback:  uridecodebin3: URI Decoder
playback:  uridecodebin: URI Decoder
playback:  decodebin3: Decoder Bin 3
playback:  decodebin: Decoder Bin
playback:  streamsynchronizer: Stream Synchronizer
playback:  subtitleoverlay: Subtitle Overlay
playback:  playsink: Player Sink
playback:  playbin3: Player Bin 3
playback:  playbin: Player Bin 2
```
Although there are many other plugins there are four main catagories; *base*, *good*, *bad*, and *ugly*. These may be installed with `$ sudo atp install`. 
```
gstreamer1.0-plugins-base - GStreamer plugins from the "base" set
gstreamer1.0-plugins-good - GStreamer plugins from the "good" set
gstreamer1.0-plugins-bad - GStreamer plugins from the "bad" set
gstreamer1.0-plugins-ugly - GStreamer plugins from the "ugly" set
```
It is likely that your distro included the *base* and the *good*. If you wish to listen to a radio station that steams AAC data, then you will need to install the *bad* set of plugins. For example if this station has an error and does not play:
```
$ gst-launch-1.0 -e playbin uri=http://radionz-ice.streamguys.com/concert
```
Install the *bad* plugin with:
```
$ sudo apt install gstreamer1.0-plugins-bad
```
Using *gst-inspect-1.0* you will see that the plugin and feature counts have increased:
```
$ gst-inspect-1.0 
... cut ...
Total count: 230 plugins, 790 features
```
You may also specifically check if the AAC audio decoder is now installed with:
```
$ gst-inspect-1.0 faad
Factory Details:
  Rank                     secondary (128)
  Long-name                AAC audio decoder
  Klass                    Codec/Decoder/Audio
  Description              Free MPEG-2/4 AAC decoder
... cut ...  
  Source module            gst-plugins-bad
  Source release date      2019-05-29
  Binary package           GStreamer Bad Plugins (Ubuntu)
... cut ...  
```

## Recording a mp3 stream to a file

The next two programs are:
* **phrase_creator.py**
* **time_google_tts.py**

Note copy the folder *phrase* and its contents to the folder you place these programs in.

If you want *google translate tts* to tell you the time then the response will be something like, "The time is 1 30 pm", in which the response the first piece of speech, "The time is", never changes. Only the time component of this speech changes. Thus "The time is" could be recorded as a local mp3 file. This would be played first, and then the calculated time would be sent as text to *google translate tts* such that the returned mp3 stream would just be the time.

This may be a bit pointless, but possibly it could be useful if you lost your network connection and had to switch to, say, a locally installed *espeak* to perform the tts. At least the first part of the response sentence would have good speech quality even if the last part from *espeak* was a bit like a Dalek.

Run the **phrase_creator.py** program like this:
```
$ python3 phrase_creator.py "The quick brown fox."
```
Check that a mp3 file was created and can be played...
```
$ mpv phrase/the_quick_brown_fox.mp3
```

The **time_google_tts.py** program is designed to play one of the local mp3 files in the *phrase/* folder. These are *the_time_is.mp3* and *todays_date_is.mp3*. After this the time or date is determined and this is sent as text to *google translate tts*. The response is then appended to what has been spoken. Run the program like this:

```
$ python3 time_google_tts.py time

$ python3 time_google_tts.py date
```
If running on a Windows platform see the note at the bottom of the *time_google_tts.py* program.

## Internet Radio.

The next program is:
* **radio.py**

This is a console menu driven internet radio station streamer that uses GStreamer *playbin* which is passed the uri of an internet radio station.

It uses loop and call backs, rather than polling so that Control-C will stop the station that is being listened to. This is done through using try: / except: 
```
try:
    mainloop.run()
    except KeyboardInterrupt:
        print('\n Station deselected via Ctrl-C')

    pipe.set_state(Gst.State.NULL)
```
Without the above a Control-C would have no effect, and therefore you could not get back to the menu to select another radio station.

Note that AAC streamed internet stations needed the Gstreamer "bad". You can check what is installed on you computer with
```
$ apt list --installed
```
At the start of the program edit the *station_list* to add stations that you wish to listen to.

## Espeak

**Espeak** is a text-to-speech synthesizer that is installed on your computer and does not require internet access. There is also an Espeak plugin for GStreamer.

The program...

* **espeak.py**

...demonstrates the functionality of *espeak* with GStreamer. See the "Notes" section at the bottom of the program for more information.

Installation of espeak involves:
```
$ sudo apt install espeak-ng
$ sudo apt install gstreamer1.0-espeak
```

Test espeak-ng as follows:
```
$ espeak-ng "hello"
```
Test the GStreaming of espeak
```
$ gst-launch-1.0 espeak text="hello using alsasink" ! alsasink
$ gst-launch-1.0 espeak text="hello using pulsesink" ! pulsesink
$ gst-launch-1.0 espeak text="hello using autoaudiosink" ! autoaudiosink

$ gst-launch-1.0 espeak text="hello" rate=0 pitch=0 ! autoaudiosink
$ gst-launch-1.0 espeak text="hello" rate=-50 pitch=-100 ! autoaudiosink

$ gst-launch-1.0 espeak text="You can change the speed" ! speed speed=1.0 ! pulsesink

$ gst-inspect-1.0 espeak
```
To run the epeak.py program:
```
$ python3 espeak.py "Hello this is espeak plugin for Gstreamer talking"
```

## Espeak and Google switch

The program...

* **espeak_google.py**

... is designed to check the status of the internet and if it is up it will send text to *google translates tts* servers to be returned as a mp3 data stream. If the network goes down then this is detected and the text is sent to *espeak* to provide the text-to-speech.

While running *espeak_google.py* enable and disable your internet connection. The text to speech method that is used will automtically switch.

The objective is that by default you will use the internet for the better text to speech voice quality, however in the cases where the internet is unavailable, then you can still run your program.


## More Efficient Program Design

In the above programs the design has been primarily to perform only one GStream text-to-speech activity and then close down the program. When this design is used for repeatedly performing text-to-speech then initializaton and instantiation are repeated each time. A more efficient design is to do these setup activities once when the program is launched and then repeatedly performs the main test-to-speech activity. The program...

* **google_efficient.py**

...contains a `def google_setup():` method that is called once to intialize and instantiate and it returns the GStream pipeline and the loop objects. The `def google_execute(pipeline, loop, text):` method is then able to repeatedly perform text-to-speech activities.

The *radio.py*, internet radio station program above, repeated the initialization and instantiation each time a radio station was selected. The program...

* **radio_efficient.py**

... contains a *radio_start()* function so the initialization and instantiation is only done once on launching. After this the *radio()* function changes the stations by changing the *playbin* set_property for the uri.


## GUI Interface and Streaming

The program...

* **radio_gui.py**

...is based on the *radio_efficient.py* code, but uses the Gtk GUI interface to produce a window from which to select the radio stations instead of a menu on a console terminal. Every GUI has its own loop structure to maintain the window. Thus when streaming with the *playbin* plugin there is no need to create a loop specifically to maintain the streaming. With Gtk the line of code that maintains the loop is `Gtk.main()`.

The `radio_gui.py` program has a set of Gtk radio buttons for radio station selection. These buttons all have the same call back function. The GStream pipeline only contains the *playbin* plugin. Thus to change stations it is merely a matter of setting the pipeline state to Null to stop the previous station from continuing to stream. Then setting the pipeline property for the uri to the new station will commence streaming of the new station once `pipeline.set_state(Gst.State.PLAYING)` occurs. The call back used is as follows:  

```
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
```
The program also includes a mute checkbox and a volume sliding scale control. The *mute* and *volume* are properties of the *playbin* plugin. In the program with *playbin* instantitated as *pipline* the callbacks are as follows:
```
def cb_checkbox(checkbox):
    'Mute toggle on / off'
    #print(checkbox.get_active())
    if checkbox.get_active():
        pipeline.set_property('mute', True)
    else:
        pipeline.set_property('mute', False)
```
```
def cb_scale_moved(scale):
    'Adjust the volume 0 to 1'
    pipeline.set_property('volume', scale.get_value())
```

## Links

The following are GStreamer links that may be useful:

GStreamer [website](https://gstreamer.freedesktop.org/modules/gstreamer.html)

GStreamer [code repository](https://gitlab.freedesktop.org/gstreamer/gstreamer).

A GStreamer Application Development Manual (1.6.0), in C, is avaialble in [pdf](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.698.7207&rep=rep1&type=pdf). Section 20.1 on page 112 describes using the *playbin* plugin.

[Python GStreamer Tutorial](https://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.html). Unfortunately it is in Python2. There are some print statements, etc. that need to be converted to print() for Python3.

GStreamer API description of [playbin](https://gstreamer.freedesktop.org/documentation/playback/playbin.html?gi-language=c)

[Program Creek](https://www.programcreek.com/python/) provides sample python code that uses [Gst](https://www.programcreek.com/python/index/7110/gi.repository.Gst). For example code examples of [Gst.parse_launch](https://www.programcreek.com/python/example/88576/gi.repository.Gst.parse_launch)

## Author

Ian Stewart

2020-03-28

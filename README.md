# GStreamer - Gst

## An Introduction to using GStreamer in Python3 Programs

This is a collection of python3 programs to demonstate features of the **GStreamer** (Gst) module from the gi repository. The focus is on streaming audio and the use of google translates text-to-speech (tts) facility.

Previously my python approach to using google tts included the use of the urllib module to send text to google translate which was received back in spoken form as a stream of mp3 data. This data was fed into a mp3 player. Refer to the program `google_tts_urllib.py` as an example. 

This collection of programs uses GStreamer and its plugin's as an alternative to this urllib/mp3 player solution. 

In python the GStreamer library is imported as follows:
```
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
```

When a program requests data to be streamed it needs to have a way to continue running until it has received all of the stream. With Gstreamer the ways of doing this are by the simple *polling* method or by the more complex method of *looping* and using *call backs*.

Refer to the programs:

* google_tts_poll.py
* google_tts_loop.py

In these programs modify the code below the line `if __name__ == "__main__:"` to experiment with your own text to speech messages, playing mp3 files or streaming an internet radio station. Also place the demo mp3 file `yakety_yak.mp3` into the same folder as these programs to hear a demonstration of playing from a uri that is a local file.

When polling is used then Control-C will not abort what is currently being streamed. It is necessary to wait until completion. In the case of streaming an internet radio staion it never completes. Therefore it is necessary to kill the process.

However, with looping, the loop may be halted with a Control-C and this can stop the program. The looping may be implemented as follows:
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

In both of these poll and loop programs one line of the code is:
```
player = Gst.ElementFactory.make('playbin', 'player')
```

Of the four catagories of plugins, **playback** is one of the plugins for the base set for GStreamer. [Playback](https://gstreamer.freedesktop.org/documentation/playback/index.html?gi-language=c) has eleven features of which one of them is **playbin**. [Playbin](https://gstreamer.freedesktop.org/documentation/playback/playbin.html?gi-language=c) provides a stand-alone everything-in-one abstraction for an audio and/or video player. Thus playbin is the only plugin required for the *google_tts_poll.py* and *google_tts_loop.py* programs. This makes the code simple and perhaps faster in its execution than with the *google_tts_urllib.py*.

## Background to GStreamer

Before moving on to more programs it helps to have an understanding of the backgound to GStreamer and its python bindings.

Code eaxmples for using GStreamer in a program will most often be found to be in the C programming language. When using these examples they need to be converted to python. For example in the C language a line of code may be:
```
player = gst_element_factory_make ("playbin", "player");
```
In Python this is written as:
```
player = Gst.ElementFactory.make('playbin', 'player')
```
Computer programs are generally written in C in order to have good performance. When a C library of source code is compiled to produce the native executable C file, it can also generate a metadata file. Different languages have a middleware layer called **GObject Introspection** (gi) which read this metadata and automatically provide bindings to call into the C library. Thus python bindings are automatically generated. This means that if the C program is changed, it is an easy and automated process to change the python bindings. Other languages that can automatically create these bindings are C++, Java, Ruby, Common Lisp, and .NET/Mono. 

There are over one hundred C programs that have the **Python GObject Introspection** (PyGOBject) bindings. GStreamer is one of them. In the case of GStreamer it also has hundreds of plugins that enhance its features.

A [Python GStreamer API reference manual](https://lazka.github.io/pgi-docs/#Gst-1.0) has been automatically created and posted on a github website. For a documentation example for the above code, the description of the API for the [Gst.ElementFactory.make()](https://lazka.github.io/pgi-docs/Gst-1.0/classes/ElementFactory.html#Gst.ElementFactory.make) function. This [PyGObject API reference](http://lazka.github.io/pgi-docs/) also describes the bindings for more than one hundred other C libraries. 

While most of the tutorials for using GStreamer are not specifically for the Python language, there is [Python GStreamer Tutorial](https://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.html), however it is from 2015 and examples use python2. Thus it may require minor modifications to the code be run under python3.

See Links section below for references to more documentation.

## Gst.parse_launch()

In the above programs the "all-in-one" plugin **playbin** was used. Thus playbin was a pipeline of *one* plugin. Thus the code...
```
player = Gst.ElementFactory.make('playbin', 'player')
```
could instead have been...
```
player = Gst.parse_launch('playbin')
```
or instead of *player* we could use the more applicable word *pipeline*...
```
pipeline = Gst.parse_launch('playbin')
pipeline.set_property('uri', uri)
pipeline.set_state(Gst.State.PLAYING) 
```

There will be cases where a pipeline of multiple plugins needs to be built to meet the requirements of the python program. In this case the python program will use the **Gst.parse_launch()** function. The arguments for each plugin in the pipeline will be exclamation mark (!) separated. Thus the python code for a program that converts a mp3 file to a wav file will be like this:
```
pipeline = Gst.parse_launch("filesrc location=hello.mp3 ! decodebin ! audioresample ! audioconvert ! audio/x-raw,format=S24LE,rate=48000 ! wavenc ! filesink location=hello.wav")
```
The above is somewhat difficult to read. The code may be written so its easier to comprehend as follows...
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

* mp3_to_wave_loop.py
* mp3_to_wave_poll.py

Note that the *hello.mp3* file will need to be in the same folder as these program to test the default conversion of mp3 to wave file. If the *yakety_yak.mp3* file is in the folder then convert it to the *yakety_yak.wav* file with:
```
$ python3 mp3_to_wave_loop.py yakety_yak.mp3
```

## gst-launch-1.0 and gst-inspect-1.0


## Links
The GStreamer [website](https://gstreamer.freedesktop.org/modules/gstreamer.html) and the [code repository](https://gitlab.freedesktop.org/gstreamer/gstreamer).

A GStreamer Application Development Manual (1.6.0), in C, is avaialble in pdf. Section 20.1 on page 112 describes using the *playbin* plugin.
http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.698.7207&rep=rep1&type=pdf

A Python GStreamer Tutorial 

https://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.html

unfortunately it is in python2. There are some print statements that need to be converted to print() for python3.



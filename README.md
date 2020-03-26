# GStreamer - Demonstration using Python Programs

This is a collection of python programs to demonstate features of the **GStreamer** (Gst) module from the gi repository. The focus is on audio and use of google translates text-to-speech (tts) facility.

Previously my python approach to using google tts included the use of the urllib module to send text to google which was received back in spoken form as a stream of mp3 data. This data was fed into a mp3 player. Refer to the program `google_tts_urllib.py` for an example. 

This collection of programs uses GStreamer and its plugin's as an alternative to the urllib/mp3 player solution. In python3 the GStreamer library is imported as follows:
```
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
```

When a program requests data to be streamed it needs to have a way to continue running until it has received all of the stream. With Gstreamer the ways of doing this are by the simple *polling* method or by the more complex method of *looping* and using *call backs*.

Refer to the programs:

* google_tts_poll.py
* google_tts_loop.py

Modify the code below the line `if __name__ == "__main__:"` for experimenting with your own text to speech messages, playing mp3 files or streaming an internet radio station. Also place the demo mp3 file `yakety_yak.mp3` into the same folder as these programs.

When polling is used then Control-C will not abort what is currently being streamed. It is necessary to wait until completion. In the case of streaming an internet radio staion it never completes. Therefore it is necessary to kill the process.

However with looping, then the loop is commenced to run as follows:
```
try:
    loop.run()
except KeyboardInterrupt:
    loop.quit()
    player.set_state(Gst.State.NULL)
    sys.exit('\nExit via Control-C')
```
Thus a Control-C will interupt the streaming and exit the program. 

Note that the loop method is not contained in the *Gst* library. It is however in the *GObject* or *GLib* libraries. Thus it needs to be imported, instatiated and controlled with either of the following:

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

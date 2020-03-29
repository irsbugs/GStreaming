#!/usr/bin/env python3
#
# espeak.py
#
# This uses the GStreamer (Gst) module with its parse_launch() function.
#
# This uses a loop and needs call_back() function(s) for EOS, etc.
#
# Add a quoted line of text for sys.argv to pass to espeak
# E.g.
# $ python3 espeak.py "I want espeak to say this."
#
#
# Ian Stewart - 2020-03-30

# Importing...
import sys
import os.path
import time
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GObject', '2.0')
from gi.repository import Gst, GObject

MESSAGE = "Hello world this is e speak talking to you."

def speak(message=MESSAGE):
    """ 
    Initialize: Gst, loop and bus.
    Build the pipeline template
    Gst.parse_launch() to establish the pipeline
    Start espeak
    Run loop and accept bus_call() interupts, checking for EOS.
    End by changing state to null.
    """
    start_time = time.time()

    # Init
    Gst.init(None)

    # print(dir(Gst))
    # print(Gst._version)  # 1.0
    # print(Gst.version()) # (major=1, minor=14, micro=5, nano=0)
    # print(Gst.version_string()) # GStreamer 1.14.5

    def on_eos_message(bus, message, loop):
        """EOS - End of Stream"""
        #print("Bus name:", bus.get_name())
        #print(message.type)
        loop.quit()


    def on_error_message(bus, message, loop):
        """Error messages"""
        print("Bus name:", bus.get_name())
        err, debug = message.parse_error()
        print("Error: {}:\n{}".format(err, debug))
        loop.quit()
        sys.exit("Exited due to above error")


    def on_all_message(bus, message, loop):
        """Print all messages - If desired."""
        #print("Bus name:", bus.get_name())
        # Uncomment to view all messages for troubleshooting...
        print(message.type)
        pass

    # Instantiate
    pipeline_template = """
            espeak text="{text}" rate={rate} pitch={pitch} voice={voice} 
                   gap={gap} track={track} 
            ! autoaudiosink
            """.format(
                        text=message,
                        rate=0,         # -100 to + 100
                        pitch=0,        # -100 to + 100
                        voice="en-gb",  # See list below
                        gap=0,          # 0 to max Int. i.e. about 20.
                        track=0,        # Huh? What does track do?
                      )

    pipeline = Gst.parse_launch(pipeline_template)

    # Instantiate and initialize the bus call-back 
    loop = GObject.MainLoop()

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message::error", on_error_message, loop)
    bus.connect("message::eos", on_eos_message, loop)
    bus.connect("message", on_all_message, loop)

    pipeline.set_state(Gst.State.PLAYING)  

    loop.run() 

    # On exiting loop() set state to Null.
    pipeline.set_state(Gst.State.NULL)
    loop.quit()

    print("Time taken: {} milli-secs."
            .format(int((time.time()-start_time) * 1000)))


if __name__=="__main__":

    if len(sys.argv) < 2:
        print("Warning: Please provide a quoted line of text for espeak to say.")
        print("Continuing, but using default message file.")
        speak()

    else:
        input_message = sys.argv[1]
        speak(input_message)

"""
Notes: 

Warning message that occurs with Espeak:

(gst-launch-1.0:937): GStreamer-WARNING **: ../../gstreamer-1.8.1/gst/gstpad.c:5052:store_sticky_event:<amrparse0:src> Sticky event misordering, got 'caps' before 'stream-start

Seems to be this bug: https://bugzilla.gnome.org/show_bug.cgi?id=768166
...which should be fix in December 2017.

$ espeak-ng --voices
Pty Language       Age/Gender VoiceName          File                 Other Languages
 5  af              --/M      Afrikaans          gmw/af               
 5  am              --/M      Amharic            sem/am               
 5  an              --/M      Aragonese          roa/an               
 5  ar              --/M      Arabic             sem/ar               
 5  as              --/M      Assamese           inc/as               
 5  az              --/M      Azerbaijani        trk/az               
 5  bg              --/M      Bulgarian          zls/bg               
 5  bn              --/M      Bengali            inc/bn               
 5  bpy             --/M      Bishnupriya_Manipuri inc/bpy              
 5  bs              --/M      Bosnian            zls/bs               
 5  ca              --/M      Catalan            roa/ca               
 5  cmn             --/M      Chinese_(Mandarin) sit/cmn              (zh-cmn 5)(zh 5)
 5  cs              --/M      Czech              zlw/cs               
 5  cy              --/M      Welsh              cel/cy               
 5  da              --/M      Danish             gmq/da               
 5  de              --/M      German             gmw/de               
 5  el              --/M      Greek              grk/el               
 5  en-029          --/M      English_(Caribbean) gmw/en-029           (en 10)
 2  en-gb           --/M      English_(Great_Britain) gmw/en               (en 2)
 5  en-gb-scotland  --/M      English_(Scotland) gmw/en-GB-scotland   (en 4)
 5  en-gb-x-gbclan  --/M      English_(Lancaster) gmw/en-GB-x-gbclan   (en-gb 3)(en 5)
 5  en-gb-x-gbcwmd  --/M      English_(West_Midlands) gmw/en-GB-x-gbcwmd   (en-gb 9)(en 9)
 5  en-gb-x-rp      --/M      English_(Received_Pronunciation) gmw/en-GB-x-rp       (en-gb 4)(en 5)
 2  en-us           --/M      English_(America)  gmw/en-US            (en 3)
 5  eo              --/M      Esperanto          art/eo               
 5  es              --/M      Spanish_(Spain)    roa/es               
 5  es-419          --/M      Spanish_(Latin_America) roa/es-419           (es-mx 6)(es 6)
 5  et              --/M      Estonian           urj/et               
 5  eu              --/M      Basque             eu                   
 5  fa              --/M      Persian            ira/fa               
 5  fa-Latn         --/M      Persian_(Pinglish) ira/fa-Latn          
 5  fi              --/M      Finnish            urj/fi               
 5  fr-be           --/M      French_(Belgium)   roa/fr-BE            (fr 8)
 5  fr-ch           --/M      French_(Switzerland) roa/fr-CH            (fr 8)
 5  fr-fr           --/M      French_(France)    roa/fr               (fr 5)
 5  ga              --/M      Gaelic_(Irish)     cel/ga               
 5  gd              --/M      Gaelic_(Scottish)  cel/gd               
 5  gn              --/M      Guarani            sai/gn               
 5  grc             --/M      Greek_(Ancient)    grk/grc              
 5  gu              --/M      Gujarati           inc/gu               
 5  hi              --/M      Hindi              inc/hi               
 5  hr              --/M      Croatian           zls/hr               (hbs 5)
 5  hu              --/M      Hungarian          urj/hu               
 5  hy              --/M      Armenian_(East_Armenia) ine/hy               (hy-arevela 5)
 5  hy-arevmda      --/M      Armenian_(West_Armenia) ine/hy-arevmda       (hy 8)
 5  ia              --/M      Interlingua        art/ia               
 5  id              --/M      Indonesian         poz/id               
 5  is              --/M      Icelandic          gmq/is               
 5  it              --/M      Italian            roa/it               
 5  ja              --/M      Japanese           jpx/ja               
 5  jbo             --/M      Lojban             art/jbo              
 5  ka              --/M      Georgian           ccs/ka               
 5  kl              --/M      Greenlandic        esx/kl               
 5  kn              --/M      Kannada            dra/kn               
 5  ko              --/M      Korean             ko                   
 5  kok             --/M      Konkani            inc/kok              
 5  ku              --/M      Kurdish            ira/ku               
 5  ky              --/M      Kyrgyz             trk/ky               
 5  la              --/M      Latin              itc/la               
 5  lfn             --/M      Lingua_Franca_Nova art/lfn              
 5  lt              --/M      Lithuanian         bat/lt               
 5  lv              --/M      Latvian            bat/lv               
 5  mi              --/M      poz/mi             poz/mi               
 5  mk              --/M      Macedonian         zls/mk               
 5  ml              --/M      Malayalam          dra/ml               
 5  mr              --/M      Marathi            inc/mr               
 5  ms              --/M      Malay              poz/ms               
 5  mt              --/M      Maltese            sem/mt               
 5  my              --/M      Burmese            sit/my               
 5  nb              --/M      Norwegian_Bokmål  gmq/nb               (no 5)
 5  nci             --/M      Nahuatl_(Classical) azc/nci              
 5  ne              --/M      Nepali             inc/ne               
 5  nl              --/M      Dutch              gmw/nl               
 5  om              --/M      Oromo              cus/om               
 5  or              --/M      Oriya              inc/or               
 5  pa              --/M      Punjabi            inc/pa               
 5  pap             --/M      Papiamento         roa/pap              
 5  pl              --/M      Polish             zlw/pl               
 5  pt              --/M      Portuguese_(Portugal) roa/pt               (pt-pt 5)
 5  pt-br           --/M      Portuguese_(Brazil) roa/pt-BR            (pt 6)
 5  ro              --/M      Romanian           roa/ro               
 5  ru              --/M      Russian            zle/ru               
 5  sd              --/M      Sindhi             inc/sd               
 5  si              --/M      Sinhala            inc/si               
 5  sk              --/M      Slovak             zlw/sk               
 5  sl              --/M      Slovenian          zls/sl               
 5  sq              --/M      Albanian           ine/sq               
 5  sr              --/M      Serbian            zls/sr               
 5  sv              --/M      Swedish            gmq/sv               
 5  sw              --/M      Swahili            bnt/sw               
 5  ta              --/M      Tamil              dra/ta               
 5  te              --/M      Telugu             dra/te               
 5  tn              --/M      Setswana           bnt/tn               
 5  tr              --/M      Turkish            trk/tr               
 5  tt              --/M      Tatar              trk/tt               
 5  ur              --/M      Urdu               inc/ur               
 5  vi              --/M      Vietnamese_(Northern) aav/vi               
 5  vi-vn-x-central --/M      Vietnamese_(Central) aav/vi-VN-x-central  
 5  vi-vn-x-south   --/M      Vietnamese_(Southern) aav/vi-VN-x-south    
 5  yue             --/M      Chinese_(Cantonese) sit/yue              (zh-yue 5)(zh 8)

print(Gst.VERSION_MAJOR)  #1
print(Gst.VERSION_MINOR)  # 14
print(Gst.VERSION_MICRO)  # 5
print(Gst.VERSION_NANO)  # 0
print(Gst._version)  # 1.0
print(Gst.version()) # (major=1, minor=14, micro=5, nano=0)
print(Gst.version_string()) # GStreamer 1.14.5
$ espeak-ng --version
eSpeak NG text-to-speech: 1.49.2  Data at: /usr/lib/x86_64-linux-gnu/espeak-ng-data
What is GStreamer espeak version? - 0.4.0 according to $ gst-inspect-1.0 espeak

Installation:
$ sudo apt install espeak-ng
$ espeak-ng "hello"

$ sudo apt install gstreamer1.0-espeak

$ gst-launch-1.0 espeak text="hello using alsasink" ! alsasink
$ gst-launch-1.0 espeak text="hello using pulsesink" ! pulsesink
$ gst-launch-1.0 espeak text="hello using autoaudiosink" ! autoaudiosink

$ gst-launch-1.0 espeak text="hello" rate=0 pitch=0 ! autoaudiosink
$ gst-launch-1.0 espeak text="hello" rate=-50 pitch=-100 ! autoaudiosink

# Pipeline "speed" element. Value from 0.0 to 1.0. Where 1 is the normal speed.
$ gst-launch-1.0 espeak text="You can change the speed" ! speed speed=1.0 ! pulsesink

$ gst-inspect-1.0 espeak
Factory Details:
  Rank                     none (0)
  Long-name                eSpeak as a sound source
  Klass                    Source/Audio
  Description              Use eSpeak library as a sound source for GStreamer
  Author                   Aleksey Lim <alsroot@sugarlabs.org>

Plugin Details:
  Name                     espeak
  Description              Uses eSpeak library as a sound source for GStreamer
  Filename                 /usr/lib/x86_64-linux-gnu/gstreamer-1.0/libgstespeak.so
  Version                  0.4.0
  License                  LGPL
  Source module            gst-plugins-espeak
  Binary package           gst-plugins-espeak
  Origin URL               http://sugarlabs.org/go/DevelopmentTeam/gst-plugins-espeak

"""

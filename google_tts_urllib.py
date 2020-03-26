#!/usr/bin/env python3
#
# google_tts_urlib.py
#
# Demonstration of using google translations text-to-speech
# with the urllib library functions.
#
# The returned mp3 stream is played via a choice of mplayer, ffplay or mpv
#
# Ian Stewart - 2020-03-24
#
import subprocess
import urllib.parse
import urllib.request

def text_to_speech(message='Hello World', language='en', mp3="mplayer"):
    """
    Use google translate to do text to speech translation.
    To play the mp3 data use mplayer, ffplay, or mpv.
    message = text to be converted to speech
    language = en is English, fr is French, de is German, etc.
    mp3 =  mp3 player to use: mplayer, ffplay, mpv
    """
    # Build the url string.
    url = 'https://translate.google.com/translate_tts'
    user_agent = 'Mozilla'
    values = {'tl' : language,
              'client' : 'tw-ob',
              'ie' : 'UTF-8',
              'ttsspeed': 1, # Set to 0.3 for slower speech.
              'q' : message }
    data = urllib.parse.urlencode(values)
    headers = { 'User-Agent' : user_agent }

    req = urllib.request.Request(url + "?" + data, None, headers)

    # Select the mp3 player to use... mplayer, ffplay or mpv.
    # Note: Can use "-" instead of "/dev/stdin"
    if mp3 == "mplayer":
        player = subprocess.Popen \
            (
            args = ("mplayer", "-nolirc", "-cache", "1024", "-really-quiet", 
                    "/dev/stdin"),
            stdin = subprocess.PIPE
            )

    if mp3 == "ffplay":
        player = subprocess.Popen \
            (
            args = ("ffplay", "-autoexit", "-loglevel", "quiet", "-nodisp", 
                    "/dev/stdin"),
            stdin = subprocess.PIPE
            )   

    if mp3 == "mpv":
        player = subprocess.Popen \
            (
            args = ("mpv", "--no-video", "--really-quiet", 
                    "/dev/stdin"),
            stdin = subprocess.PIPE
            )  

    # Send the request to google, and send mp3 data to mp3 player.
    try: 
        with urllib.request.urlopen(req) as response:
            mp3_data = response.read()
            player.stdin.write(mp3_data)

    except urllib.error.URLError as e:
        print(e)
        print(e.reason)
        print(e.read())

    player.stdin.close()
    player.wait()
    #print(player.returncode) # 0 is OK.

if __name__ == "__main__":

    text_to_speech()
    text_to_speech("Text to speech defaults to being in English.")
    text_to_speech("C'est la vie. Oh là là", "fr", "ffplay") # French ffplay
    text_to_speech("hello using mpv", "en", "mpv") # English mpv
    text_to_speech("こんにちは。私は話しています。", "ja") # Japanese mplayer



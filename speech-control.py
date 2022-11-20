#!/usr/bin/env python3

import argparse
import queue
import sys
import sounddevice as sd
import json
import subprocess

from vosk import Model, KaldiRecognizer

q = queue.Queue()
words = []
öffnen = False
last_command_opened = ''
last_command_closed = ''
tobreak = False


def confirm(Arr):
    for word in Arr:
        if word == "bestätige" or word == "bestätigen" or word == "bestätigt":
            return True
    return False

def computertasks (Arr):
    for word in Arr:
        if word == "abmelden":
            if confirm(Arr):
                subprocess.Popen(["pkill", "-u", "konstantinm"])
        if word == "herunterfahren":
            if confirm(Arr):
                subprocess.Popen(["shutdown", "-h","0"])

def close(Arr):
    global last_command_closed
    for word in Arr:
        if word == "github" and last_command_closed != word:
            subprocess.Popen(["pkill", "github-desktop"])
            last_command_closed = word
        if word == "blender" and last_command_closed != word:
            subprocess.Popen(["pkill", "blender"])
            last_command_closed = word
        if word == "discord" or word == "disco" and last_command_closed != word:
            subprocess.Popen(["pkill", "Discord"])
            last_command_closed = word
        if word == "firefox" and last_command_closed != word:
            subprocess.Popen(["pkill", "firefox"])
            last_command_closed = word
        if word == "signal" and last_command_closed!= word:
            subprocess.Popen(["pkill", "signal-desktop"])
            last_command_closed = word
        if word == "code" and last_command_closed!= word:
            subprocess.Popen(["pkill", "codium"])
            last_command_closed = word
        if word == "geogebra" and last_command_closed!= word:
            subprocess.Popen(["pkill", "geogebra"])
            subprocess.Popen(["pkill", "electron"])
            last_command_closed = word
        if word == "gimp" and last_command_closed!= word:
            subprocess.Popen(["pkill", "gimp"])
            last_command_closed = word
        if word == "anki" and last_command_closed!= word:
            subprocess.Popen(["pkill", "anki"])
            last_command_closed = word
        if word == "whatsapp" or word == "whats-app" and last_command_closed!= word:
            subprocess.Popen(["pkill", "whatsapp"])
            last_command_closed = word
        if word == "cura" or word == "hurra" and last_command_closed!= word:
            subprocess.Popen(["pkill", "Ultimaker-Cura"])# frequently mistake (hurra)
            last_command_closed = word
        
        
        

def open(Arr):
    global last_command_opened
    for word in Arr:
        if word == "firefox" and last_command_opened != word:
            subprocess.Popen(["/usr/bin/firefox", "startpage.com"])
            last_command_opened = word
        if word == "blender" and last_command_opened != word:
            subprocess.Popen(["/usr/bin/blender"])
            last_command_opened = word
        if word == "kommandozeile" and last_command_opened!= word:
            subprocess.Popen(["/usr/bin/gnome-terminal"])
            last_command_opened = word
        if word == "schach" and last_command_opened!= word:
            subprocess.Popen(["/usr/bin/firefox", "lichess.org"])
            last_command_opened = word
        if word == "youtube" and last_command_opened!= word:
            subprocess.Popen(["/usr/bin/firefox", "youtube.com"])
            last_command_opened = word
        if word == "signal" and last_command_opened!= word:
            subprocess.Popen(["/usr/bin/signal-desktop"])
            last_command_opened = word
        if word == "discord" and last_command_opened!= word:
            subprocess.Popen(["/usr/bin/discord"])
            last_command_opened = word
        if word == "code" and last_command_opened!= word:
            subprocess.Popen(["flatpak", "run", "com.vscodium.codium"])
            last_command_opened = word
        if word == "geogebra" and last_command_opened!= word:
            subprocess.Popen(["/usr/bin/geogebra"])
            last_command_opened = word
        if word == "gimp" and last_command_opened!= word:
            subprocess.Popen(["/usr/bin/gimp"])
            last_command_opened = word
        if word == "anki" and last_command_opened!= word:
            subprocess.Popen(["flatpak", "run", "net.ankiweb.Anki"])
            last_command_opened = word
        if word == "github" and last_command_opened!= word:
            subprocess.Popen(["flatpak", "run", "io.github.shiftey.Desktop"])
            last_command_opened = word
        if word == "whatsapp" or word == "whats-app" and last_command_opened!= word:
            subprocess.Popen(["flatpak", "run", "io.github.mimbrero.WhatsAppDesktop"])
            last_command_opened = word
        if word == "cura" or word == "hurra" and last_command_opened!= word: # frequently mistake (hurra)
            subprocess.Popen(["flatpak", "run", "com.ultimaker.cura"])
            last_command_opened = word


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
args = parser.parse_args(remaining)

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])

    model = Model(lang="de")

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
            dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                vc = json.loads(rec.Result())
                words = vc['text'].split()
                print(words)
                for word in words:
                    if word == "öffne" or word == "öffner" or word == "öffnet": #frequently mistake (öffner & öffnet)
                       open(words)
                    if word == "schließe" or word == "schließen" or word == "schließt": #frequently mistake (schließen & schließt)
                       close(words)
                    if word == "computer":
                       computertasks(words)
                    if word == "sprachsteuerung":
                        for word2 in words:
                            if word2 == "beenden" or word2 == "beende":
                                if confirm(words):
                                    tobreak = True

                last_command_opened = ""
                last_command_closed = ""
            else:
                vc = json.loads(rec.PartialResult())
                words = vc['partial'].split()
                print(words)

                for word in words:
                    if word == "öffne" or word == "öffner" or word == "öffnet": #frequently mistake (öffner & öffnet)
                       open(words)
                    if word == "schließe" or word == "schließen" or word == "schließt": #frequently mistake (schließen & schließt)
                       close(words)
                    if word == "computer":
                       computertasks(words)
                    if word == "sprachsteuerung":
                        for word2 in words:
                            if word2 == "beenden" or word2 == "beende":
                                if confirm(words):
                                    tobreak = True


            
                
            if tobreak:
                break    
                
            if dump_fn is not None:
                dump_fn.write(data)

except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))


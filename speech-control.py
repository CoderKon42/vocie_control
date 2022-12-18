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
last_command = ''
tobreak = False
isactive = True
numbers_one_to_twenty = ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf", "dreizehn", "vierzehn", "fünfzehn","sechzehn","siebzehn", "achtzehn","neunzehn","zwanzig"]
apps = [
{"openname": "blender", "isflatpak": False, "parameter": None}, 
{"openname": "gnome-terminal", "isflatpak": False, "parameter": None},
{"openname": "discord", "isflatpak": False, "parameter": None},
{"openname": "firefox", "isflatpak": False, "parameter": "startpage.com"},
{"openname": "firefox", "isflatpak": False, "parameter": "lichess.org"},
{"openname": "firefox", "isflatpak": False, "parameter": "youtube.com"},
{"openname": "signal-desktop", "isflatpak": False, "parameter": None},
{"openname": "gimp", "isflatpak": False, "parameter": None},
{"openname": "geogebra", "isflatpak": False, "parameter": None, "tokill": "geogebra && pkill electron"},
{"openname": "com.vscodium.codium", "isflatpak": True, "parameter": None, "tokill":"codium"},
{"openname": "net.ankiweb.Anki", "isflatpak": True, "parameter": None, "tokill": "anki"},
{"openname": "io.github.shiftey.Desktop", "isflatpak": True, "parameter": None, "tokill": "github-desktop"},
{"openname": "io.github.mimbrero.WhatsAppDesktop", "isflatpak": True, "parameter": None, "tokill": "whatsapp"},
{"openname": "com.ultimaker.cura", "isflatpak": True, "parameter": None , "tokill": "Ultimaker-Cura"}
]
identifier = ["blender", 0, "terminal", 1, "kommandozeile", 1, "discord", 2, "disco", 2, "firefox", 3, "schach", 4, "youtube", 5, "signal", 6, "gimp", 7, "geogebra", 8, "code", 9, "anki", 10, "github", 11, "whatsapp", 12, "whats-app", 12, "cura", 13, "hurra", 13]
# name of the app and/or nickname followed by the index of where the app is in the apps list

def whatToDo(Arr):
    global isactive
    global tobreak
    for word in Arr:  
        if isactive:
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
                if word2 == "deaktivieren" or word2 =="deaktiviere":
                    isactive = False
                if word2 == "aktivieren" or word2 =="aktiviere":
                    isactive = True

def confirm(Arr):
    for word in Arr:
        if word == "bestätige" or word == "bestätigen" or word == "bestätigt":
            return True
    return False

def getPercent(Arr):
    for word in Arr:
        if word in numbers_one_to_twenty:
            return numbers_one_to_twenty.index(word)
    return None


def computertasks (Arr):
    global last_command
    for word in Arr:
        if word == "abmelden":
            if confirm(Arr):
                subprocess.Popen(["pkill", "-u", "konstantinm"])
        if word == "herunterfahren":
            if confirm(Arr):
                subprocess.Popen(["shutdown", "-h","0"])
        if word == "neustarten":
            if confirm(Arr):
                subprocess.Popen(["reboot"])
        if word == "leiser" and last_command!= word:
            percent = getPercent(Arr)
            if percent is not None:
                subprocess.Popen(["amixer", "-D", "pulse", "sset", "Master", f"{percent}%-"])
                last_command = word
        if word == "lauter" or word == "laut" or word == "lauta" and last_command != word:
            percent = getPercent(Arr)
            if percent is not None:
                subprocess.Popen(["amixer", "-D", "pulse", "sset", "Master", f"{percent}%+"])
                last_command = word


def open(Arr):
    global last_command
    for word in Arr:
        if word in identifier and word != last_command:
            app = apps[identifier[identifier.index(word)+1]]
            if app['isflatpak']:
                if app["parameter"] == None:
                    subprocess.Popen(["flatpak", "run", app['openname']])
                else:
                    subprocess.Popen(["flatpak", "run", ['openname'], app['parameter']])
            else:
                if app["parameter"] == None:
                    subprocess.Popen([f"/usr/bin/{app['openname']}"])
                else:
                    subprocess.Popen([f"/usr/bin/{app['openname']}", app['parameter']])
            last_command = word

def close(Arr):
    for word in Arr:
        if word in identifier:
            app = apps[identifier[identifier.index(word)+1]]
            if app['isflatpak']:
                subprocess.Popen(["pkill", app['tokill']])
            else:
                subprocess.Popen(["pkill", app['openname']])

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
                whatToDo(words)  
                last_command_opened = ""
                last_command_closed = ""
            else:
                vc = json.loads(rec.PartialResult())
                words = vc['partial'].split()
                whatToDo(words)  
            print(words)      

            if tobreak:
                break    
                
            if dump_fn is not None:
                dump_fn.write(data)

except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))

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
{"openname": "blender", "isflatpak": False, "parameter": None, "elsekill": None}, 
{"openname": "gnome-terminal", "isflatpak": False, "parameter": None, "elsekill": None},
{"openname": "discord", "isflatpak": False, "parameter": None ,"elsekill": None},
{"openname": "firefox", "isflatpak": False, "parameter": "startpage.com", "elsekill": None},
{"openname": "firefox", "isflatpak": False, "parameter": "lichess.org", "elsekill": None},
{"openname": "firefox", "isflatpak": False, "parameter": "youtube.com", "elsekill": None},
{"openname": "signal-desktop", "isflatpak": False, "parameter": None, "elsekill": None},
{"openname": "gimp", "isflatpak": False, "parameter": None, "elsekill": None},
{"openname": "geogebra", "isflatpak": False, "parameter": None, "elsekill": "electron"},
{"openname": "com.vscodium.codium", "isflatpak": True, "parameter": None, "tokill":"codium", "elsekill": None},
{"openname": "net.ankiweb.Anki", "isflatpak": True, "parameter": None, "tokill": "anki", "elsekill": None},
{"openname": "io.github.shiftey.Desktop", "isflatpak": True, "parameter": None, "tokill": "github-desktop", "elsekill": None},
{"openname": "io.github.mimbrero.WhatsAppDesktop", "isflatpak": True, "parameter": None, "tokill": "whatsapp", "elsekill": None},
{"openname": "com.ultimaker.cura", "isflatpak": True, "parameter": None , "tokill": "Ultimaker-Cura", "elsekill": None}
]
identifier = ["blender", 0, "terminal", 1, "kommandozeile", 1, "discord", 2, "disco", 2, "firefox", 3, "schach", 4, "youtube", 5, "signal", 6, "gimp", 7, "geogebra", 8, "code", 9, "anki", 10,"anke", 10, "anti", 10, "github", 11, "whatsapp", 12, "whats-app", 12, "cura", 13, "hurra", 13]
# name of the app and/or nickname followed by the index of where the app is in the apps list

def whatToDo(Arr, issentencecomplete = False):
    global isactive
    global tobreak 
    if isactive:
        if "öffne" in Arr or "öffner" in Arr or "öffnet" in Arr: #frequently mistake (öffner & öffnet)
            open(Arr)
        if "schließe" in Arr or "schließen" in Arr or "schließt" in Arr: #frequently mistake (schließen & schließt)
            close(Arr)
        if "computer" in Arr:
            computertasks(Arr)
        if ("google" in Arr or "googles" in Arr) and issentencecomplete == True:
            if "google" in Arr:
                key = "google"
            if "googles" in Arr:
                key = "googles"
            google(Arr, key)
    if "sprachsteuerung" in Arr:
        if "beenden" in Arr or "beende" in Arr:
            if confirm(Arr):
                tobreak = True
        if "deaktivieren" in Arr or "deaktiviere" in Arr:
            isactive = False
        if "aktivieren" in Arr or "aktiviere" in Arr:
            isactive = True

def confirm(Arr):
    if "bestätige" in Arr or "bestätigen" in Arr or "bestätigt" in Arr:
        return True
    return False

def getPercent(Arr):
    for word in Arr:
        if word in numbers_one_to_twenty:
            return numbers_one_to_twenty.index(word)
    return None

def computertasks (Arr):
    global last_command
    if "abmelden" in Arr:
        if confirm(Arr):
            subprocess.Popen(["pkill", "-u", "konstantinm"])
    if "herunterfahren" in Arr:
        if confirm(Arr):
            subprocess.Popen(["shutdown", "-h","0"])
    if "neustarten" in Arr:
        if confirm(Arr):
            subprocess.Popen(["reboot"])
    if "leiser" in Arr and last_command!= "leiser":
        percent = getPercent(Arr)
        if percent is not None:
            subprocess.Popen(["amixer", "-D", "pulse", "sset", "Master", f"{percent}%-"])
            last_command = "leiser"
    if ("lauter" in Arr or "laut" in Arr or "lauta" in Arr) and last_command != "lauter":
        percent = getPercent(Arr)
        if percent is not None:
            subprocess.Popen(["amixer", "-D", "pulse", "sset", "Master", f"{percent}%+"])
            last_command = "lauter"


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
                if app["elsekill"] == None:
                    subprocess.Popen(["pkill", app['tokill']])
                else:
                    subprocess.Popen(["pkill", app['tokill']])
                    subprocess.Popen(["pkill", app['elsekill']])
            else:
                if app["elsekill"] == None:
                    subprocess.Popen(["pkill", app['openname']])
                else:
                    subprocess.Popen(["pkill", app['openname']])
                    subprocess.Popen(["pkill", app['elsekill']])

def google(Arr, keyword):
        google_index = Arr.index(keyword)
        aftergoogle = Arr[google_index + 1:]
        param = '+'.join(aftergoogle)
        subprocess.Popen(["/usr/bin/firefox", f"https://www.ecosia.org/search?q={param}&addon=firefox&addonversion=4.1.0&method=topbar"])


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
                whatToDo(words, True)
                last_command = ""
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

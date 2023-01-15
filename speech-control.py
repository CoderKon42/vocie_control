#!/usr/bin/env python3

import argparse
import queue
import sys
import sounddevice as sd
import json
import subprocess
import os
import apps_local

from vosk import Model, KaldiRecognizer

q = queue.Queue()
words = []
last_commands = []
tobreak = False
isactive = True
numbers_one_to_twenty = ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf", "dreizehn", "vierzehn", "fünfzehn","sechzehn","siebzehn", "achtzehn","neunzehn","zwanzig"]
apps_local.load_identifier()
identifier = apps_local.identifier
apps_local.load_apps()
apps = apps_local.apps

def whatToDo(Arr, issentencecomplete = False):
    global isactive
    global tobreak
    global last_commands
    if isactive:
        if "öffne" in Arr or "öffner" in Arr or "öffnet" in Arr:
            open_app(Arr)
        if "schließe" in Arr or "schließen" in Arr or "schließt" in Arr:
            close(Arr)
        if "computer" in Arr:
            computertasks(Arr)
        if ("google" in Arr or "googles" in Arr) and issentencecomplete:
            if "google" in Arr:
                key = "google"
            if "googles" in Arr:
                key = "googles"
            google(Arr, key)
    if "sprachsteuerung" in Arr:
        if "beenden" in Arr or "beende" in Arr:
            if confirm(Arr):
                tobreak = True
                notify("Sprachsteuerung beendet")
        if "deaktivieren" in Arr or "deaktiviere" in Arr:
            isactive = False
            if  not "deaktiviert" in last_commands:
                notify("Sprachsteuerung deaktiviert")
                last_commands.append("deaktiviert")
        if "aktivieren" in Arr or "aktiviere" in Arr:
            isactive = True
            if not "aktiviert" in last_commands:
                notify("Sprachsteuerung aktiviert")
                last_commands.append("aktiviert")

def confirm(Arr):
    if "bestätige" in Arr or "bestätigen" in Arr or "bestätigt" in Arr:
        return True
    return False

def notify(text):
    os.system(f'zenity --notification --text="{text}"')

def getPercent(Arr):
    for word in Arr:
        if word in numbers_one_to_twenty:
            return numbers_one_to_twenty.index(word)
    return None

def computertasks (Arr):
    global last_commands
    if "abmelden" in Arr:
        if confirm(Arr):
            with open('.cache/vosk/username', 'r') as usr:
                username = usr.read().split('\n')[0]
                subprocess.Popen(["pkill", "-u", username])
    if "herunterfahren" in Arr:
        if confirm(Arr):
            subprocess.Popen(["shutdown", "-h","0"])
    if "neustarten" in Arr or "neu" in Arr:
        if "neu" in Arr:
            try:
                if Arr[Arr.index("neu") + 1] != "starten":
                    return
            except IndexError:
                return
        if confirm(Arr):
            subprocess.Popen(["reboot"])
    if "leiser" in Arr and not "leiser" in last_commands:
        percent = getPercent(Arr)
        if percent is not None:
            subprocess.Popen(["amixer", "-D", "pulse", "sset", "Master", f"{percent}%-"])
            last_commands.append("leiser")
    if ("lauter" in Arr or "laut" in Arr or "lauta" in Arr) and not "lauter" in last_commands:
        percent = getPercent(Arr)
        if percent is not None:
            subprocess.Popen(["amixer", "-D", "pulse", "sset", "Master", f"{percent}%+"])
            last_commands.append("lauter")


def open_app(Arr):
    global last_commands
    for word in Arr:
        if word in identifier and  not word in last_commands:
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
            last_commands.append(word)


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
        notify("Sprachsteuerung bereit")

        rec = KaldiRecognizer(model, args.samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                vc = json.loads(rec.Result())
                words = vc['text'].split()
                whatToDo(words, True)
                last_commands = []
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

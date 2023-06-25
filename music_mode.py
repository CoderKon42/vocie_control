import subprocess

def getPercent(Arr):
    numbers_one_to_twenty = ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf", "dreizehn", "vierzehn", "fünfzehn","sechzehn","siebzehn", "achtzehn","neunzehn","zwanzig"]
    for word in Arr:
        if word in numbers_one_to_twenty:
            return numbers_one_to_twenty.index(word)
    return None

def music(Arr, last_commands):
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
    if ("pause" in Arr or "pausieren" in Arr or "weiter" in Arr or "abspielen" in Arr) and not "pause" in last_commands:
        subprocess.Popen(["playerctl", "-i", "kdeconnect","play-pause", "smplayer"])
        last_commands.append("pause")
    if ("überspringen" in Arr or "nächster" in Arr or "nächstes" in Arr)and not "next" in last_commands:
        subprocess.Popen(["playerctl", "next"])
        last_commands.append("next")
    if ("vorheriges" in Arr or "vorheriger" in Arr or "letztes" in Arr or "letzter" in Arr or "zurück" in Arr) and not "previous" in last_commands:
        subprocess.Popen(["playerctl", "previous"]) #resets the current playing song
        subprocess.Popen(["playerctl", "previous"]) # starts the previous song
        last_commands.append("previous")
    
    return last_commands
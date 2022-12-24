import apps_local

isflatpak = None
name = ""
tokill = ""
elsekill = ""
parameter = ""
identifier = []

def flatpak():
    global isflatpak

    isflatpak_str = input("Ist die Anwendung als flatpak istalliert worden (J/N)")
    if isflatpak_str == 'J':
        isflatpak = True
    elif isflatpak_str == 'N':
        isflatpak = False
    else:
        print('Bitte geben sie ein N oder J ein')
        flatpak()

def openname():
    global name
    if isflatpak:
        name = input("welcher befehl startet die Anwendung (flatpak run ...)")
    else:
        name = input("wie ist der Name der Anwendung im Verzeichnis /usr/bin/")

def kill():
    global tokill
    tokill = input("welcher Befehl beendet die Anwendung (pkill ...), werden zwei Befehle gebraucht nur einen angeben")

def ekill():
    global elsekill
    if isflatpak:
        elsekill = input("muss noch ein anderer pkill ausgeführt werden (Befehl/N)")
    else:
        elsekill = input("muss außer pkill name (aus /usr/bin/) noch ein zweiter pkill ausgeführt werden um die Anwendung zu beenden (Befehl/N)")
    if elsekill == "N":
        elsekill = None

def param():
    global parameter
    parameter = input("Braucht die Anwendung einen Parameter (Parameter/N) (z.B firefox startpage.com)")
    if parameter == "N":
        parameter = None

def ids():
    global identifier
    id = input("Gebe ein Wort an, auf welches die Anwendung reagieren soll (Wort/N)")
    if id == "N":
        return
    identifier.append(id)
    ids()

ids()
flatpak()
openname()
param()
if isflatpak:
    kill()
ekill()

if isflatpak:
    apps_local.insert_app(identifier, name, isflatpak, tokill, parameter, elsekill)
else:
    apps_local.insert_app(identifier, name, isflatpak, None, parameter, elsekill)

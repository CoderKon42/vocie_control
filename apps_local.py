apps = []
identifier = []


def load_apps():
    index_read = 0
    with open('.cache/vosk/apps_save', 'r') as f:
        values = f.read().split('\n')
        json_element = None

        while index_read < len(values)-2:

            if values[index_read + 2]== "False":
                isflatpak = False
            else:
                isflatpak = True

            if values[index_read +3]== "None":
                parameter = None
            else:
                parameter = values[index_read +3]
        

            try:
                if values[index_read + 5] == "":

                    if values[index_read +4]== "None":
                        elsekill = None
                    else:
                        elsekill = values[index_read +4]



                    json_element = {"openname": values[index_read +1], "isflatpak": isflatpak, "parameter": parameter, "elsekill": values[index_read +4] }
                    index_read += 5
                else:

                    if values[index_read +5]== "None":
                        elsekill = None
                    else:
                        elsekill = values[index_read +5]



                    json_element = {"openname": values[index_read +1], "isflatpak": isflatpak, "parameter": parameter,"tokill": values[index_read +4],  "elsekill": values[index_read + 5] }
                    index_read += 6
            except IndexError:
                pass
            apps.append(json_element)


def load_identifier():
    with open('.cache/vosk/identifiers_save', 'r') as f:
        values = f.read().split('\n')
        for i in range(len(values)):
            if i % 2 == 0:
                identifier.append(values[i])
            else:
                identifier.append(int(values[i]))


def insert_app(identifiers, openname, isflatpak, tokill = None, parameter = None, elsekill = None):
    # identifier as list
    load_apps()
    load_identifier()

    if identifiers == []:
        print("No Id found")
        return

    for id in identifiers:
        if id in identifier:
            print ("identifier already exists")
            return

    for app in apps:
        if openname in app['openname']:
            if app['parameter'] == parameter:
                print("app already exists")
                return

    if not isflatpak:
        apps.append({"openname": openname, "isflatpak": isflatpak, "parameter": parameter, "elsekill": elsekill})     
    else:
        if tokill == None:
            print("could not insert, tokill is missing")
            return
        apps.append({"openname": openname, "isflatpak": isflatpak, "parameter": parameter, "tokill": tokill, "elsekill": elsekill})

    for identifier_app in identifiers:
        identifier.append(identifier_app)
        identifier.append(len(apps)+1)

    insert_app_save(identifiers, openname, isflatpak, tokill, parameter, elsekill , len(apps)-1)
    

def insert_app_save(identifiers, openname, isflatpak,tokill, parameter, elsekill, index):
    first = True
    with open('.cache/vosk/apps_save', 'a') as f:
        if isflatpak:
            f.write(f'\n{openname}\n{isflatpak}\n{parameter}\n{tokill}\n{elsekill}\n')
        else:
            f.write(f'\n{openname}\n{isflatpak}\n{parameter}\n{elsekill}\n')
    with open('.cache/vosk/identifiers_save', 'a') as f:
        for identifier_app in identifiers:
            f.write(f'{identifier_app}')
            f.write(f'\n{index}\n')
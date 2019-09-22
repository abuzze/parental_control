'''
pc_control: Main module

Copyright 2019, abuzze
Licensed under MIT.
'''
from win10toast import ToastNotifier
import time
import requests
import datetime
import time
import glob, os, json

class Timer():

    def __init__(self):
        self.start_time = time.monotonic()

    def seconds_elapsed(self):
        return time.monotonic() - self.start_time
    def minutes_elapsed(self):
        return (time.monotonic() - self.start_time)/60
    def hours_elapsed(self):
        return (time.monotonic() - self.start_time)/60/60

def weather_toast(location="N/A", temperature = "N/A", description = "N/A"):
    toaster = ToastNotifier()
    toaster.show_toast("Wetterbericht",
                   "Es sind derzeit "+ temperature+" °C in "+location +"\r\n" + description,
                   icon_path='sun-2-32.ico',
                   duration=5,
                   threaded=True)
    while toaster.notification_active(): time.sleep(0.1)

def notification(heading="", text="", duration=5):
    toaster = ToastNotifier()
    toaster.show_toast(heading,text, icon_path='joystick-32.ico',duration=5,threaded=True)
    while toaster.notification_active(): time.sleep(0.1)

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current local time
    check_time = check_time or datetime.datetime.now().time()

    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def create_settings():
    if os.path.isfile('./settings.json'):
        return
    settings = {
        "_comment": "Mo-Sun",
        "playtime": [60,60,60,60,90,140,140],
        "time_restrictions":{"0":["6:45-7:20","13:00-17:30"],
                     "1":["6:45-7:20","13:00-17:30"],
                     "2":["6:45-7:20","13:00-17:30"],
                     "3":["6:45-7:20","13:00-17:30"],
                     "4":["6:45-7:20","13:00-17:30"],
                     "5":["6:45-9:00","14:00-18:00"],
                     "6":["6:45-9:00","14:00-18:00"]}                   
    }
    with open('settings.json', 'w') as outfile:
        json.dump(settings, outfile)    

def create_playtime_log():

    if os.path.isfile('./playtime_log.json'):
        return
    playtime_log = {"playtime_used": []}
    with open('playtime_log.json', 'w') as outfile:
        json.dump(playtime_log, outfile)

def update_playtime(playtime):
    #load todays already used playtime
    with open("playtime_log.json") as data_file:
        playtime_log = json.load(data_file)
    
    new_playtime = True

    for k in playtime_log['playtime_used']:
       
        if k['date'] == datetime.datetime.today().strftime('%d.%m.%Y'):
            k['playtime_used'] = playtime
            new_playtime = False

    if new_playtime:
        new_playtime_entry = {"date": datetime.datetime.today().strftime('%d.%m.%Y'), "playtime_used": playtime}
        playtime_log['playtime_used'].append(new_playtime_entry)

    with open('playtime_log.json', 'w') as outfile:
        json.dump(playtime_log, outfile)

def get_playtime_used():
    with open("playtime_log.json") as data_file:
        playtime_log = json.load(data_file)
    if len(playtime_log['playtime_used']) > 0:
        for k in playtime_log['playtime_used']:
            if k['date'] == datetime.datetime.today().strftime('%d.%m.%Y'):
                return k['playtime_used']
    else:
        return 0

def get_forecast():
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q=Ammersbek&APPID=479ec853357bd9e2fc2d8afd2c385fdd&units=metric')

    forecast = {}
    forecast['location'] = str(r.json()['name'])
    forecast['temperature'] = r.json()['main']['temp']
    forecast['weather'] = str(r.json()['weather'])
    forecast['description'] = str(r.json()['weather'][0]['description'])
    return forecast

def shutdown(message=""):
    notification("Der Computer geht jetzt aus",message)
    os.system('shutdown -s')

def main():
    create_settings()
    create_playtime_log()

    with open("./settings.json") as data_file:
        data = json.load(data_file)
    
    time_restrictions = []
    playtime_minutes_today = data['playtime'][datetime.datetime.today().weekday()]
    time_restrictions_enabled = True

    for k in data['time_restrictions']:
        if k == str(datetime.datetime.today().weekday()):
            time_restrictions = data['time_restrictions'][k]

    for t in time_restrictions:
        hours = t.split("-")
        starttime = hours[0].split(":")
        endtime = hours[1].split(":")

        #within the playtime
        if (is_time_between(datetime.time(int(starttime[0]),int(starttime[1])),datetime.time(int(endtime[0]),int(endtime[1])))):
            time_restrictions_enabled = False
    
    forecast = get_forecast()

    if time_restrictions_enabled:
        shutdown("Keine Spielzeit","Es ist es "+str(datetime.datetime.now().time()))

    elif forecast['description'].find('rain') and  forecast['temperature'] > 20:
        weather_toast(forecast['location'], str(forecast['temperature']), forecast['description'])
        shutdown("Das Wetter ist zu gut zum Computer spielen.")
    else:
        #no restrictions and playtime left
        notification("Viel Spass beim spielen", "Du hast noch " +str(playtime_minutes_today- get_playtime_used())+ " von " + str(playtime_minutes_today) +" Minuten Spielzeit")
        mytimer = Timer()    
    
        while get_playtime_used() < playtime_minutes_today:
            update_playtime(get_playtime_used()+1)
            print('Playtime used: {} at: {}'.format(get_playtime_used(),datetime.datetime.now().time()))
            time.sleep(60)

            if playtime_minutes_today- get_playtime_used() == 15:
                notification("Die Zeit ist bald um", "Du hast noch 15 Minuten.")
                print("15 min warning")
            if playtime_minutes_today- get_playtime_used() == 5:
                notification("Die Zeit ist bald um", "Du hast noch 5 Minuten.")
                print("5 min warning")
            if playtime_minutes_today- get_playtime_used() < 1:
                shutdown("Die Zeit ist um")
main()

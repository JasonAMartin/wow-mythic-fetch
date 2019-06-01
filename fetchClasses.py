# Get classes in the game and put into the DB

import sqlite3 as lite
import sys
import requests
import datetime


def start_fetch():
    url = "https://us.api.battle.net/wow/data/character/classes?locale=en_US&apikey=gtzfar8g9nkgd6jzhaug9nn7hfk32sgq"
    r = requests.get(url=url)
    if r.status_code is 200:
        add_classes(r.json())


def add_classes(data):
    classes = data['classes']
    for game_class in classes:
        game_id = game_class["id"]
        game_mask = game_class["mask"]
        game_power_type = game_class["powerType"]
        game_name = game_class["name"]

        cur = con.cursor()
        cur.execute(
            '''SELECT * FROM Classes where class_id=? and class_name=?''', (game_id, game_name))
        exists = cur.fetchone()
        if exists is None:
            try:
                cur.execute('''INSERT INTO Classes(class_id, class_mask, class_power_type, class_name) VALUES(?,?,?,?)''',
                            (game_id, game_mask, game_power_type, game_name))
            except sqlite3.Error as e:
                print("Couldn't add game class. Error: {0}".format(e))
            finally:
                print('Adding class: ', game_name)
                con.commit()


# MAIN
try:
    con = lite.connect('./db/WOW.db')
except:
    print('General error')
    sys.exit(1)
finally:
    if con:
        print('connected...')

# REPORTS
start_fetch()

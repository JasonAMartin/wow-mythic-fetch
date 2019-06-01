# Fetch player data and put it in the DB. Mythic table players_checked is updated to 1 when mythic is scanned.
import sqlite3 as lite
import sys
import requests


def get_mythic_groups():
    groups = []
    cur = con.cursor()
    cur.execute("SELECT players_checked, tank_name, tank_realm, healer_name, healer_realm, dps1_name, dps1_realm, dps2_name, dps2_realm, dps3_name, dps3_realm, zone, tank_id, healer_id, dps1_id, dps2_id, dps3_id, id FROM Mythics where players_checked=0")
    rows = cur.fetchall()
    print("grabbed player data")
    if rows is not None:
        for row in rows:
            print("found row")
            tank_name = row[1]
            tank_realm = row[2]
            healer_name = row[3]
            healer_realm = row[4]
            dps1_name = row[5]
            dps1_realm = row[6]
            dps2_name = row[7]
            dps2_realm = row[8]
            dps3_name = row[9]
            dps3_realm = row[10]
            zone = row[11]
            tank_id = row[12]
            healer_id = row[13]
            dps1_id = row[14]
            dps2_id = row[15]
            dps3_id = row[16]
            update_player(tank_id, tank_name, tank_realm, zone)
            update_player(healer_id, healer_name, healer_realm, zone)
            update_player(dps1_id, dps1_name, dps1_realm, zone)
            update_player(dps2_id, dps2_name, dps2_realm, zone)
            update_player(dps3_id, dps3_name, dps3_realm, zone)
            print("prepping Mythics update")
            try:
                cur.execute("Update Mythics set players_checked=1 where id={0}".format(row[17]))
            except sqlite3.Error as e:
                print("Couldn't update mythics. Error: {0}".format(e))
            finally:
                print("updating Mythics")
                con.commit()
    return groups


def update_player(id, name, realm, zone):
    #    url = "https://{0}.api.battle.net/wow/character/{1}/{2}?fields=items&locale=en_US&apikey=gtzfar8g9nkgd6jzhaug9nn7hfk32sgq".format(zone, realm, name)
    url = "https://{0}.api.battle.net/wow/character/{1}/{2}?locale=en_US&apikey=gtzfar8g9nkgd6jzhaug9nn7hfk32sgq".format(zone, realm, name)
    cur = con.cursor()
    cur.execute(
        '''SELECT name, server FROM Players where name=? and server=?''', (name, realm))
    exists = cur.fetchone()
    if exists is None:
        # add player
        # get data
        r = requests.get(url=url)
        # TODO: want to do something with 404s?
        if r.status_code is 200:
            build_player_record(r.json(), zone, id)


def build_player_record(data, zone, id):
    name = data['name']
    server = data['realm']
    player_class = data['class']
    race = data['race']
    gender = data['gender']
    level = data['level']
    achievement_points = data['achievementPoints']
    faction = data['faction']
    total_honorable_kills = data['totalHonorableKills']
    thumbnail = data['thumbnail']

    # check if player record exists, add if not
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM Players where wow_id={0}".format(id))
    exists = cur.fetchone()
    if exists is None:
        try:
            cur.execute('''INSERT INTO Players(name, server, class, race, gender, level, achievementPoints, faction, totalHonorableKills, thumbnail, wow_id, zone) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                        (name, server, player_class, race, gender, level, achievement_points, faction, total_honorable_kills, thumbnail, id, zone))
        except sqlite3.Error as e:
            print("Couldn't add player. Error: {0}".format(e))
        finally:
            print('Adding new player: {0}.', name)
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
get_mythic_groups()
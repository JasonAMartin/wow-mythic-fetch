# passed in a player name, server, realm
# check if player has item set pulled for today
# if not, pull data and update. If so, pass.
import sqlite3 as lite
import sys
import requests
import datetime
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-fetch", "--fetch", help="fetch type is new by default. Pass in 'all' for everything.")
args = parser.parse_args()
fetch_type = args.fetch


def get_today():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")


def start_fetch(fetch="new"):
    # get all Players
    # iterate and run update_items
    print("starting item fetch ...")
    cur = con.cursor()
    if fetch is not "new":
        cur.execute("SELECT name, server, zone, wow_id, id, last_checked FROM Players where last_checked <> '{0}'".format(get_today()))
    else:
        cur.execute("SELECT name, server, zone, wow_id, id, last_checked FROM Players where last_checked is NULL")
    rows = cur.fetchall()
    for row in rows:
        update_items(row[3], row[0], row[1], row[2], row[4])


def update_items(id, name, realm, zone, player_table_id):
    cur = con.cursor()
    cur.execute("SELECT server_slug, server_name, server_id FROM Servers where server_name=\"{0}\"".format(realm))
    server_data = cur.fetchone()
    if server_data is None:
        # server lookup failed, so return
        return None

    try:
        cur.execute("UPDATE Players set last_checked = '{0}' where id = {1}".format(get_today(), player_table_id))
    except sqlite3.Error as e:
        print("Couldn't update Player last_checked. Error: {0}".format(e))
    finally:
        print("updating players_checked to date: {0}".format(get_today()))
        con.commit()

    url = "https://{0}.api.battle.net/wow/character/{1}/{2}?fields=items,talents&locale=en_US&apikey=gtzfar8g9nkgd6jzhaug9nn7hfk32sgq".format(zone,  server_data[0], name)
    cur.execute(
        '''SELECT playerid, fetch_date FROM Items where playerid=? and fetch_date=?''', (id, get_today()))
    exists = cur.fetchone()
    if exists is None:
        # fetch items
        print("fetching url: {0}".format(url))
        r = requests.get(url=url)
        # TODO: want to do something with 404s?
        if r.status_code is 200:
            build_item_record(r.json(), zone, id)


def build_item_record(data, zone, id):
    if 'items' not in data:
        return None

    if 'talents' not in data:
        return None

    items = data['items']
    talents = data['talents']
    average_item_level = items['averageItemLevel']
    average_item_level_equipped = items['averageItemLevelEquipped']

    head_id = 0
    neck_id = 0
    shoulder_id = 0
    back_id = 0
    chest_id = 0
    wrist_id = 0
    hands_id = 0
    waist_id = 0
    legs_id = 0
    feet_id = 0
    finger1_id = 0
    finger2_id = 0
    trinket1_id = 0
    trinket2_id = 0
    main_hand_id = 0
    off_hand_id = 0
    relics = []
    if 'head' in items:
        head_id = items['head']['id']
    if 'neck' in items:
        neck_id = items['neck']['id']
    if 'shoulder' in items:
        shoulder_id = items['shoulder']['id']
    if 'back' in items:
        back_id = items['back']['id']
    if 'chest' in items:
        chest_id = items['chest']['id']
    if 'wrist' in items:
        wrist_id = items['wrist']['id']
    if 'hands' in items:
        hands_id = items['hands']['id']
    if 'waist' in items:
        waist_id = items['waist']['id']
    if 'legs' in items:
        legs_id = items['legs']['id']
    if 'feet' in items:
        feet_id = items['feet']['id']
    if 'finger1' in items:
        finger1_id = items['finger1']['id']
    if 'finger2' in items:
        finger2_id = items['finger2']['id']
    if 'trinket1' in items:
        trinket1_id = items['trinket1']['id']
    if 'trinket2' in items:
        trinket2_id = items['trinket2']['id']
    if 'mainHand' in items:
        main_hand_id = items['mainHand']['id']
    if 'offHand' in items:
        off_hand_id = items['offHand']['id']
    if 'mainHand' in items:
        relics = items['mainHand']['relics']
    relics_length = len(relics)
    relics1_bonus1 = 0
    relics1_bonus2 = 0
    relics1_bonus3 = 0
    relics2_bonus1 = 0
    relics2_bonus2 = 0
    relics2_bonus3 = 0
    relics3_bonus1 = 0
    relics3_bonus2 = 0
    relics3_bonus3 = 0
    if relics_length > 0:
        if 'bonusLists' in relics[0]:
            if len(relics[0]['bonusLists']) > 0:
                relics1_bonus1 = relics[0]['bonusLists'][0]
            if len(relics[0]['bonusLists']) > 1:
                relics1_bonus2 = relics[0]['bonusLists'][1]
            if len(relics[0]['bonusLists']) > 2:
                relics1_bonus3 = relics[0]['bonusLists'][2]

    if relics_length > 1:
        if 'bonusLists' in relics[0]:
            if len(relics[1]['bonusLists']) > 0:
                relics2_bonus1 = relics[1]['bonusLists'][0]
            if len(relics[1]['bonusLists']) > 1:
                relics2_bonus2 = relics[1]['bonusLists'][1]
            if len(relics[1]['bonusLists']) > 2:
                relics2_bonus3 = relics[1]['bonusLists'][2]

    if relics_length > 2:
        if 'bonusLists' in relics[0]:
            if len(relics[2]['bonusLists']) > 0:
                relics3_bonus1 = relics[2]['bonusLists'][0]
            if len(relics[2]['bonusLists']) > 1:
                relics3_bonus2 = relics[2]['bonusLists'][1]
            if len(relics[2]['bonusLists']) > 2:
                relics3_bonus3 = relics[2]['bonusLists'][2]

    # add record
    cur = con.cursor()

    try:
        cur.execute('''INSERT INTO Items(playerid, averageItemLevel, averageItemLevelEquipped, head_id, neck_id, shoulder_id, back_id, chest_id, wrist_id, hands_id, waist_id, legs_id, feet_id, finger1_id, finger2_id, trinket1_id, trinket2_id, mainHand_id, offHand_id, relics1_bonus1, relics1_bonus2, relics1_bonus3, relics2_bonus1, relics2_bonus2, relics2_bonus3, relics3_bonus1, relics3_bonus2, relics3_bonus3, fetch_date) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (id, average_item_level, average_item_level_equipped, head_id, neck_id, shoulder_id, back_id, chest_id, wrist_id, hands_id, waist_id, legs_id,
                     feet_id, finger1_id, finger2_id, trinket1_id, trinket2_id, main_hand_id, off_hand_id, relics1_bonus1, relics1_bonus2, relics1_bonus3,
                     relics2_bonus1, relics2_bonus2, relics2_bonus3, relics3_bonus1, relics3_bonus2, relics3_bonus3, get_today()))
    except sqlite3.Error as e:
        print("Couldn't add items for player. Error: {0}".format(e))
    finally:
        print('Adding items for player: {0}.', id)
        con.commit()

    # send talents off
    build_talent_record(id, talents)


def build_talent_record(id, talents):
    print ("building talents for id: {0}".format(id))
    for talent in talents:
        if 'spec' not in talent:
            return None
        tiers = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0
        }
        spec_name = talent['spec']['name']
        spec_role = talent['spec']['role']
        spec_talents = talent['talents']
        for tier in spec_talents:
            if tier is not None:
                selected_tier = tier['tier']
                selected_column = tier['column']
                tiers[selected_tier] = selected_column

        # check if this exists. If not, add it
        cur = con.cursor()
        cur.execute(
            '''SELECT * FROM Talents where playerid=? and spec_name=? and spec_role=? and tier0=? and tier1=? and tier2=? and tier3=? and tier4=? and tier5=? and tier6=?''',
            (id, spec_name, spec_role, tiers[0], tiers[1], tiers[2], tiers[3], tiers[4], tiers[5], tiers[6]))
        exists = cur.fetchone()
        if exists is None:
            try:
                cur.execute('''INSERT INTO Talents(
                playerid, spec_name, spec_role, tier0, tier1, tier2, tier3, tier4, tier5, tier6) VALUES(?,?,?,?,?,?,?,?,?,?)''',
                            (id, spec_name, spec_role, tiers[0], tiers[1], tiers[2], tiers[3], tiers[4], tiers[5], tiers[6]))
            except sqlite3.Error as e:
                print("Couldn't add talents for player. Error: {0}".format(e))
            finally:
                print('Adding talents for player: {0}.', id)
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
if fetch_type is 'all':
    fetch_records = 'all'
else:
    fetch_records = 'new'

print("fetch {0}".format(fetch_records))
start_fetch(fetch_records)

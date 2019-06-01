# ask questions and print out response.
import sqlite3 as lite
import sys
import datetime


def class_name_lookup(id):
    cur = con.cursor()
    cur.execute(
        "SELECT class_id, class_name FROM Classes where class_id={0}".format(id))
    row = cur.fetchone()
    return row[1]


def get_players_from_mythic(dungeon='all', keystone_level_min=0, keystone_level_max=None):
    cur = con.cursor()
    if keystone_level_max is None:
        # just getting players for exact keystone
        if dungeon is not 'all':
            # get specific dungeon
            cur.execute("SELECT keystone_level, tank_id, healer_id, dps1_id, dps2_id, dps3_id FROM Mythics where keystone_level={0} and dungeon_name='{1}'".format(keystone_level_min, dungeon))
        else:
            # get all dungeons
            cur.execute("SELECT keystone_level, tank_id, healer_id, dps1_id, dps2_id, dps3_id FROM Mythics where keystone_level>={0}".format(keystone_level_min))
    else:
        # getting keystone range
        if dungeon is not 'all':
            # get specific dungeon
            cur.execute(
                "SELECT keystone_level, tank_id, healer_id, dps1_id, dps2_id, dps3_id FROM Mythics where keystone_level>={0} and dungeon_name='{1}' and keystone_level >={2}".format(
                    keystone_level_min, dungeon, keystone_level_max))
        else:
            # get all dungeons
            cur.execute(
                "SELECT keystone_level, tank_id, healer_id, dps1_id, dps2_id, dps3_id FROM Mythics where keystone_level>={0} and keystone_level<='{1}'".format(
                    keystone_level_min, keystone_level_max))

    return cur.fetchall()


def get_player_item_level(player_id):
    cur = con.cursor()
    cur.execute("SELECT averageItemLevelEquipped, playerid  FROM Items where playerid={0}".format(player_id))
    has_record = cur.fetchone()
    if has_record:
        return has_record[0]
    else:
        return 0


def get_player_talents(playerid, class_id):
    cur = con.cursor()
    # get player's class ID and if it matches desired ID, continue
    cur.execute("SELECT wow_id, class from Players where wow_id = {0} and class = {1}".format(playerid, class_id))
    exists = cur.fetchone()
    if exists is not None:
        cur.execute("SELECT playerid, spec_name, tier0, tier1, tier2, tier3, tier4, tier5, tier6  FROM Talents where playerid={0}".format(playerid))
        return cur.fetchall()
    else:
        return None


def what_are_top_talents(class_id):
    print("LOOKING FOR CLASS: {0}".format(class_id))
    player_count = 0
    players = get_players_from_mythic('all', 15, 25)
    all_talents = {}
    for group in players:
        for player in group:
            talents = get_player_talents(player, class_id)
            if talents is not None:
                player_count = player_count + 1
                if talents[1] not in all_talents:
                    # add to list
                    all_talents[talents[1]] = {
                        tier## TODO this is going to be messy
                    }
                else:
                    # in list already
                    print("TALENTS: {0}".format(talents))
    print("TOTAL PLAYERS: {0}".format(player_count))


def check_player_class(role, id):
    cur = con.cursor()
    cur.execute(
        "SELECT wow_id, class FROM Players where wow_id={0}".format(id))
    row = cur.fetchone()
    if row:
        print("{0}:{1}".format(role, class_name_lookup(row[1])))


def average_ilevel_for_keystone(dungeon, keystone_level, max_tank, max_healer, max_dps):
    # this report seems to take about 25-30 seconds with 3300 mythic runs
    print("DUNGEON: {0}".format(dungeon))
    print("KEYSTONE LEVEL: {0}".format(keystone_level))
    print("EXCLUDING RUNS WHERE TANK > {0} or HEALER > {1} or ANY DPS > {2}".format(max_tank, max_healer, max_dps))
    cur = con.cursor()
    cur.execute("SELECT keystone_level, tank_id, healer_id, dps1_id, dps2_id, dps3_id FROM Mythics where keystone_level={0} and dungeon_name=\"{1}\"".format(keystone_level, dungeon))
    rows = cur.fetchall()
    overall_item_level = 0
    total_players = 0
    tank_ilevel = 0
    tanks = 0
    healer_ilevel = 0
    healers = 0
    dps_ilevel = 0
    dpsers = 0

    print("MYTHIC RUNS: {0}".format(len(rows)))
    for row in rows:
        tank = get_player_item_level(row[1])
        healer = get_player_item_level(row[2])
        dps1 = get_player_item_level(row[3])
        dps2 = get_player_item_level(row[4])
        dps3 = get_player_item_level(row[5])

        # data correctness check
        if tank > 0 and healer > 0 and dps1 > 0 and dps2 > 0 and dps3 > 0 and tank <= max_tank and healer <= max_healer and dps1 <= max_dps and dps2 <= max_dps and dps3 <= max_dps:
            tanks = tanks + 1
            healers = healers + 1
            dpsers = dpsers + 3
            tank_ilevel = tank_ilevel + tank
            healer_ilevel = healer_ilevel + healer
            dps_ilevel = dps_ilevel + dps1 + dps2 + dps3
            check_player_class('Tank', row[1]);
            check_player_class('Healer', row[2])

    if tanks > 0 and healers > 0 and dpsers > 2:
        print("TANKS: {0} AVG iLEVEL: {1}".format(tanks, tank_ilevel / tanks))
        print("HEALS: {0} AVG iLEVEL: {1}".format(healers, healer_ilevel / healers))
        print("DPS: {0} AVG iLEVEL: {1}".format(dpsers, dps_ilevel / dpsers))
    else:
        print ("All runs exceed max threshold.")


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
#average_ilevel_for_keystone('5', 925, 925, 930)
#average_ilevel_for_keystone('The Arcway', '7', 930, 930, 930)
#average_ilevel_for_keystone('The Arcway', '10', 935, 935, 935)
#average_ilevel_for_keystone('10')
#average_ilevel_for_keystone('20')
# average_ilevel_for_keystone('24')
#what_are_top_talents(7)
average_ilevel_for_keystone("Darkheart Thicket", '15', 940, 940, 945)

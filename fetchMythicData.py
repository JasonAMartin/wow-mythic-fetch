import sqlite3 as lite
import sys
import requests


def get_spec(id):
    specs = {
        62: {'name': 'Mage: Arcane', 'role': 'dps', 'count': 0},
        63: {'name': 'Mage: Fire', 'role': 'dps', 'count': 0},
        64: {'name': 'Mage: Frost', 'role': 'dps', 'count': 0},
        65: {'name': 'Paladin: Holy', 'role': 'heal', 'count': 0},
        66: {'name': 'Paladin: Protection', 'role': 'tank', 'count': 0},
        70: {'name': 'Paladin: Retribution', 'role': 'dps', 'count': 0},
        71: {'name': 'Warrior: Arms', 'role': 'dps', 'count': 0},
        72: {'name': 'Warrior: Fury', 'role': 'dps', 'count': 0},
        73: {'name': 'Warrior: Protection', 'role': 'tank', 'count': 0},
        102: {'name': 'Druid: Balance', 'role': 'dps', 'count': 0},
        103: {'name': 'Druid: Feral', 'role': 'dps', 'count': 0},
        104: {'name': 'Druid: Guardian', 'role': 'tank', 'count': 0},
        105: {'name': 'Druid: Restoration', 'role': 'heal', 'count': 0},
        250: {'name': 'Death Knight: Blood', 'role': 'tank', 'count': 0},
        251: {'name': 'Death Knight: Frost', 'role': 'dps', 'count': 0},
        252: {'name': 'Death Knight: Unholy', 'role': 'dps', 'count': 0},
        253: {'name': 'Hunter: Beast Mastery', 'role': 'dps', 'count': 0},
        254: {'name': 'Hunter: Marksmanship', 'role': 'dps', 'count': 0},
        255: {'name': 'Hunter: Survival', 'role': 'dps', 'count': 0},
        256: {'name': 'Priest: Discipline', 'role': 'heal', 'count': 0},
        257: {'name': 'Priest: Holy', 'role': 'heal', 'count': 0},
        258: {'name': 'Priest: Shadow', 'role': 'dps', 'count': 0},
        259: {'name': 'Rogue: Assassination', 'role': 'dps', 'count': 0},
        260: {'name': 'Rogue: Combat', 'role': 'dps', 'count': 0},
        261: {'name': 'Rogue: Subtlety', 'role': 'dps', 'count': 0},
        262: {'name': 'Shaman: Elemental', 'role': 'dps', 'count': 0},
        263: {'name': 'Shaman: Enhancement', 'role': 'dps', 'count': 0},
        264: {'name': 'Shaman: Restoration', 'role': 'heal', 'count': 0},
        265: {'name': 'Warlock: Affliction', 'role': 'dps', 'count': 0},
        266: {'name': 'Warlock: Demonology', 'role': 'dps', 'count': 0},
        267: {'name': 'Warlock: Destruction', 'role': 'dps', 'count': 0},
        268: {'name': 'Monk: Brewmaster', 'role': 'tank', 'count': 0},
        269: {'name': 'Monk: Windwalker', 'role': 'dps', 'count': 0},
        270: {'name': 'Monk: Mistweaver', 'role': 'heal', 'count': 0},
        577: {'name': 'Demon Hunter: Havoc', 'role': 'dps', 'count': 0},
        581: {'name': 'Demon Hunter: Vengeance', 'role': 'tank', 'count': 0}
    }

    return specs[id]


def get_dungeons():
    return [197, 198, 199, 200, 206, 207, 208, 209, 210, 227, 233, 234, 239]


def get_servers(zone = 'usa'):
    servers = {
        'usa': [1, 3, 5, 57, 1263, 1566, 61, 76],
        'eu': [509, 510, 512, 516, 531, 535, 567, 568, 570, 578, 579, 1306, 632, 506, 627, 1305, 1313]
    }
    # proudmooe 5, thrall 1263, area-52 1566, lightbringer 1, uther 3
    return servers[zone]


def build_mythic_api_calls(zone):
    mythic_calls = []
    for server in get_servers(zone):
        for dungeon in get_dungeons():
            if 'eu' in zone:
                mythic_calls.append("https://eu.api.battle.net/data/wow/connected-realm/{0}/mythic-leaderboard/{1}/period/602?namespace=dynamic-eu&locale=en_GB&access_token=2h7ptfa8vv36v4z7b8b4m6xw".format(server, dungeon))

            if 'us' in zone:
                mythic_calls.append("https://us.api.battle.net/data/wow/connected-realm/{0}/mythic-leaderboard/{1}/period/602?namespace=dynamic-us&locale=en_US&access_token=j6945863mx3g8zdr59kx5tee".format(server, dungeon))
    return mythic_calls


def get_roles(group):
    group_roles = {}
    dps = 1
    for member in group:
        spec = get_spec(member['specialization']['id'])
        member_id = member['profile']['id']
        member_name = member['profile']['name']
        member_realm = member['profile']['realm']['slug']

        if 'tank' in spec['role']:
            group_roles['tank'] = spec
            group_roles['tank']['player'] = member_id
            group_roles['tank']['player_name'] = member_name
            group_roles['tank']['player_realm'] = member_realm

        if 'heal' in spec['role']:
            group_roles['heal'] = spec
            group_roles['heal']['player'] = member_id
            group_roles['heal']['player_name'] = member_name
            group_roles['heal']['player_realm'] = member_realm

        if 'dps' in spec['role']:
            group_roles["dps{0}".format(dps)] = spec
            group_roles["dps{0}".format(dps)]['player'] = member_id
            group_roles["dps{0}".format(dps)]['player_name'] = member_name
            group_roles["dps{0}".format(dps)]['player_realm'] = member_realm
            dps = dps + 1

    return group_roles


def add_mythic_data(res, zone='us'):
    if 'map' in res:
        cur = con.cursor()
        dungeon_name = res['map']['name']
        dungeon_id = res['map']['id']

        for group in res['leading_groups']:
            keystone_level = group['keystone_level']
            completed_timestamp = group['completed_timestamp']
            ranking = group['ranking']
            complete_time = group['duration']
            affix1 = ''
            affix2 = ''
            affix3 = ''
            affix_length = 0
            if 'keystone_affixes' in group:
                affix_length = len(group['keystone_affixes'])
            if affix_length > 0:
                affix1 = group['keystone_affixes'][0]['name']
            if affix_length > 1:
                affix2 = group['keystone_affixes'][1]['name']
            if affix_length > 2:
                affix3 = group['keystone_affixes'][2]['name']
            roles = get_roles(group['members'])

            tank_id = 0
            healer_id = 0
            dps1_id=0
            dps2_id=0
            dps3_id=0
            dps1 = 0
            dps2 = 0
            dps3 = 0
            healer = 0
            tank = 0

            if 'tank' in roles:
                tank = roles['tank']['name']
                tank_id = roles['tank']['player']
                tank_name = roles['tank']['player_name']
                tank_realm = roles['tank']['player_realm']

            if 'heal' in roles:
                healer = roles['heal']['name']
                healer_id = roles['heal']['player']
                healer_name= roles['heal']['player_name']
                healer_realm = roles['heal']['player_realm']

            if 'dps1' in roles:
                dps1 = roles['dps1']['name']
                dps1_id = roles['dps1']['player']
                dps1_name = roles['dps1']['player_name']
                dps1_realm = roles['dps1']['player_realm']

            if 'dps2' in roles:
                dps2 = roles['dps2']['name']
                dps2_id = roles['dps2']['player']
                dps2_name = roles['dps2']['player_name']
                dps2_realm = roles['dps2']['player_realm']

            if 'dps3' in roles:
                dps3 = roles['dps3']['name']
                dps3_id = roles['dps3']['player']
                dps3_name = roles['dps3']['player_name']
                dps3_realm = roles['dps3']['player_realm']

            if 'tank' in roles and 'heal' in roles and 'dps1' in roles and 'dps2' in roles and 'dps2' in roles:
                # Looks like we have all needed data, so see if it's in DB already, otherwise add it.
                cur.execute('''SELECT * FROM Mythics where dungeon_id=? and keystone_level=? and complete_time=? and completed_timestamp=? and tank_id=? and healer_id=?''',
                            (dungeon_id, keystone_level, complete_time, completed_timestamp, tank_id, healer_id))
                exists = cur.fetchone()
                if exists is None:
                    try:
                        cur.execute('''INSERT INTO Mythics(keystone_level, dungeon_id, dungeon_name, complete_time, ranking, affix1, affix2, affix3, tank, tank_id,
                            healer, healer_id, dps1, dps1_id, dps2, dps2_id, dps3, dps3_id, completed_timestamp, tank_realm, tank_name, healer_realm, healer_name,
                            dps1_realm, dps1_name, dps2_realm, dps2_name, dps3_realm, dps3_name, zone) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                                    (keystone_level, dungeon_id, dungeon_name, complete_time, ranking, affix1, affix2, affix3, tank,
                                     tank_id, healer, healer_id, dps1, dps1_id, dps2, dps2_id, dps3, dps3_id, completed_timestamp,
                                     tank_realm, tank_name, healer_realm, healer_name, dps1_realm, dps1_name, dps2_realm, dps2_name, dps3_realm, dps3_name, zone))
                    except e:
                        print("Couldn't add mythic. Error: {0}".format(e))
                    finally:
                        print('Adding new mythic.')
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

# FETCH MYTHIC DATA
print("TOTAL CALLS: {0}".format(len(build_mythic_api_calls('eu'))))
# zone must be us or eu
for mythic_call in build_mythic_api_calls('eu'):
   r = requests.get(url=mythic_call)
   add_mythic_data(r.json(), 'eu')

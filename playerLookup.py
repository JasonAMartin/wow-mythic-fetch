## send in player id and get back stuff
import argparse
import sqlite3 as lite
parser = argparse.ArgumentParser()
parser.add_argument("-id", "--id", help="player's wow id")
args = parser.parse_args()
wow_id = args.id


def get_player_data(id):
    print("Displaying data for player id: {0}".format(id))
    cur = con.cursor()
    cur.execute("SELECT wow_id, name, server, class, race, zone FROM Players where wow_id=\"{0}\"".format(wow_id))
    player_data = cur.fetchone()
    if player_data is not None:
        print ("ID: {0}".format(player_data[0]))
        print ("NAME: {0}".format(player_data[1]))
        print ("SERVER: {0}".format(player_data[2]))
        # get class name
        cur = con.cursor()
        cur.execute("SELECT class_id, class_name FROM Classes where class_id={}".format(player_data[3]))
        class_data = cur.fetchone()
        print ("CLASS: {0}".format(class_data[1]))
        print ("RACE: {0}".format(player_data[4]))
        print ("ZONE: {0}".format(player_data[5]))

try:
    con = lite.connect('./db/WOW.db')
except:
    print('General error')
    sys.exit(1)
finally:
    if con:
        print('connected...')
get_player_data(wow_id)
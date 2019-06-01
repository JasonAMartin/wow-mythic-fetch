# Fetch server data for zones and put in the DB
import sqlite3 as lite
import sys
import requests
import datetime


def start_fetch():
    print("starting server fetch ...")
    master_list = []
    # get all US servers
    master_list.extend(build_server_queries('us'))
    # get all EU servers
    master_list.extend(build_server_queries('eu'))
    for item in master_list:
        build_server_record(item)


def build_server_queries(zone):
    urls = []
    master_url = "https://{0}.api.battle.net/data/wow/connected-realm/?namespace=dynamic-{0}&locale=en_US&access_token=x862y566h7mta25d2mx37v7n".format(zone)
    r = requests.get(url=master_url)
    if r.status_code is 200:
        data = r.json()
        realms = data['connected_realms']
        for realm in realms:
            urls.append({'url': realm['href'], 'zone': zone})
    return urls


def build_server_record(server_link):
    fetch_url = server_link['url'] + "&access_token=x862y566h7mta25d2mx37v7n"
    r = requests.get(url=fetch_url)
    if r.status_code is 200:
        data = r.json()
        realm_data = data['realms'][0]
        server_id = realm_data['id']
        server_name = realm_data['name']['en_US']
        server_slug = realm_data['slug']
        server_zone = server_link['zone']
        cur = con.cursor()
        cur.execute(
            '''SELECT * FROM Servers where server_id=? and server_zone=?''', (server_id, server_zone))
        exists = cur.fetchone()
        if exists is None:
            try:
                cur.execute('''INSERT INTO Servers(server_id, server_name, server_slug, server_zone) VALUES(?,?,?,?)''',
                            (server_id, server_name, server_slug, server_zone))
            except sqlite3.Error as e:
                print("Couldn't add server. Error: {0}".format(e))
            finally:
                print('Adding server: ', server_name)
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

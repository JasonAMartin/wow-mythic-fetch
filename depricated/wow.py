import json
import requests
api_url_base = 'https://us.api.battle.net/wow/character/uther/enviro?fields=items&locale=en_US&apikey=gtzfar8g9nkgd6jzhaug9nn7hfk32sgq'


headers = {'Content-Type': 'application/json'}


def get_account_info():


    response = requests.get(api_url_base, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

account_info = get_account_info()

if account_info is not None:
    print("Here's your info: ")
    # for k, v in account_info['account'].items():
    print('{0}:{1}'.format(account_info['name'], account_info['realm']))

else:
    print('[!] Request Failed')
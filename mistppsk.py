import requests
from os import getenv
from pprint import pprint
from tabulate import tabulate
from datetime import datetime

murl = 'https://api.mist.com/api/v1'
my_headers = {"Authorization": f"Token {getenv('MIST_TOKEN')}",
              "Content-Type": "application/json"}
sesh = requests.Session()
orgid = sesh.get(f"{murl}/self", headers=my_headers).json()['privileges'][0]['org_id']  # assumes only 1 item returned


def main():
    quit = False
    while not quit:
        url = f"{murl}/orgs/{orgid}/psks"

        psks = sesh.get(url, headers=my_headers).json()  # list of dictionaries of all PSKs
        psks.sort(key=Name_Sort)  # now the list is sorted

        pprint(psks)

        ListPsks(psks)
        bad_input = True
        while bad_input:
            selection = input("Update which PSK (q to quit): ")
            if selection.lower() == 'q':
                quit = True
                bad_input = False
            else:
                try:
                    selection = int(selection)
                    psks[selection]
                    bad_input = False
                except ValueError:
                    print("Bad input, not an integer, try again.")
                    continue
                except IndexError:
                    print("Bad input, out of range, try again.")
                    continue

            UpdatePsk(psks[selection])
    sesh.close()


def UpdatePsk(psk):
    pass


def ListPsks(psks):
    #GET /api/v1/orgs/:org_id/psks?name=Common&role=student&sort=ssid&limit=200&page=3

    """
    SCHEMA
{
    "name": "Common",
    "passphrase": "foryoureyesonly",
    "ssid": "warehouse",
    "usage": "single",
    "vlan_id": 417,            // optional
    "mac": "5684dae9ac8b",     // optional
    "role": "",                // optional
    "expire_time": 1614990263  // optional, epoch time in seconds, default is null, as no expiration
    "max_usage": 20            // optional, default is 0 (unlimited)
    "notes": "notes"           // optional
    "notify_expiry": true      // optional
    "expiry_notification_time": 2      // optional, unit days
    "notify_on_create_or_edit": true   // optional
    "email": "admin@test.com"  // optional, email to send psk expiring notifications to
    "admin_sso_id": "sso_id"  // optional, sso id for psk created from psk portal
}
    :return:
    """

    pprint(psks)

    psk_data = []
    for index, psk in enumerate(psks):

        try:
            max_usage = psk['max_usage']
        except KeyError:
            max_usage = ''

        try:
            vlan = psk['vlan_id']
        except KeyError:
            vlan = ''

        if psk['expire_time'] is None:
            expiry = ''
        else:
            expiry = EpochToHuman(psk['expire_time'])

        if psk['usage'] == "single":
            mac = psk['mac']
            max_usage = 1
        else:
            mac = ''

        try:
            email = psk['email'] if psk['notify_on_create_or_edit'] else ''
        except KeyError:
            email = ''

        psk_data.append([index, psk['name'], vlan, psk['usage'], max_usage, mac, expiry, email])

    header_row = ['#', 'PSK Name', 'VLAN', 'Usage', 'Max Usage', 'MAC', 'Expires', 'Notify Email']
    psk_table = tabulate(psk_data, headers=header_row, tablefmt='orgtbl')

    print("\nPSKs:")
    print(psk_table)


def IntCatch(promptstr):

    bad_input = True
    resp = ''
    while bad_input:
        try:
            resp = int(input(promptstr))
            bad_input = False
        except ValueError:
            print("Bad input, try again.")

    return resp


def Name_Sort(dictionary):
    return dictionary['name']


def EpochToHuman(epoch):

    # Convert epoch time to datetime object
    datetime_obj = datetime.fromtimestamp(epoch)

    # Convert datetime object to human-readable format displayed in system's timezone
    human_readable_time = datetime_obj.strftime("%Y-%m-%d %H:%M:%S ")

    return(human_readable_time + datetime.now().astimezone().tzname())  # Example output: 2021-03-30 12:00:00


main()
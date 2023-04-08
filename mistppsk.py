import requests
from os import getenv
from tabulate import tabulate
from datetime import datetime

murl = 'https://api.mist.com/api/v1'
my_headers = {"Authorization": f"Token {getenv('MIST_TOKEN')}",
              "Content-Type": "application/json"}
sesh = requests.Session()
self = sesh.get(f"{murl}/self", headers=my_headers).json()
name = self['name']
orgid = self['privileges'][0]['org_id']  # assumes only 1 item returned in privileges
print("Hello,", name)


def main():
    do_quit = False
    while not do_quit:
        psks = get_psks()
        list_psks(psks)

        bad_input = True
        while bad_input:
            selection = input("Update which PSK (q to quit): ")
            if selection.lower() == 'q':
                do_quit = True
                bad_input = False
            else:
                try:
                    selection = int(selection)
                    if selection < 0:
                        print("Cannot be negative.")
                        continue
                    else:
                        update_psk(psks[selection])
                        bad_input = False
                except ValueError:
                    print("Bad input, not an integer or 'q', try again.")
                    continue
                except IndexError:
                    print("Bad input, out of range, try again.")
                    continue

    sesh.close()

def get_psks():
    url = f"{murl}/orgs/{orgid}/psks?sort=name"

    psks = sesh.get(url, headers=my_headers).json()  # list of dictionaries of all PSKs
    psks.sort(key=name_sort)  # now the list is sorted by name

    return psks

def update_psk(psk):
    fields = list(psk.keys())
    fields.sort()
    header_row = ["#", "Attribute", "Value"]

    # Build field_data table with list comprehension. check to see if the field name contains the word time. if it does,
    # convert the time from epoch to human. Otherwise, just copy the value of the field into the list.
    field_data = [[index, field, epoch_to_human(psk[field])] if field.find("time") > -1 and psk[field] is not None
                  else [index, field, psk[field]] for index, field in enumerate(fields)]

    field_table = tabulate(field_data, headers=header_row, tablefmt='orgtbl')

    print(field_table)

    if yn("Would you like to change notes (y/n)? ") == 'y':
        psk = notes(psk)

    if yn("Would you like to change max usage (y/n)? ") == 'y':
        psk = max_usage(psk)

    sesh.put(url=f"{murl}/orgs/{orgid}/psks/{psk['id']}", headers=my_headers, json=psk)

def max_usage(psk):
    try:
        if int(psk['max_usage']) > 0:
            print(f"Current max_usage: {psk['max_usage']}")
        else:
            print("Current max_usage: unlimited")
    except KeyError:
        if psk['usage'] == 'single':
            print(f"Current usage is set to single with MAC {psk['mac']}")
        else:
            print("Current max_usage: unlimited")

    my_max = -1
    while my_max < 0:
        my_max = int_catch("New max usage (0 for unlimited): ")
        if my_max < 0:
            print ("Cannot be negative.")

    psk['max_usage'] = my_max

    return psk


def notes(psk):
    try:
        print(f"Current notes: {psk['notes']}")
    except KeyError:
        print("Current notes:")

    notes = input("Enter new notes (blank to remove existing notes): ")
    if notes != '':
        notes = f'{name}: {notes}'

    psk['notes'] = notes

    return psk


def list_psks(psks):
    psk_data = []
    for index, psk in enumerate(psks):

        try:
            max_usage = int(psk['max_usage'])
            if max_usage == 0:
                max_usage = ''
        except KeyError:
            max_usage = ''

        if psk['usage'] == "single":
            mac = psk['mac']
        else:
            mac = ''

        try:
            notes = psk['notes']
        except KeyError:
            notes = ''

        psk_data.append([index, psk['name'], psk['usage'], max_usage, mac, notes])

    header_row = ['#', 'PSK Name', 'Usage', 'Max Usage', 'MAC', 'Notes']
    psk_table = tabulate(psk_data, headers=header_row, tablefmt='orgtbl')

    print("\nPSKs:")
    print(psk_table)


def yn(promptstr):
    selection = ''
    bad_input = True
    while bad_input:
        selection = input(promptstr).lower()
        if selection != 'y' and selection != 'n':
            print("Bad input, please respond with 'y' or 'n'.")
        else:
            bad_input = False
    return selection


def int_catch(prompt_str):
    bad_input = True
    resp = ''
    while bad_input:
        try:
            resp = int(input(prompt_str))
            bad_input = False
        except ValueError:
            print("Bad input, not an integer, try again.")

    return resp


def name_sort(dictionary):
    return dictionary['name']


def epoch_to_human(epoch):
    # Convert epoch time to datetime object
    datetime_obj = datetime.fromtimestamp(epoch)

    # Convert datetime object to human-readable format displayed in system's timezone
    human_readable_time = datetime_obj.strftime("%Y-%m-%d %H:%M:%S ")

    return human_readable_time + datetime.now().astimezone().tzname()  # Example output: 2021-03-30 12:00:00 PDT


main()
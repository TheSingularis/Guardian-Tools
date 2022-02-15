import pickle  # Optional
import requests
import zipfile
import os
import json
import sqlite3


# dictionary that tells where to get the hashes for each table
# FULL DICTIONARY
hash_dict = {
    'DestinyClassDefinition': 'hash',
    'DestinyRaceDefinition': 'hash',
    'DestinyGenderDefinition': 'hash',
    'DestinyInventoryBucketDefinition': 'hash',
    'DestinyInventoryItemDefinition': 'hash',
    'DestinyProgressionDefinition': 'hash',
    'DestinyRecordDefinition': 'hash',
    'DestinyPresentationNodeDefinition': 'hash',
    'DestinyObjectiveDefinition': 'hash'
}


def get_manifest():
    manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'
    # get the manifest location from the json
    r = requests.get(manifest_url)
    manifest = r.json()
    mani_url = 'http://www.bungie.net'+manifest['Response']['mobileWorldContentPaths']['en']
    # Download the file, write it to manifest-zip
    r = requests.get(mani_url)
    with open("data/manifest-zip", "wb") as zip:
        zip.write(r.content)
    print("Download Complete!")

    # Extract the file contents, and rename the extracted file
    # to 'manifest.content'
    with zipfile.ZipFile('data/manifest-zip') as zip:
        name = zip.namelist()
        zip.extractall()
    os.rename(name[0], 'data/manifest.content')
    print('Unzipped!')


def build_dict(hash_dict):
    # connect to the manifest
    con = sqlite3.connect('data/manifest.content')
    print('Connected')
    # create a cursor object
    cur = con.cursor()

    all_data = {}
    # for every table name in the dictionary
    for table_name in hash_dict.keys():
        # get a list of all the jsons from the table
        cur.execute('SELECT json from '+table_name)
        print('Generating '+table_name+' dictionary....')

        # this returns a list of tuples: the first item in each tuple is our json
        items = cur.fetchall()

        # create a list of jsons
        item_jsons = [json.loads(item[0]) for item in items]

        # create a dictionary with the hashes as keys
        # and the jsons as values
        item_dict = {}
        hash = hash_dict[table_name]
        for item in item_jsons:
            item_dict[item[hash]] = item

        # add that dictionary to our all_data using the name of the table
        # as a key.
        all_data[table_name] = item_dict
    print('Dictionary Generated!')
    return all_data


# check if pickle exists, if not create one.
if os.path.isfile('data/manifest.pickle') == False:
    print('Pickle Not Found')
    print('Downloading Database')

    get_manifest()
    all_data = build_dict(hash_dict)
    with open('data/manifest.pickle', 'wb') as data:
        pickle.dump(all_data, data)
    print("'data/manifest.pickle' created!\nDONE!")
else:
    print('Pickle Already Exists')
    print('Replacing Database')

    get_manifest()
    all_data = build_dict(hash_dict)
    with open('data/manifest.pickle', 'wb') as data:
        pickle.dump(all_data, data)
    print("'data/manifest.pickle' created!\nDONE!")

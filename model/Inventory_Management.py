import requests
import json

# URL Builder:
base_url = "https://www.bungie.net/platform/Destiny2/"
# Vault size:
#vaultArmour = 108
#vaultWeapons = 108
#vaultInventory = 72
vaultSize = 500

invItems = {
    #			0 : 'Lost Items',
    1: 'Primary Weapons',
    2: 'Special Weapons',
    3: 'Heavy Weapons',
    4: 'Ghost',
    5: 'Helmet',
    6: 'Gauntlets',
    7: 'Chest Armor',
    8: 'Leg Armor',
    9: 'Class Armor',
    10: 'Artifacts',
    11: 'Vehicle',
    12: 'Sparrow Horn',
    13: 'Ships',
    14: 'Shaders',
    15: 'Emblems',
    16: 'Emotes',
    17: 'Weapon Bundles',
}
# Uncomment this line to print JSON output to a file:
#f = open('inventoryItem.txt', 'w')


def transferItem(payload, session):
    req_string = base_url + "TransferItem/"
    print("Transferring item from vault to character...")
    res = session.post(req_string, data=payload)
    error_stat = res.json()['ErrorStatus'].decode('utf-8')
    print("Error status: " + error_stat + "\n")
    return res


def equipItem(payload, session):
    # Send the request to equip the item:
    equip_url = base_url + "EquipItem/"
    print("Equipping item...")
    res = session.post(equip_url, data=payload)
    error_stat = res.json()['ErrorStatus'].decode('utf-8')
    print("Error status: " + error_stat + "\n")
    return res


def getVault(session, membershipType, destinyMembershipId):
    getVault_url = base_url + membershipType + "/Profile/" + destinyMembershipId + "/?components=ProfileInventories"
    res = session.get(getVault_url)
    error_stat = res.json()['ErrorStatus']
    print("getVault Error status: " + error_stat + "\n")
    return res


def getCharacterInventory(session, characterId):
    req_string = base_url + membershipType + "/Account/" + destinyMembershipId + "/Character/" + characterId + "/Inventory/"
    print("Fetching data for: " + req_string + "\n")
    res = session.get(req_string)
    error_stat = res.json()['ErrorStatus']
    print("getCharacterInventory Error status: " + error_stat + "\n")
    return res


def getCharacterInventorySummary(session, membershipType, destinyMembershipId, characterId):
    req_string = base_url + membershipType + "/Account/" + destinyMembershipId + "/Character/" + characterId + "/Inventory/Summary/"
    print("Fetching data for: " + req_string + "\n")
    res = session.get(req_string)
    error_stat = res.json()['ErrorStatus']
    print("getCharacterInventorySummary Error status: " + error_stat + "\n")
    return res


def parsegetCharacterInventorySummary(session, charInventorySummary, all_data):
    array_size = 0
    vault_list = [{
        'itemName': '',
        'tierTypeName': '',
        'itemTypeName': '',
        'icon': '',
        'bucket': '',
    } for array_size in range(vaultSize)]
    array_size = 0

    for item in charInventorySummary.json()['Response']['data']['items']:
        vault_list[array_size]['itemReferenceHash'] = item['itemHash']
        vault_list[array_size]['itemId'] = item['itemId']
        inventoryItem = all_data['DestinyInventoryItemDefinition'][item['itemHash']]
        #f.write (json.dumps(inventoryItem, indent=4))
        if (inventoryItem['displayProperties']['name'] != ""):
            bucketHash = all_data['DestinyInventoryBucketDefinition'][item['bucketHash']]
            vault_list[array_size]['itemName'] = inventoryItem['displayProperties']['name']
            if ((inventoryItem['displayProperties']['name'] != "Classified") and (inventoryItem['hash'] != 1826822442) and (item['bucketHash'] != 1801258597)):
                vault_list[array_size]['itemName'] = inventoryItem['displayProperties']['name']
                vault_list[array_size]['tierTypeName'] = inventoryItem['tierTypeName']
                vault_list[array_size]['itemTypeName'] = inventoryItem['itemTypeName']
                vault_list[array_size]['icon'] = "http://www.bungie.net/" + inventoryItem['icon']
                vault_list[array_size]['bucket'] = bucketHash['bucketName']
        array_size += 1

    return vault_list


def parseVault(session, vaultResult, all_data):
    array_size = 0
    weapon_list = [{
        "itemReferenceHash": 0,
        "itemId": 0,
        'itemName': '',
        'tierTypeName': '',
        'itemTypeName': '',
        "stackSize": 1,
        'icon': '',
        'bucket': '',
        'equipped': '',
    } for array_size in range(vaultSize)]

    # print(vaultResult)
    # print(vaultResult.json()['Response'])

    # with open("profileInventoryOutput.json", "w") as text_file:
    #    text_file.write(str(vaultResult.json()['Response']).replace("'", "\"").replace("True", "true").replace("False", "false"))

    for item in vaultResult.json()['Response']['profileInventory']['data']['items']:
        weapon_list[array_size]['itemReferenceHash'] = item['itemHash']
        inventoryItem = all_data['DestinyInventoryItemDefinition'][item['itemHash']]
        weapon_list[array_size]['itemName'] = inventoryItem['displayProperties']['name']
        if ((inventoryItem['displayProperties']['name'] != "Classified") and (inventoryItem['hash'] != 1826822442)):
            # Equipped item or Subclass:
            if ((item['transferStatus'] == 3) or (item['transferStatus'] == 1)):
                weapon_list[array_size]['equipped'] = True
            bucketHash = all_data['DestinyInventoryBucketDefinition'][inventoryItem['inventory']['bucketTypeHash']]
            weapon_list[array_size]['itemName'] = inventoryItem['displayProperties']['name']
            weapon_list[array_size]['tierTypeName'] = inventoryItem['inventory']['tierTypeName']
            weapon_list[array_size]['itemTypeName'] = inventoryItem['itemTypeDisplayName']
            weapon_list[array_size]['icon'] = "https://www.bungie.net" + inventoryItem['displayProperties']['icon']
            weapon_list[array_size]['bucket'] = bucketHash['displayProperties']['name'] if "name" in bucketHash['displayProperties'] else ""
        if ((inventoryItem['displayProperties']['name'] == "Classified") or (inventoryItem['hash'] == 1826822442)):  # or (inventoryItem['bucketTypeHash'] == 0)):
            weapon_list[array_size]['itemName'] = inventoryItem['displayProperties']['name']
            weapon_list[array_size]['tierTypeName'] = "Classified"
            weapon_list[array_size]['itemTypeName'] = "Classified"
            weapon_list[array_size]['bucket'] = "Classified"
        array_size += 1

    return weapon_list


def parseVaultHtml(session, vaultResult, all_data):
    array_size = 0
    vault_list = [{
        'itemName': '',
        'tierTypeName': '',
        'itemTypeName': '',
        'icon': '',
    } for array_size in range(vaultSize)]
    array_size = 0

    for bucket in vaultResult.json()['Response']['data']['buckets']:
        for item in bucket['items']:
            hashReqString = base_url + "Manifest/6/" + str(item['itemHash'])
            vault_list[array_size]['itemReferenceHash'] = item['itemHash']
            vault_list[array_size]['itemId'] = item['itemInstanceId']
            inventoryItem = all_data['DestinyInventoryItemDefinition'][item['itemHash']]
            if (inventoryItem['displayProperties']['name'] != ""):
                vault_list[array_size]['itemName'] = inventoryItem['displayProperties']['name']
                vault_list[array_size]['tierTypeName'] = inventoryItem['tierTypeName']
                vault_list[array_size]['itemTypeName'] = inventoryItem['itemTypeName']
                vault_list[array_size]['icon'] = "http://www.bungie.net/" + inventoryItem['icon']
            # print "Item name is: " + vault_list[array_size]['itemName']
            array_size += 1

    return vault_list


def GetCharacterSummary(session, membershipType, destinyMembershipId):
    req_string = base_url + membershipType + "/Account/" + destinyMembershipId + "/Character/" + characterId + "/"
    res = session.get(req_string)
    print(req_string)
    error_state = res.json()['ErrorStatus'].decode('utf-8')
    print("Error status: " + error_state + "\n")
    return res


def GetCurrentBungieUser(session):
    req_string = 'https://www.bungie.net/Platform/User/GetCurrentBungieNetUser/'
    res = session.get(req_string)
    print(req_string)
    error_state = res.json()['ErrorStatus'].decode('utf-8')
    print("Error status: " + error_state + "\n")
    return res


def GetAdvisorsForCharacter(session, membershipType, destinyMembershipId, characterId):
    req_string = base_url + membershipType + "/Account/" + destinyMembershipId + "/Character/" + characterId + "/Advisors/"
    res = session.get(req_string)
    print(req_string)
    error_state = res.json()['ErrorStatus'].decode('utf-8')
    print("getAdvisorsForCharacter Error status: " + error_state + "\n")
    return res


def getAccount(session, membershipType, destinyMembershipId):
    req_string = base_url + membershipType + "/Account/" + destinyMembershipId + "/"
    res = session.get(req_string)
    print(req_string)
    error_state = res.json()['ErrorStatus'].decode('utf-8')
    print("getAccount Error status: " + error_state + "\n")
    return res

# https://www.bungie.net/Platform/User/GetBungieNetUser/


def GetCurrentUser(session):
    req_string = 'https://www.bungie.net/Platform/User/GetBungieNetUser/'
    res = session.get(req_string)
    print(req_string)
    error_state = res.json()['ErrorStatus'].decode('utf-8')
    print("getCurrentUser Error status: " + error_state + "\n")
    return res

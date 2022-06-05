base_url = "https://www.bungie.net/platform/Destiny2"


def GetCurrentBungieAccount(session):
    req_string = 'https://www.bungie.net/Platform/User/GetCurrentBungieAccount/'
    res = session.get(req_string)
    # print(req_string)
    error_state = res.json()['ErrorStatus']
    print("getCurrentBungieAccount Error status: " + error_state + "\n")
    return res


def GetAccountInfo(session, membershipType, destinyMembershipId):
    getAccount_url = base_url + "/" + membershipType + "/Profile/" + destinyMembershipId + "/?components=Profiles,ProfileInventories,Characters"
    res = session.get(getAccount_url)
    error_stat = res.json()['ErrorStatus']
    print("getAccountInfo Error status: " + error_stat + "\n")
    return res


def GetCharId(oauth_session, session, char_num):  # char_num: int between 0 and 2
    accountSummary = GetAccountInfo(oauth_session, session.get('membershipType'), session.get('destinyMembershipId'))

    return list(accountSummary.json()['Response']['characters']['data'])[char_num]


def GetCharacters(accountSummary, all_data):
    charCount = len(list(accountSummary.json()['Response']['characters']['data']))
    characters = [None] * charCount

    for x in range(0, charCount):
        charId = list(accountSummary.json()['Response']['characters']['data'])[x]
        char = accountSummary.json()['Response']['characters']['data'][charId]

        charClass = all_data['DestinyClassDefinition'][char['classHash']]['genderedClassNamesByGenderHash'][str(char['genderHash'])]
        title = all_data['DestinyRecordDefinition'][char['titleRecordHash']]['titleInfo']['titlesByGenderHash'][str(
            char['genderHash'])] if "titleRecordHash" in char else ""

        characters[x] = Character(charClass,
                                  char['light'],
                                  title,
                                  char['emblemBackgroundPath']
                                  )

    return characters


class Character():
    def __init__(self, charClass, lightLevel, title, backgroundImage):
        self.charClass = charClass
        self.lightLevel = lightLevel
        self.title = title
        self.backgroundImage = backgroundImage

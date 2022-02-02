import requests
import json

from Account_Management import *

base_url = "https://www.bungie.net/platform/Destiny2/"

weekOneChallenges = 10
weekTwoChallenges = 10
weekThreeChallenges = 10
weekFourChallenges = 9
weekFiveChallenges = 7
weekSixChallenges = 7
weekSevenChallenges = 7
weekEightChallenges = 6
weekNineChallenges = 6
weekTenChallenges = 5

totalChallenges = (weekOneChallenges +
                   weekTwoChallenges +
                   weekThreeChallenges +
                   weekFourChallenges +
                   weekFiveChallenges +
                   weekSixChallenges +
                   weekSevenChallenges +
                   weekEightChallenges +
                   weekNineChallenges +
                   weekTenChallenges +
                   1)   # Add one for the "Complete all seasonal challenges triumph"


def getProgress(session, membershipType, destinyMembershipId):
    getProgress_url = base_url + membershipType + "/Profile/" + destinyMembershipId + "/?components=Records"
    res = session.get(getProgress_url)
    error_stat = res.json()['ErrorStatus']
    print("getProgress Error Status: " + error_stat + "\n")
    return res


def parseProgress(session, progressResult, all_data, firstChar):
    parentNodes = {4143126230,  # Week 1
                   4143126229,  # Week 2
                   4143126228,  # Week 3
                   4143126227,  # Week 4
                   4143126226,  # Week 5
                   4143126225,  # Week 6
                   4143126224,  # Week 7
                   4143126239,  # Week 8
                   4143126238,  # Week 9
                   2527916754,  # Week 10
                   3608142460   # Seasonal Capstone
                   }

    triumphs = [None] * totalChallenges
    loop_count = 0

    for item in progressResult.json()['Response']['characterRecords']['data'][firstChar]['records']:
        if len(list(all_data['DestinyRecordDefinition'][int(item)]['parentNodeHashes'])) > 0:
            parentNodeHash = all_data['DestinyRecordDefinition'][int(item)]['parentNodeHashes'][0]
            if parentNodeHash in parentNodes:
                record = all_data['DestinyRecordDefinition'][int(item)]

                # make a list of the objectives for each record

                triumphs[loop_count] = Triumph(record['index'],
                                               record['displayProperties']['name'],
                                               record['displayProperties']['description'],
                                               "http://www.bungie.net" + record['displayProperties']['icon'])
                loop_count += 1

    return triumphs


class Triumph():
    def __init__(self, index, challengeName, challengeDescription, icon):
        self.index = index
        self.challengeName = challengeName
        self.challengeDescription = challengeDescription
        self.icon = icon

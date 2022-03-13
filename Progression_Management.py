from inspect import trace
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
    """
    search the DestinyPresentationNodeDefinition for 'Seasonal Challenges'
        this gets us 'Weekly' and 'Past'
        'Weekly':
            Children for each week + one parent for the completionist capstone:
                Week:
                    Challenges to list
        'Past Challenges':
            Children for each prior season:
                Challenges to list

    """

    for record in all_data['DestinyPresentationNodeDefinition']:    # Loop all records
        if "Seasonal Challenges" in all_data['DestinyPresentationNodeDefinition'][int(record)]['displayProperties']['name']:   # Find the Seasonal Challenges record

            #print(f"seasonal challenges hash: {str(record)}")

            # This returns the hashes for weekly and past challenges (prior to Witch Queen)
            childHashes = list(all_data['DestinyPresentationNodeDefinition'][int(record)]['children']['presentationNodes'])

            if len(childHashes) > 0:
                weeklyHash = childHashes[0]['presentationNodeHash']
                #print(f"weekly hash: {weeklyHash}")

            if len(childHashes) > 1:
                pastChallengesHash = childHashes[1]
                # TODO: Implement previous seasons, kinda hard rn (03/12/2022) cuz theres no previous seasons available

            weekNodes = [None] * 0

            for node in list(all_data['DestinyPresentationNodeDefinition'][int(weeklyHash)]['children']['presentationNodes']):
                weekNodes.append(node['presentationNodeHash'])

            triumphList = getChallengesFromParentNodes(progressResult, all_data, firstChar, weekNodes)

            seasonTitle = ""
            for t in triumphList:
                if "Season of" in t.challengeDescription:
                    words = t.challengeDescription.split()

                    while (words[0] != "Season") & (len(words) > 0):
                        words.pop(0)

                    if words[2] == "the":
                        seasonTitle = " ".join(words[0:4])
                    else:
                        seasonTitle = " ".join(words[0:3])

            seasons = [None] * 0
            seasons.append(Season(seasonTitle, triumphList))

            # TODO: Finish This, the above hashes need to be searched in the ['DestinyPresentationNodeDefinition'] table and then use their children to get the list of 'parentNodes' like below

            # for presentationNode in all_data['DestinyPresentationNodeDefinition'][int(record)]['children']['presentationNodes']:
            # print(f"presentaion node hash: {str(presentationNode)}")

    return seasons


def getChallengesFromParentNodes(progressResult, all_data, firstChar, parentNodes):
    triumphs = [None] * totalChallenges
    loop_count = 0

    for item in progressResult.json()['Response']['characterRecords']['data'][firstChar]['records']:
        if len(list(all_data['DestinyRecordDefinition'][int(item)]['parentNodeHashes'])) > 0:
            parentNodeHash = all_data['DestinyRecordDefinition'][int(item)]['parentNodeHashes'][0]
            if parentNodeHash in parentNodes:
                record = all_data['DestinyRecordDefinition'][int(item)]

                if len(list(record['objectiveHashes'])) > 0:
                    objectives = []
                    for apiObj in progressResult.json()['Response']['characterRecords']['data'][firstChar]['records'][item]['objectives']:
                        databaseObj = all_data['DestinyObjectiveDefinition'][apiObj['objectiveHash']]

                        objectives.append(Objective(databaseObj['displayProperties']['name'],
                                                    databaseObj['displayProperties']['description'],
                                                    databaseObj['progressDescription'],
                                                    apiObj['progress'],
                                                    apiObj['completionValue'],
                                                    apiObj['complete'],
                                                    apiObj['objectiveHash']))

                triumphs[loop_count] = Triumph(record['index'],
                                               record['displayProperties']['name'],
                                               record['displayProperties']['description'],
                                               objectives,
                                               "http://www.bungie.net" + record['displayProperties']['icon'])

                loop_count += 1

    # Clear None values, None values occur if there is a week of challenges that has not yet been released
    fixedList = []

    for t in triumphs:
        if t != None:
            fixedList.append(t)

    return fixedList


class Season():
    def __init__(self, title, triumphs):
        self.title = title
        self.triumphs = triumphs


class Triumph():
    def __init__(self, index, challengeName, challengeDescription, objectives, icon):
        self.index = index
        self.challengeName = challengeName
        self.challengeDescription = challengeDescription
        self.objectives = objectives
        self.icon = icon

    def getComplete(self):
        complete = True

        for objective in self.objectives:
            if objective.complete == False:
                complete = False

        return complete


class Objective():
    def __init__(self, objName, objDescription, progressDescription, progressValue, completionValue, complete, objHash):
        self.objName = objName
        self.objDescription = objDescription
        self.progressDescription = progressDescription
        self.progressValue = progressValue
        self.completionValue = completionValue
        self.complete = complete
        self.objHash = objHash

    def getProgressValue(self):
        return self.completionValue if self.progressValue >= self.completionValue else self.progressValue

    def getCompletion(self):
        return (self.progressValue / self.completionValue) * 100

    def getCompletionString(self):
        return str(int(self.getCompletion()))

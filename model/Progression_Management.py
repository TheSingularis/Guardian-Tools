import requests
import json

from model.Account_Management import *

base_url = "https://www.bungie.net/platform/Destiny2/"


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

    parentNodes = []

    for record in all_data['DestinyPresentationNodeDefinition']:    # Loop all records
        if "Seasonal Challenges" in all_data['DestinyPresentationNodeDefinition'][int(record)]['displayProperties']['name']:   # Find the Seasonal Challenges record
            print(f"seasonal challenges hash: {str(record)}")
            # This returns the hashes for weekly and past challenges (prior to Witch Queen)
            childHashes = list(all_data['DestinyPresentationNodeDefinition'][int(record)]['children']['presentationNodes'])

            weeklyHash = childHashes[0]['presentationNodeHash']
            pastChallengesHash = childHashes[1]

            # TODO: Finish This, the above hashes need to be searched in the ['DestinyPresentationNodeDefinition'] table and then use their children to get the list of 'parentNodes' like below

            for presentationNode in all_data['DestinyPresentationNodeDefinition'][weeklyHash]['children']['presentationNodes']:
                parentNodes.append(presentationNode['presentationNodeHash'])

    triumphs = []

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

                triumphs.append(Triumph(record['index'],
                                        record['displayProperties']['name'],
                                        record['displayProperties']['description'],
                                        objectives,
                                        "http://www.bungie.net" + record['displayProperties']['icon']))

    return triumphs


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

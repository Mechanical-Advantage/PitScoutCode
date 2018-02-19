import numpy as np
import sqlite3 as sql

#Defines the fields stored in the "Scout" table of the database. This database stores the record for each match scan
SCOUT_FIELDS = {
    "Team": 0,
    "Match": 0,
    "Fouls": 0,
    "TechFouls": 0,
    "intakeType": 0,
    "deliveryMethod": 0,
    "driveTrain": 0,
    "NumDelToScale": 0,
    "NumDelToSwitch": 0,
    "NumDelToXchange": 0,
    "canClimb": 0,
    "canSupportOthers": 0,
    "canDriveOverBump": 0,
    "canDriveOnRamp": 0,
    "autoDelToSwitchAcross": 0,
    "autoDelToScaleAcross": 0,
    "autoCrossLineFromLeft": 0,
    "autoCrossLineFromCenter": 0,
    "autoCrossLineFromRight": 0,
    "autoToSwitchFromLeft": 0,
    "autoToSwitchFromCenter": 0,
    "autoToSwitchFromRight": 0,
    "autoToScaleFromLeft": 0,
    "autoToScaleFromCenter": 0,
    "autoToScaleFromRight": 0,
    "autoToXchangeFromLeft": 0,
    "autoToXchangeFromCenter": 0,
    "autoToXchangeFromRight": 0,
    "SpareField1": 0,
    "SpareField2": 0,
    "Replay": 0,
    "Flag": 0
}

#Defines the fields that are stored in the "averages" and similar tables of the database. These are the fields displayed on the home page of the website.
AVERAGE_FIELDS = {
    "team": 0,
    "apr":0,
    "NumDelToScale": 0,
    "NumDelToSwitch": 0,
    "NumDelToXchange": 0
}

#Defines the fields displayed on the charts on the team and compare pages
CHART_FIELDS = {
    "match": 0,
    "NumDelToScale": 0,
    "NumDelToSwitch": 0,
    "NumDelToXchange": 0
}


# Main method to process a full-page sheet
# Submits three times, because there are three matches on one sheet
# The sheet is developed in Google Sheets and the coordinates are defined in terms on the row and column numbers from the sheet.
def processSheet(scout):
    for s in (0, 16, 32):
        #Sets the shift value (used when turning cell coordinates into pixel coordinates)
        scout.shiftDown(s)

        num1 = scout.rangefield('J-5', 0, 9)
        num2 = scout.rangefield('J-6', 0, 9)
        num3 = scout.rangefield('J-7', 0, 9)
        num4 = scout.rangefield('J-8', 0, 9)
        scout.set("Team", 1000 * num1 + 100 * num2 + 10 * num3 + num4)
        scout.set("Match", 1)

        scout.set("Fouls", int(0))
        scout.set("TechFouls", int(0))

        scout.set("intakeType", scout.rangefield('I-11', 0, 3))
        scout.set("deliveryMethod", scout.rangefield('I-14', 0, 4))
        scout.set("driveTrain", scout.rangefield('I-17', 0, 3))
        scout.set("NumDelToScale", scout.rangefield('AA-7', 0, 9))
        scout.set("NumDelToXchange", scout.rangefield('AA-8', 0, 9))
        numallsw1 = scout.rangefield('AA-5', 0, 9)
        numallsw2 = scout.rangefield('AA-6', 0, 9)
        scout.set("NumDelToSwitch", numallsw1 * 10 + numallsw2)
        scout.set("canClimb", scout.boolfield('AJ-13'))
        scout.set("canSupportOthers", scout.boolfield('AJ-14'))
        scout.set("canDriveOverBump", scout.boolfield('AJ-15'))
        scout.set("canDriveOnRamp", scout.boolfield('AJ-16'))
        scout.set("autoCrossLineFromLeft", scout.boolfield('Y-13'))
        scout.set("autoCrossLineFromCenter", scout.boolfield('Z-13'))
        scout.set("autoCrossLineFromRight", scout.boolfield('AA-13'))
        scout.set("autoToSwitchFromLeft", scout.boolfield('Y-14'))
        scout.set("autoToSwitchFromCenter", scout.boolfield('Z-14'))
        scout.set("autoToSwitchFromRight", scout.boolfield('AA-14'))
        scout.set("autoDelToSwitchAcross", scout.boolfield('AB-14'))
        scout.set("autoDelToScaleAcross", scout.boolfield('AB-15'))
        scout.set("autoToScaleFromLeft", scout.boolfield('Y-15'))
        scout.set("autoToScaleFromCenter", scout.boolfield('Z-15'))
        scout.set("autoToScaleFromRight", scout.boolfield('AA-15'))
        scout.set("autoToXchangeFromLeft", scout.boolfield('Y-16'))
        scout.set("autoToXchangeFromCenter", scout.boolfield('Z-16'))
        scout.set("autoToXchangeFromRight", scout.boolfield('AA-16'))



        scout.set("Replay", 0)

#        sideAttempt = scout.boolfield('F-11') and not scout.boolfield('O-11')
#        centerAttempt = scout.boolfield('J-11') and not scout.boolfield('O-11')
#        sideSuccess = scout.boolfield('F-11') and scout.boolfield('O-11')
#        centerSuccess = scout.boolfield('J-11') and scout.boolfield('O-11')
#        scout.set("AutoSideAttempt", int(sideAttempt))
#        scout.set("AutoCenterAttempt", int(centerAttempt))
#        scout.set("AutoSideSuccess", int(sideSuccess))
#        scout.set("AutoCenterSuccess", int(centerSuccess))

        scout.submit()


#Takes an entry from the Scout database table and generates text for display on the team page. This page has 4 columns, currently used for auto, 2 teleop, and other (like fouls and end game)
def generateTeamText(e):
    text = {'auto': "", 'teleop1': "", 'teleop2': "", 'other': ""}
    text['auto'] += 'baseline, ' if e['autoCrossLine'] else ''
    text['auto'] += 'Switch try, ' if e['autoDelToSwitch'] else ''
    text['auto'] += 'Scale try, ' if e['autoDelToScale'] else ''
    text['auto'] += 'Exchange try, ' if e['autoDelToXchange'] else ''

    text['teleop1'] += str(
        e['NumDelToScale']) + 'x to scale, ' if e['NumDelToScale'] else ''

    text['teleop2'] += str(
        e['NumDelToSwitch']) + 'to switch, ' if e['NumDelToSwitch'] else ''

    text['other'] = 'Climb, ' if e['canClimb'] else ' '


    return text


#Takes an entry from the Scout database table and generates chart data. The fields in the returned dict must match the CHART_FIELDS definition at the top of this file
def generateChartData(e):
    dp = dict(CHART_FIELDS)
    dp["match"] = e['match']

    dp['NumDelToScale'] += e['NumDelToScale']
    dp['NumDelToSwitch'] += e['NumDelToSwitch']
    dp['NumDelToXchange'] += e['NumDelToXchange']

    return dp


#Takes a set of team numbers and a string indicating quals or playoffs and returns a prediction for the alliances score and whether or not they will achieve any additional ranking points
def predictScore(datapath, teams, level='quals'):
    conn = sql.connect(datapath)
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    ballScore = []
    endGame = []
    autoGears = []
    teleopGears = []
    for n in teams:
        average = cursor.execute('SELECT * FROM averages WHERE team=?',
                                 (n, )).fetchall()
        assert len(average) < 2
        if len(average):
            entry = average[0]
        else:
            entry = [0] * 8
        autoGears.append(entry[2])
        teleopGears.append(entry[3])
        ballScore.append((entry[5] + entry[6]))
        endGame.append((entry[7]))
    retVal = {'score': 0, 'gearRP': 0, 'fuelRP': 0}
    score = sum(ballScore[0:3]) + sum(endGame[0:3])
    if sum(autoGears[0:3]) >= 1:
        score += 60
    else:
        score += 40
    if sum(autoGears[0:3]) >= 3:
        score += 60
    elif sum(autoGears[0:3] + teleopGears[0:3]) >= 2:
        score += 40
    if sum(autoGears[0:3] + teleopGears[0:3]) >= 6:
        score += 40
    if sum(autoGears[0:3] + teleopGears[0:3]) >= 12:
        score += 40
        if level == 'playoffs':
            score += 100
        else:
            retVal['gearRP'] == 1
    if sum(ballScore[0:3]) >= 40:
        if level == 'playoffs':
            score += 20
        else:
            retVal['fuelRP'] == 1
    retVal['score'] = score
    return retVal


#Takes an entry from the Scout table and returns whether or not the entry should be flagged based on contradictory data.
def autoFlag(entry):
#    if (entry['AutoHighBalls']
#            or entry['TeleopHighBalls']) and (entry['AutoLowBalls']
#                                              or entry['AutoHighBalls']):
#        return 1
#    if entry['Hang'] and entry['FailedHang']:
#        return 1
    return 0


#Takes a list of Scout table entries and returns a nested dictionary of the statistical calculations (average, maxes, median, etc.) of each field in the AVERAGE_FIELDS definition
def calcTotals(entries):
    sums = dict(AVERAGE_FIELDS)
    noDefense = dict(AVERAGE_FIELDS)
    lastThree = dict(AVERAGE_FIELDS)
    noDCount = 0
    lastThreeCount = 0
    for key in sums:
        sums[key] = []
    #For each entry, add components to the running total if appropriate
    for i, e in enumerate(entries):
        sums['NumDelToScale'].append(e['NumDelToScale'])
        sums['NumDelToSwitch'].append(e['NumDelToSwitch'])
        sums['NumDelToXchange'].append(e['NumDelToXchange'])


        if i < 3:
            lastThree['NumDelToScale'] += e['NumDelToScale']
            lastThree['NumDelToSwitch'] += e['NumDelToSwitch']
            lastThree['NumDelToXchange'] += e['NumDelToXchange']
            lastThreeCount += 1

    #If there is data, average out the last 3 or less matches
    if (lastThreeCount):
        for key, val in lastThree.items():
            lastThree[key] = round(val / lastThreeCount, 2)

    #If there were matches where the team didn't play D, average those out
    if (noDCount):
        for key, val in noDefense.items():
            noDefense[key] = round(val / noDCount, 2)

    average = dict(AVERAGE_FIELDS)
    median = dict(AVERAGE_FIELDS)
    maxes = dict(AVERAGE_FIELDS)
    for key in sums:
        if key != 'team' and key != 'apr':
            average[key] = round(np.mean(sums[key]), 2)
            median[key] = round(np.median(sums[key]), 2)
            maxes[key] = round(np.max(sums[key]), 2)
    retVal = {
        'averages': average,
        'median': median,
        'maxes': maxes,
        'noDefense': noDefense,
        'lastThree': lastThree
    }

    #Calculate APRs. This is an approximate average points contribution to the match
    for key in retVal:
        apr = 100
#        apr = retVal[key]['autoballs'] + retVal[key]['teleopballs'] + retVal[key]['end']
#        if retVal[key]['autogear']:
#            apr += 20 * min(retVal[key]['autogear'], 1)
#        if retVal[key]['autogear'] > 1:
#            apr += (retVal[key]['autogear'] - 1) * 10
#
#            min(retVal[key]['teleopgear'], 2 - retVal[key]['autogear']) * 20,
#            0)
#        if retVal[key]['autogear'] + retVal[key]['teleopgear'] > 2:
#            apr += min(retVal[key]['teleopgear'] + retVal[key]['autogear'] - 2,
#                       4) * 10
#        if retVal[key]['autogear'] + retVal[key]['teleopgear'] > 6:
#            apr += min(retVal[key]['teleopgear'] + retVal[key]['autogear'] - 6,
#                       6) * 7
        apr = int(apr)
        retVal[key]['apr'] = apr

    return retVal

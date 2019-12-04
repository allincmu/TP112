import time
import urllib.request
import decimal
from tkinter import *

from bs4 import BeautifulSoup
# From https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
from cmu_112_graphics import *
from mechanize import Browser

############################## Helper Functions ###############################

# From: https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))




class Competition(object):
    competitions = dict()

    def __init__(self, html, name, dancer):
        self.recallPercentages = dict()
        self.dancer = dancer
        self.events = dict()
        startTime = time.time()
        self.name = name
        self.html = BeautifulSoup(html, features='html.parser')
        self.getEvents(dancer)
        self.number = None
        self.numberOfPossibleRecalls = dict()
        self.numberOfRecalls = dict()
        Competition.competitions[self.name] = self
        # self.getJudgeNumbers()
        endTime = time.time()
        # print('done comp ', endTime - startTime)

    def __repr__(self):
        # compStr = ''
        # for event in self.events:
        #     compStr += (str(self.events[event]) + '\n')
        return self.name

    def getEvents(self, dancer):
        for link in self.html.find_all('a'):
            evtName = link.string.strip()
            event = Event(link.get('href'), evtName, self.dancer)
            self.events[evtName] = event
            if event.level in dancer.eventsByLevel:
                dancer.eventsByLevel[event.level].append(event)
            else:
                dancer.eventsByLevel[event.level] = [event]

    # TODO: JUDGES LETTERS
    def getJudgeLetters(self):
        for event in self.events:
            eventLink = self.events[event]

    def getResultsTablesForComp(self):
        start = time.time()
        for eventName in self.events:
            event = self.events[eventName]
            event.getResultsTablesForEvent()
        end = time.time()
        print('done comp', end - start)

    def getRecallPercentagesForComp(self):
        for eventName in self.events:
            event = self.events[eventName]
            self.getRecallPercentagesForEvent(event)
        self.calculateRecallPercentages()
        for judge in self.recallPercentages:
            percentage = self.recallPercentages[judge]
            print(f'Judge {judge}: {percentage}%')

    def getRecallPercentagesForEvent(self, event):
        for heat in event.resultsTables:
            self.getRecallPercentagesForHeat(event, heat)

    def getRecallPercentagesForHeat(self, event, heat):
        resultTable = event.resultsTables[heat]
        for judgeIndex in range(len(resultTable[0])):
            judgeNumber = resultTable[0][judgeIndex]
            if judgeNumber.isnumeric():
                if judgeNumber in self.numberOfPossibleRecalls:
                    self.numberOfPossibleRecalls[judgeNumber] += 1
                else:
                    self.numberOfPossibleRecalls[judgeNumber] = 1
                recall = resultTable[1][judgeIndex]
                if recall:
                    if judgeNumber in self.numberOfRecalls:
                        self.numberOfRecalls[judgeNumber] += 1
                    else:
                        self.numberOfRecalls[judgeNumber] = 1

        print(self.numberOfRecalls)
        print(self.numberOfPossibleRecalls, '\n')

    def calculateRecallPercentages(self):
        for judge in self.numberOfPossibleRecalls:
            numPossibleRecalls = self.numberOfPossibleRecalls[judge]
            if judge not in self.numberOfRecalls:
                self.recallPercentages[judge] = 0
            else:
                numRecalls = self.numberOfRecalls[judge]
                recallRate = numRecalls / numPossibleRecalls
                recallPercentage = Competition.convertRateToPercent(recallRate)
                self.recallPercentages[judge] = recallPercentage

    @staticmethod
    def convertRateToPercent(rate):
        return roundHalfUp(rate * 100)


class Event(object):
    stdDances = ['V. Waltz', 'Tango', 'Foxtrot', 'Quickstep', 'Waltz']
    smoothDances = ['V. Waltz', 'Tango', 'Foxtrot', 'Waltz']
    latinDances = {'Cha Cha', 'Rumba', 'Jive', 'Samba', 'Paso Doble'}
    rhythmDances = {'Cha Cha', 'Rumba', 'Swing', 'Mambo', 'Bolero'}
    levels = {'Newcomer', 'Bronze', 'Silver', 'Gold'}

    def __init__(self, url, eventName, dancer):
        self.dancer = dancer
        self.eventName = eventName
        self.url = url
        content = urllib.request.urlopen(self.url).read()
        self.eventHTML = BeautifulSoup(content, features='html.parser')

        self.style = ''
        self.place = 0
        self.dance = []
        self.rounds = 0
        self.level = ''
        self.YCNPoints = 0
        self.resultsTables = dict()

        self.getStyleAndDance()
        self.getRounds()
        self.getPlace()
        self.getLevel()
        self.getYCNPoints()

    def __repr__(self):
        eventStr = f'Event Name: {self.eventName}'
        eventStr += f'\n\tURL: {self.url}'
        eventStr += f'\n\tLevel: {self.level}'
        eventStr += f'\n\tStyle: {self.style}'
        eventStr += f'\n\tDance: {self.dance}'
        eventStr += f'\n\tRounds: {self.rounds}'
        eventStr += f'\n\tPlace: {self.place}'
        eventStr += f'\n\tPoints: {self.YCNPoints}'
        return self.eventName

    @staticmethod
    def getRoundName(i):
        roundNames = ['Final', 'Semi-Final', 'Quarter-Final']
        if i <= 2:
            return roundNames[i]
        else:
            deno = 2 ** i
            return "1/" + str(deno) + "-Final"

    def getStyleAndDance(self):
        if 'Am.' in self.eventName:
            for dance in Event.smoothDances:
                if dance in self.eventName:
                    self.dance = [dance]
                    self.style = 'Smooth'
                    break

            for dance in Event.rhythmDances:
                if dance in self.eventName:
                    self.dance = [dance]
                    self.style = 'Rhythm'
                    break

        elif 'Intl.' in self.eventName:
            for dance in Event.stdDances:
                if dance in self.eventName:
                    self.dance = [dance]
                    self.style = 'Standard'
                    break

            for dance in Event.latinDances:
                if dance in self.eventName:
                    self.dance = [dance]
                    self.style = 'Latin'
                    break

        elif 'Standard' in self.eventName:
            self.style = 'Standard'

        elif 'Smooth' in self.eventName:
            self.style = 'Smooth'

        elif 'Latin' in self.eventName:
            self.style = 'Latin'

        elif 'Rhythm' in self.eventName:
            self.style = 'Rhythm'

        if self.dance == []:
            self.getDanceFromEventPage()

    def getDanceFromEventPage(self):
        dances = self.eventHTML.find_all('td', attrs={'class': 'h3'})[0:-1]
        for dance in dances:
            dance = str(dance)
            if self.style == 'Standard':
                for danceName in Event.stdDances:
                    if danceName in dance:
                        self.dance += [danceName]
            elif self.style == 'Smooth':
                for danceName in Event.smoothDances:
                    if danceName in dance:
                        self.dance += [danceName]
            elif self.style == 'Latin':
                for danceName in Event.latinDances:
                    if danceName in dance:
                        self.dance += [danceName]
            elif self.style == 'Rhythm':
                for danceName in Event.rhythmDances:
                    if danceName in dance:
                        self.dance += [danceName]

    def getLevel(self):
        for level in Event.levels:
            if level in self.eventName:
                self.level = level

    def getRounds(self):
        self.rounds = len(self.eventHTML.find_all('option'))
        if self.rounds == 0:
            self.rounds = 1

        if self.rounds == 0:
            print('error')

    def getPlace(self):
        endIndex = self.eventName.find(')')
        self.place = int(self.eventName[0:endIndex])

    def getYCNPoints(self):
        if self.rounds == 2:
            if self.place <= 3:
                self.YCNPoints = 4 - self.place
        elif self.rounds > 2:
            if self.place <= 3:
                self.YCNPoints = 4 - self.place
            elif self.place > 3 and self.place <= 6:
                self.YCNPoints = 1
        else:
            self.YCNPoints = 0

    def getCoupleNumber(self, eventPage):
        tableElements = eventPage.find_all('td')
        for element in tableElements:
            linksInTableElements = element.find_all('a')
            for link in linksInTableElements:
                if link.string == self.dancer.fullName:
                    self.number = element.previous_sibling.string

    def getResultsTablesForEvent(self):
        starttime = time.time()
        maxRound = self.rounds - 1
        for i in range(maxRound, 0, -1):
            roundName = Event.getRoundName(i)
            resultTable = self.getResultTableForRound(i, maxRound)
            if len(resultTable) == 2:
                self.resultsTables[roundName] = resultTable
            # print(self.eventName, roundName, resultTable)
            if resultTable[-1][-1] != 'R':
                break
        endtime = time.time()
        print('done results tables ', endtime - starttime)

    def getRoundPage(self, i):
        br = Browser()
        br.addheaders = [('User-agent', 'Firefox')]
        br.open(self.url)
        if i != None:
            br.select_form(name="selectRound")
            br['selCount'] = [str(i)]
            br.submit()
        else:
            i = 0
        soup = BeautifulSoup(br.response().read(), features='html.parser')
        return soup

    def getResultTableForRound(self, i, maxRound):
        roundPage = self.getRoundPage(i)
        if i == maxRound:
            self.getCoupleNumber(roundPage)

        # Consulted: https://stackoverflow.com/questions/23377533/ +
        #       python-beautifulsoup-parsing-table
        data = []
        table = roundPage.find('table', attrs={'class': 't1n'})
        rows = table.find_all('tr')
        for rowIndex in range(1, len(rows)):
            columns = []
            row = rows[rowIndex]
            if rowIndex == 1:
                rowElements = row.find_all('td')
                for element in rowElements:
                    columns += [element.text.strip()]
                data.append([element for element in columns])
            else:
                rowElements = row.find_all('td')
                competitorNumber = rowElements[0].text.strip()
                if competitorNumber != self.number:
                    continue
                for elementIndex in range(len(rowElements)):
                    element = rowElements[elementIndex].text.strip()
                    columns += [element]
                if columns != []:
                    data = Event.truncateExcessData(columns, data)
        return data

    @staticmethod
    def truncateExcessData(columns, data):
        colsToBeAdded = []
        for i in range(len(data[0])):
            colsToBeAdded.append(columns[i])
        data.append(colsToBeAdded)
        return data


class Dancer(object):
    def __init__(self, firstName, lastName):
        self.firstName = firstName
        self.lastName = lastName
        self.fullName = self.firstName + ' ' + self.lastName
        self.resultsURL = (f'http://results.o2cm.com/individual.asp?' +
                           f'szLast={lastName}&szFirst={firstName}')
        self.eventsByLevel = dict(Gold=[], Silver=[], Bronze=[], Newcomer=[])
        self.getCompetitions()
        self.newcomerYCN = dict()
        self.bronzeYCN = dict()
        self.silverYCNs = dict()
        self.goldYCNs = dict()
        self.ycnDict = dict()
        self.createYCNDict(self.newcomerYCN)
        self.createYCNDict(self.bronzeYCN)
        self.createYCNDict(self.silverYCNs)
        self.createYCNDict(self.goldYCNs)

        self.getYCNPoints()

    def getCompetitions(self):
        content = urllib.request.urlopen(self.resultsURL).read()
        self.resultsBS = BeautifulSoup(content, features='html.parser')
        results = self.resultsBS.find_all('table')[0]
        self.resultsPageHTML = self.resultsBS.prettify()

        self.competitions = []
        self.competitionList = []
        for competition in results.find_all('b'):
            self.competitions.append(competition.string)

        for i in range(len(self.competitions)):
            compName = self.competitions[i]
            if i < len(self.competitions) - 1:
                nextCompName = self.competitions[i + 1]
                endIndex = self.resultsPageHTML.find(nextCompName)
            else:
                endIndex = len(self.resultsPageHTML) - 1
            startIndex = self.resultsPageHTML.find(compName)
            compHTML = self.resultsPageHTML[startIndex:endIndex]
            self.competitionList.append(Competition(compHTML, compName, self))

    def createYCNDict(self, d):
        d['Latin'] = dict()
        d['Rhythm'] = dict()
        d['Standard'] = dict()
        d['Smooth'] = dict()

        for style in d:
            d[style]['Total'] = 0
        for dance in Event.latinDances:
            d['Latin'][dance] = 0
        for dance in Event.rhythmDances:
            d['Rhythm'][dance] = 0
        for dance in Event.stdDances:
            d['Standard'][dance] = 0
        for dance in Event.smoothDances:
            d['Smooth'][dance] = 0

    def getYCNPoints(self):
        self.getYCNForLevel('Gold', self.goldYCNs, None)
        self.getYCNForLevel('Silver', self.silverYCNs, self.goldYCNs)
        self.getYCNForLevel('Bronze', self.bronzeYCN, self.silverYCNs)
        self.getYCNForLevel('Newcomer', self.newcomerYCN, self.bronzeYCN)

        self.ycnDict['Newcomer'] = self.newcomerYCN
        self.ycnDict['Bronze'] = self.bronzeYCN
        self.ycnDict['Silver'] = self.silverYCNs
        self.ycnDict['Gold'] = self.goldYCNs

    def getYCNForLevel(self, level, currYCNDict, prevYCNDict):
        if prevYCNDict is not None:
            for style in prevYCNDict:
                for dance in prevYCNDict[style]:
                    currYCNDict[style][dance] = prevYCNDict[style][dance] * 2

        for event in self.eventsByLevel[level]:
            for dance in event.dance:
                style = event.style
                if style not in currYCNDict:
                    currYCNDict[style] = dict()
                    currYCNDict[style]['Total'] = 0

                if dance in currYCNDict[style]:
                    currYCNDict[style][dance] += event.YCNPoints
                else:
                    currYCNDict[style][dance] = event.YCNPoints

                currYCNDict[style]['Total'] += event.YCNPoints

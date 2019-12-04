import time
import urllib.request
from tkinter import *

from bs4 import BeautifulSoup
# From https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
from cmu_112_graphics import *
from mechanize import Browser

# From: https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
import decimal


def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))


###############################################################################
# Helper function for print2dList.
# This finds the maximum length of the string
# representation of any item in the 2d list
def maxItemLength(a):
    maxLen = 0
    rows = len(a)
    cols = len(a[0])
    for row in range(rows):
        for col in range(cols):
            maxLen = max(maxLen, len(str(a[row][col])))
    return maxLen


# Because Python prints 2d lists on one row,
# we might want to write our own function
# that prints 2d lists a bit nicer.
def print2dList(a):
    if (a == []):
        # So we don't crash accessing a[0]
        print([])
        return
    rows = len(a)
    cols = len(a[0])
    fieldWidth = maxItemLength(a)
    print("[ ", end="")
    for row in range(rows):
        if (row > 0): print("\n  ", end="")
        print("[ ", end="")
        for col in range(cols):
            if (col > 0): print(", ", end="")
            # The next 2 lines print a[row][col] with the given fieldWidth
            formatSpec = "%" + str(fieldWidth) + "s"
            print(formatSpec % str(a[row][col]), end="")
        print(" ]", end="")
    print("]")


#################################################################################


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
        compStr = ''
        for event in self.events:
            compStr += (str(self.events[event]) + '\n')
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

        print2dList(resultTable)
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


class ElliottToy(object):
    def __init__(self, mode):
        self.ycnDict = {
            'Newcomer': {
                'Latin': {'Total': 126, 'Samba': 30, 'Cha Cha': 38, 'Jive': 20,
                          'Rumba': 38, 'Paso Doble': 0},
                'Rhythm': {'Total': 22, 'Cha Cha': 7, 'Swing': 6, 'Bolero': 0,
                           'Rumba': 5, 'Mambo': 4},
                'Standard': {'Total': 222, 'V. Waltz': 0, 'Tango': 38,
                             'Foxtrot': 58, 'Quickstep': 74,
                             'Waltz': 52},
                'Smooth': {'Total': 122, 'V. Waltz': 2, 'Tango': 31,
                           'Foxtrot': 30, 'Waltz': 59}},
            'Bronze': {
                'Latin': {'Total': 63, 'Samba': 15, 'Cha Cha': 19, 'Jive': 10,
                          'Rumba': 19, 'Paso Doble': 0},
                'Rhythm': {'Total': 10, 'Cha Cha': 3, 'Swing': 3, 'Bolero': 0,
                           'Rumba': 2, 'Mambo': 2},
                'Standard': {'Total': 111, 'V. Waltz': 0, 'Tango': 19,
                             'Foxtrot': 29, 'Quickstep': 37,
                             'Waltz': 26},
                'Smooth': {'Total': 59, 'V. Waltz': 1, 'Tango': 14,
                           'Foxtrot': 15, 'Waltz': 29}},
            'Silver': {
                'Latin': {'Total': 23, 'Samba': 7, 'Cha Cha': 6, 'Jive': 4,
                          'Rumba': 6, 'Paso Doble': 0},
                'Rhythm': {'Total': 0, 'Cha Cha': 0, 'Swing': 0, 'Bolero': 0,
                           'Rumba': 0, 'Mambo': 0},
                'Standard': {'Total': 44, 'V. Waltz': 0, 'Tango': 8,
                             'Foxtrot': 13, 'Quickstep': 14, 'Waltz': 9},
                'Smooth': {'Total': 28, 'V. Waltz': 0, 'Tango': 7, 'Foxtrot': 7,
                           'Waltz': 14}},
            'Gold': {'Latin': {'Total': 4, 'Samba': 1, 'Cha Cha': 1, 'Jive': 1,
                               'Rumba':
                                   1, 'Paso Doble': 0},
                     'Rhythm': {'Total': 0, 'Cha Cha': 0, 'Swing': 0,
                                'Bolero': 0, 'Rumba': 0, 'Mambo': 0},
                     'Standard': {'Total': 16, 'V. Waltz': 0, 'Tango': 3,
                                  'Foxtrot': 5, 'Quickstep': 5, 'Waltz': 3},
                     'Smooth': {'Total': 8, 'V. Waltz': 0, 'Tango': 2,
                                'Foxtrot': 2, 'Waltz': 4}}}
        self.competitionList = ['02-16-19 - The UPenn Classic',
                                '10-26-19 - Keystone Dancesport Classic',
                                '11-23-19 - OSB Collegiate Challenge 2019']


class SplashScreenMode(Mode):
    def appStarted(mode):
        mode.msg = 'Press any key to enter a dancer!'
        mode.dancerSet = False

    def resetApp(mode):
        Competition.competitions = None
        mode.dancerSet = False
        mode.msg = 'Press any key to enter a dancer!'

    def keyPressed(mode, event):
        if event.key == 'Tab':
            mode.app.setActiveMode(mode.app.testUsingET)
            return

        firstName = mode.app.getUserInput("Competitor's First Name: ")
        if (firstName == None):
            mode.app.showMessage('You canceled!')
        else:
            lastName = mode.app.getUserInput("Competitor's Last Name: ")
            if (lastName == None):
                mode.app.showMessage('You canceled!')
            else:
                firstName = firstName.title()
                lastName = lastName.title()
                mode.name = firstName + ' ' + lastName
                mode.msg = f'Pulling results for {firstName} {lastName}... \n'
                mode.msg += 'Please Wait. This may take a few moments.'
                mode.dancerSet = True
                mode.firstName = firstName
                mode.lastName = lastName

    def timerFired(mode):
        if mode.dancerSet == True:
            mode.app.competitor = Dancer(mode.firstName, mode.lastName)
            if mode.app.competitor.competitions == ['No Results on File']:
                mode.app.showMessage(f'No Results on O2CM for {mode.name}.\n' +
                                     'Please re-enter dancer name.')
                mode.resetApp()
                return
            mode.app.setActiveMode(mode.app.menuMode)

    def redrawAll(mode, canvas):
        fontTitle = 'Arial 30 bold'
        fontMsg = 'Arial 20 bold'
        canvas.create_text(mode.width / 2, 150,
                           text='Ballroom YCN Points Calculator',
                           font=fontTitle)
        canvas.create_text(mode.width / 2, 190, text='and Statistics Program',
                           font=fontTitle)
        canvas.create_text(mode.width / 2, 300, text=mode.msg, font=fontMsg)


class YCNMode(Mode):
    def appStarted(mode):
        mode.rows = 28
        mode.cols = 6
        mode.app.margin = 50

        mode.styleOrder = ['Smooth', 'Standard', 'Rhythm', 'Latin']

        smoothDances = ['', 'Waltz', 'Tango', 'Foxtrot', 'V. Waltz', 'Total',
                        '']
        stdDances = ['Waltz', 'Quickstep', 'Tango', 'Foxtrot', 'V. Waltz',
                     'Total', '']
        rhythmDances = ['Cha Cha', 'Rumba', 'Swing', 'Mambo', 'Bolero', 'Total',
                        '']
        latinDances = ['Cha Cha', 'Rumba', 'Samba', 'Jive', 'Paso Doble',
                       'Total', '']

        mode.styleAndDanceDict = dict()
        mode.styleAndDanceDict['Smooth'] = smoothDances
        mode.styleAndDanceDict['Standard'] = stdDances
        mode.styleAndDanceDict['Rhythm'] = rhythmDances
        mode.styleAndDanceDict['Latin'] = latinDances

        mode.dances = smoothDances + stdDances + rhythmDances + latinDances

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.menuMode)

    # From https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCellBounds(mode, row, col):
        gridWidth = mode.app.width - 2 * mode.app.margin
        gridHeight = mode.app.height - 2 * mode.app.margin
        columnWidth = gridWidth / mode.cols
        rowHeight = gridHeight / mode.rows
        x0 = mode.app.margin + col * columnWidth
        x1 = mode.app.margin + (col + 1) * columnWidth
        y0 = mode.app.margin + row * rowHeight
        y1 = mode.app.margin + (row + 1) * rowHeight
        return (x0, y0, x1, y1)

    def redrawAll(mode, canvas):
        canvas.create_text(mode.app.width / 2, mode.app.margin / 2,
                           text='YCN Points Tally', font='Arial 25 bold')

        text = ('Totals in Red indicate that a dancer has pointed out of ' +
                'that style and level. Empty cells indicate that no points ' +
                'have been earned.\n')
        text += 'Press any key to return to the Main Menu'
        canvas.create_text(mode.app.width / 2,
                           mode.app.height - mode.app.margin / 2,
                           text=text, fill='red')

        for row in range(mode.rows):
            if row in [1, 7, 14, 21]: continue

            if row == 0:
                fill = 'light green'
            else:
                fill = None
            for col in range(mode.cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill=fill)
        mode.setUpHeaders()
        mode.drawTableXHeaders(canvas)
        mode.drawTableYHeaders(canvas)
        mode.drawDances(canvas)
        mode.addYCNPointsToTable(canvas)

    def setUpHeaders(mode):

        mode.xheaders = ['Style', 'Dance', 'Newcomer', 'Bronze', 'Silver',
                         'Gold']
        mode.yheaders = [('Smooth', 2), ('Standard', 8),
                         ('Rhythm', 15), ('Latin', 22)]

    def drawTableXHeaders(mode, canvas):
        font = 'Bold'
        for col in range(mode.cols):
            row = 0
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2,
                               text=mode.xheaders[col], font=font)

    def drawTableYHeaders(mode, canvas):
        font = 'bold'
        for style, row in mode.yheaders:
            col = 0
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2,
                               text=style, font=font)

    def drawDances(mode, canvas):
        col = 1
        startRow = 1
        for row in range(startRow, mode.rows):
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            text = mode.dances[row - 1]
            font = 'Arial 10'
            if text == 'Total':
                font = 'Arial 10 bold'
            canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2,
                               text=text, font=font)

    def addYCNPointsToTable(mode, canvas):
        levelOrder = ['Newcomer', 'Bronze', 'Silver', 'Gold']
        col = 2
        row = 1
        for level in levelOrder:
            for style in mode.styleOrder:
                for dance in mode.styleAndDanceDict[style]:
                    if dance == '':
                        row += 1
                        continue

                    points = mode.app.competitor.ycnDict[level][style][dance]
                    if points != 0:
                        font = 'Arial 10'
                        fill = 'black'
                        if dance == 'Total':
                            font = 'Arial 10 bold'
                            if points >= 7: fill = 'red'
                        (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                        canvas.create_text(x1 + (x0 - x1) / 2,
                                           y1 + (y0 - y1) / 2,
                                           text=points, font=font,
                                           fill=fill)
                    row += 1
            col += 1
            row = 1


# Subclass of YCNMode
class YCNModeCondensed(YCNMode):
    def appStarted(mode):
        mode.rows = 5
        mode.cols = 5
        mode.app.margin = 50

        mode.styleOrder = ['Smooth', 'Standard', 'Rhythm', 'Latin']

    def redrawAll(mode, canvas):
        canvas.create_text(mode.app.width / 2, mode.app.margin / 2,
                           text='YCN Points Tally (Condensed)',
                           font='Arial 25 bold')

        text = ('Totals in Red indicate that a dancer has pointed out of ' +
                'that style and level. Empty cells indicate that no points ' +
                'have been earned.\n')
        text += 'Press any key to return to the Main Menu'
        canvas.create_text(mode.app.width / 2,
                           mode.app.height - mode.app.margin / 2,
                           text=text, fill='red')

        for row in range(mode.rows):
            if row == 0:
                fill = 'light blue'
            else:
                fill = None
            for col in range(mode.cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill=fill)

        mode.setUpHeaders()
        mode.drawTableXHeaders(canvas)  # Inherited from superclass
        mode.drawTableYHeaders(canvas)
        mode.addYCNPointsToTable(canvas)

    def setUpHeaders(mode):
        mode.xheaders = ['Style', 'Newcomer', 'Bronze', 'Silver', 'Gold']
        mode.yheaders = ['Smooth', 'Standard', 'Rhythm', 'Latin']

    def drawTableYHeaders(mode, canvas):
        font = 'Bold'
        for row in range(1, mode.rows):
            col = 0
            style = mode.yheaders[row - 1]
            # getCellBounds(row, col) inherited from superclass
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2,
                               text=style, font=font)

    def addYCNPointsToTable(mode, canvas):
        levelOrder = ['Newcomer', 'Bronze', 'Silver', 'Gold']
        col = 1
        row = 1
        for level in levelOrder:
            for style in mode.styleOrder:
                points = mode.app.competitor.ycnDict[level][style]['Total']
                if points != 0:
                    fill = 'black'
                    font = 'Arial 20 bold'
                    if points >= 7: fill = 'red'
                    (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                    canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2,
                                       text=points, font=font,
                                       fill=fill)
                row += 1
            col += 1
            row = 1


class testUsingET(Mode):
    def appStarted(mode):
        mode.app.competitor = ElliottToy(mode)
        mode.app.setActiveMode(mode.app.menuMode)


class MenuMode(Mode):
    def keyPressed(mode, event):
        if event.key == '1':
            mode.app.setActiveMode(mode.app.splashScreenMode)
            mode.app.splashScreenMode.resetMode()
        elif event.key == '2':
            mode.app.setActiveMode(mode.app.ycnMode)
        elif event.key == '3':
            mode.app.setActiveMode(mode.app.ycnModeCondensed)
        elif event.key == '4':
            mode.app.setActiveMode(mode.app.compPicker)
            mode.app.compPicker.resetMode()

        # More will be added later

    def redrawAll(mode, canvas):
        menuText = '\t\tMenu \n\n'
        menuText += 'Press 1 - To return to the start screen\n'
        menuText += 'Press 2 - To view to the YCN points chart (expanded)\n'
        menuText += 'Press 3 - To view to the YCN points chart (condensed)\n'
        menuText += 'Press 4 - To view to the Recall Rate Graph\n'
        menuText += 'Press 5 - To view to the Competetive Summary\n'
        menuText += 'Press 6 - To view to the Raw Results\n'

        canvas.create_text(mode.app.width / 2, mode.app.height / 2,
                           text=menuText, font='Arial 20')


class CompPicker(Mode):
    def appStarted(mode):
        mode.resetMode()

    def resetMode(mode):
        mode.compSelected = False
        mode.getMsg()

    def timerFired(mode):
        if mode.compSelected:
            mode.compSelection.getResultsTablesForComp()
            mode.app.recallGraphMode.compSelection = mode.compSelection
            mode.app.setActiveMode(mode.app.recallGraphMode)
            mode.app.recallGraphMode.resetMode()

    def keyPressed(mode, event):
        compIndex = event.key
        numComps = mode.app.competitor.competitionList

        if mode.compSelected:
            return

        elif compIndex.isalpha():
            mode.app.setActiveMode(mode.app.menuMode)

        elif compIndex.isnumeric() and int(compIndex) < len(numComps):
            compIndex = int(compIndex)
            mode.compSelection = mode.app.competitor.competitionList[compIndex]
            mode.compSelected = True

        else:
            mode.app.showMessage(f'Invalid Entry: \'{compIndex}\' \n' +
                                 'There is no competition associated with ' +
                                 f'\'{compIndex}\'')
        mode.getMsg()

    def redrawAll(mode, canvas):
        font = 'Arial 20'
        canvas.create_text(mode.app.width / 2, mode.app.height / 2,
                           text=mode.msg, font=font)

    def getMsg(mode):
        if mode.compSelected:
            mode.msg = f'Pulling recall data at {mode.compSelection} \n'
            mode.msg += 'Please Wait... This will take several minutes.'

        else:
            mode.msg = ('Please enter the number of the competition to ' +
                        'generate a recall rate graph: \n')
            for i in range(len(mode.app.competitor.competitionList)):
                compName = str(mode.app.competitor.competitionList[i])
                mode.msg += ('\tPress ' + str(i) + ':\t' + compName + '\n')


# TODO: implement recall graph mode
class RecallGraphMode(Mode):

    def appStarted(mode):
        mode.resetMode()

    def resetMode(mode):
        mode.compSelection.getRecallPercentagesForComp()
        numJudges = len(mode.compSelection.recallPercentages)
        mode.rows = 101
        mode.cols = numJudges * 2 + 1
        mode.app.margin = 50

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.compPicker)
        mode.app.compPicker.resetMode()

    # From https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    # With slight edits
    def getCellBounds(mode, row, col):
        gridWidth = mode.app.width - 2 * mode.app.margin
        gridHeight = mode.app.height - 2 * mode.app.margin
        columnWidth = gridWidth / mode.cols
        rowHeight = gridHeight / (mode.rows + 5)
        x0 = mode.app.margin + col * columnWidth
        x1 = mode.app.margin + (col + 1) * columnWidth
        y0 = mode.app.margin + row * rowHeight
        y1 = mode.app.margin + (row + 1) * rowHeight
        if row == 101:
            y1 = mode.app.margin + (row + 4) * rowHeight
        return (x0, y0, x1, y1)

    def redrawAll(mode, canvas):
        canvas.create_text(mode.app.width / 2, mode.app.margin / 2,
                           text='YCN Points Tally', font='Arial 25 bold')

        mode.drawBars(canvas)

    def drawBars(mode, canvas):
        colIndex = 1
        for judge in mode.compSelection.recallPercentages:
            percentage = mode.compSelection.recallPercentages[judge]
            barYBottom = 100
            barYTop = barYBottom - percentage
            for rowIndex in range(barYBottom, barYTop + 1, -1):
                (x0, y0, x1, y1) = mode.getCellBounds(rowIndex, colIndex)
                canvas.create_rectangle(x0, y0, x1, y1, fill = 'light blue')
            mode.drawJudgeName(canvas, colIndex, judge)
            colIndex += 2

    def drawJudgeName(mode, canvas, colIndex, judge):
        nameRowIndex = 101
        (x0, y0, x1, y1) = mode.getCellBounds(nameRowIndex, colIndex)
        canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2, text = judge)







# From https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
# With slight edits
class O2CMApp(ModalApp):
    def appStarted(app):
        app.splashScreenMode = SplashScreenMode()
        app.ycnMode = YCNMode()
        app.ycnModeCondensed = YCNModeCondensed()
        app.testUsingET = testUsingET()
        app.menuMode = MenuMode()
        app.compPicker = CompPicker()
        app.recallGraphMode = RecallGraphMode()
        app.setActiveMode(app.splashScreenMode)
        app.timerDelay = 500


app = O2CMApp(width=1000, height=650)

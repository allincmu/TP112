# From https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
from cmu_112_graphics import *
from tkinter import *
from bs4 import BeautifulSoup
from mechanize import Browser
import urllib.request, time, random


class Competition(object):

    competitions = dict()
    def __init__(self, html, name, Dancer):
        starttime = time.time()
        self.name = name
        self.html = BeautifulSoup(html, features='html.parser')
        self.getEvents(html, Dancer)
        self.number = None
        Competition.competitions[self.name] = self
        # self.getJudgeNumbers()
        endtime = time.time()
        print('done comp ', endtime-starttime)
    
    def getEvents(self, html, Dancer):
        self.eventsURL = dict()
        for link in self.html.find_all('a'):
            evtName = link.string.strip()
            event = Event(link.get('href'), evtName)
            self.eventsURL[evtName] = event
            if event.level in Dancer.eventsByLevel:
                Dancer.eventsByLevel[event.level].append(event)
            else:
                Dancer.eventsByLevel[event.level] = [event]
    
    # def getJudgeNumbers(self):
    #     for event in eventsURL:
    #         eventLink = eventsURL[event]

            
    
    def __repr__(self):
        compStr = ''
        for Event in self.eventsURL:
            compStr += (str(self.eventsURL[Event]) + '\n')
        return self.name


    def addEvent(self, Event):
        self.events.append(Event)

class Event(object):

    stdDances = ['V. Waltz', 'Tango', 'Foxtrot', 'Quickstep', 'Waltz']
    smoothDances = ['V. Waltz', 'Tango', 'Foxtrot', 'Waltz']
    latinDances = set(['Cha Cha', 'Rumba', 'Jive', 'Samba', 'Paso Doble'])
    rhythmDances = set(['Cha Cha', 'Rumba', 'Swing','Mambo', 'Bolero'])
    levels = set(['Newcomer', 'Bronze', 'Silver', 'Gold'])

    def __init__(self, url, eventName):
        starttime = time.time()
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

        # self.getResultsTables()
        
        endtime = time.time()
   
    
    def getRoundName(self, i):
        roundNames = ['Final', 'Semi-Final', 'Quarter-Final']
        if i <= 2:
            return roundNames[i]
        else:
            deno = 2**i
            return "1/" + str(deno) + "-Final"

    def getResultsTables(self):
        starttime = time.time()
        for i in range(1, self.rounds):
            roundName = self.getRoundName(i)
            resultTable = self.getResultTable(i)
            self.resultsTables[roundName] = resultTable
        endtime = time.time()
        print('done results tables ', endtime-starttime)
        print(self.resultsTables)
        
    def getResultTable(self, i):
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
        
        # From: https://stackoverflow.com/questions/23377533/ +
        #       python-beautifulsoup-parsing-table
        data = []
        table = soup.find('table', attrs={'class':'t1n'})
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols])
        
        return data
    
    # # From ___________________________________________________________________________________________________
    # # With slight edits
    # def print2dList(self, a, compact = False, number = 120):
    #     foundNum = False
    #     a.pop(0)
    #     if (a == []):
    #         # So we don't crash accessing a[0]
    #         print([])
    #         return
    #     rows = len(a)
    #     cols = len(a[0])
    #     fieldWidth = maxItemLength(a)
    #     print("[ ", end="")
    #     for row in range(rows):
    #         if (row > 0):
    #             if compact == True:
    #                 if a[row][0] != str(number): 
    #                     foundNum = True
    #                     continue
    #             print("\n  ", end="")
    #         print("[ ", end="")
    #         for col in range(cols):
    #             if (col > 0): print(", ", end="")
    #             # The next 2 lines print a[row][col] with the given fieldWidth
    #             formatSpec = "%" + str(fieldWidth) + "s"
    #             print(formatSpec % str(a[row][col]), end="")
    #         print(" ]", end="")
    #         if foundNum == True:
    #             break
    #     print("]")

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
        dances = self.eventHTML.find_all('td', attrs={'class':'h3'})[0:-1]
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
                self.YCNPoints = 4-self.place
        elif self.rounds > 2:
            if self.place <= 3:
                self.YCNPoints = 4-self.place
            elif self.place > 3 and self.place <= 6:
                self.YCNPoints = 1
        else:
            self.YCNPoints = 0    

    # might implement later
    def getDCDIPoints(self):
        pass
        

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

class Dancer(object):
    def __init__(self, firstName, lastName):
        self.firstName = firstName
        self.lastName = lastName
        self.resultsURL = (f'http://results.o2cm.com/individual.asp?' +
                           f'szLast={lastName}&szFirst={firstName}')
        self.eventsByLevel = {'Gold':[], 'Silver':[], 'Bronze':[], 'Newcomer':[]}
        self.getCompetitions()
        self.newcomerYCNs = dict()
        self.bronzeYCNs = dict()
        self.silverYCNs = dict()
        self.goldYCNs = dict()
        self.ycnDict = dict()
        self.createYCNDict(self.newcomerYCNs)
        self.createYCNDict(self.bronzeYCNs)
        self.createYCNDict(self.silverYCNs)
        self.createYCNDict(self.goldYCNs)

        self.getYCNPoints()
        print(self.ycnDict)
        
        
    
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
            if i < len(self.competitions)-1:
                nextCompName = self.competitions[i+1]
                endIndex = self.resultsPageHTML.find(nextCompName)
            else:
                endIndex = len(self.resultsPageHTML)-1
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
        self.getGoldYCN()
        self.getSilverYCN()
        self.getBronzeYCN()
        self.getNewcomerYCN()

        self.ycnDict['Newcomer'] = self.newcomerYCNs
        self.ycnDict['Bronze'] = self.bronzeYCNs
        self.ycnDict['Silver'] = self.silverYCNs
        self.ycnDict['Gold'] = self.goldYCNs  
    
    def getGoldYCN(self):
        for goldEvent in self.eventsByLevel['Gold']:          
            for dance in goldEvent.dance:
                style = goldEvent.style
                if style not in self.goldYCNs:
                    self.goldYCNs[style] = dict()
                    self.goldYCNs[style]['Total'] = 0

                if dance in self.goldYCNs[style]:
                    self.goldYCNs[style][dance] += goldEvent.YCNPoints
                else:
                    self.goldYCNs[style][dance] = goldEvent.YCNPoints
                
                self.goldYCNs[style]['Total'] += goldEvent.YCNPoints

    def getSilverYCN(self):

        for style in self.goldYCNs:
            for dance in self.goldYCNs[style]:
                self.silverYCNs[style][dance] = self.goldYCNs[style][dance]*2


        for silverEvent in self.eventsByLevel['Silver']:
            for dance in silverEvent.dance:
                style = silverEvent.style
                if style not in self.silverYCNs:
                    self.silverYCNs[style] = dict()
                    self.silverYCNs[style]['Total'] = 0

                if dance in self.silverYCNs[style]:
                    self.silverYCNs[style][dance] += silverEvent.YCNPoints
                else:
                    self.silverYCNs[style][dance] = silverEvent.YCNPoints
                
                self.silverYCNs[style]['Total'] += silverEvent.YCNPoints
                


    def getBronzeYCN(self):
        for style in self.silverYCNs:
            for dance in self.silverYCNs[style]:
                self.silverYCNs[style][dance]
                self.bronzeYCNs[style][dance] = self.silverYCNs[style][dance]*2

        for bronzeEvent in self.eventsByLevel['Bronze']:
            
            for dance in bronzeEvent.dance:
                style = bronzeEvent.style
                if style not in self.bronzeYCNs:
                    self.bronzeYCNs[style] = dict()
                    self.bronzeYCNs[style]['Total'] = 0

                if dance in self.bronzeYCNs[style]:
                    self.bronzeYCNs[style][dance] += bronzeEvent.YCNPoints
                else:
                    self.bronzeYCNs[style][dance] = bronzeEvent.YCNPoints
                
                self.bronzeYCNs[style]['Total'] += bronzeEvent.YCNPoints
    
    def getNewcomerYCN(self):
        for style in self.bronzeYCNs:
            for dance in self.bronzeYCNs[style]:
                self.bronzeYCNs[style][dance]
                self.newcomerYCNs[style][dance] = self.bronzeYCNs[style][dance]*2

        for newcomerEvent in self.eventsByLevel['Newcomer']:
            
            for dance in newcomerEvent.dance:
                style = newcomerEvent.style
                if style not in self.newcomerYCNs:
                    self.newcomerYCNs[style] = dict()
                    self.newcomerYCNs[style]['Total'] = 0

                if dance in self.newcomerYCNs[style]:
                    self.newcomerYCNs[style][dance] += newcomerEvent.YCNPoints
                else:
                    self.newcomerYCNs[style][dance] = newcomerEvent.YCNPoints
                
                self.newcomerYCNs[style]['Total'] += newcomerEvent.YCNPoints

class ElliottToy(object):
    def __init__(self, mode):
        self.ycnDict = {'Newcomer': {'Latin': {'Total': 126, 'Samba': 30, 'Cha Cha': 38, 'Jive': 20, 'Rumba': 38, 'Paso Doble': 0}, 'Rhythm': {'Total': 22, 'Cha Cha': 7, 'Swing': 6, 'Bolero': 0, 'Rumba': 5, 'Mambo': 4}, 'Standard': {'Total': 222, 'V. Waltz': 0, 'Tango': 38, 'Foxtrot': 58, 'Quickstep': 74, 'Waltz': 52}, 'Smooth': {'Total': 122, 'V. Waltz': 2, 'Tango': 31, 'Foxtrot': 30, 'Waltz': 59}}, 'Bronze': {'Latin': {'Total': 63, 'Samba': 15, 'Cha Cha': 19, 'Jive': 10, 'Rumba': 19, 'Paso Doble': 0}, 'Rhythm': {'Total': 10, 'Cha Cha': 3, 'Swing': 3, 'Bolero': 0, 'Rumba': 2, 'Mambo': 2}, 'Standard': {'Total': 111, 'V. Waltz': 0, 'Tango': 19, 'Foxtrot': 29, 'Quickstep': 37, 'Waltz': 26}, 'Smooth': {'Total': 59, 'V. Waltz': 1, 'Tango': 14, 'Foxtrot': 15, 'Waltz': 29}}, 'Silver': {'Latin': {'Total': 23, 'Samba': 7, 'Cha Cha': 6, 'Jive': 4, 'Rumba': 6, 'Paso Doble': 0}, 'Rhythm': {'Total': 0, 'Cha Cha': 0, 'Swing': 0, 'Bolero': 0, 'Rumba': 0, 'Mambo': 0}, 'Standard': {'Total': 44, 'V. Waltz': 0, 'Tango': 8, 'Foxtrot': 13, 'Quickstep': 14, 'Waltz': 9}, 'Smooth': {'Total': 28, 'V. Waltz': 0, 'Tango': 7, 'Foxtrot': 7, 'Waltz': 14}}, 'Gold': {'Latin': {'Total': 4, 'Samba': 1, 'Cha Cha': 1, 'Jive': 1, 'Rumba': 
                        1, 'Paso Doble': 0}, 'Rhythm': {'Total': 0, 'Cha Cha': 0, 'Swing': 0, 'Bolero': 0, 'Rumba': 0, 'Mambo': 0}, 'Standard': {'Total': 16, 'V. Waltz': 0, 'Tango': 3, 'Foxtrot': 5, 'Quickstep': 5, 'Waltz': 3}, 'Smooth': {'Total': 8, 'V. Waltz': 0, 'Tango': 2, 'Foxtrot': 2, 'Waltz': 4}}}
  
class SplashScreenMode(Mode):
    def appStarted(mode):
        mode.msg = 'Press any key to enter a dancer!'
        mode.dancerSet = False

    def redrawAll(mode, canvas):
        fontTitle = 'Arial 30 bold'
        fontMsg = 'Arial 20 bold'
        canvas.create_text(mode.width/2, 150, 
                           text='Ballroom YCN Points Calculator', 
                           font=fontTitle)
        canvas.create_text(mode.width/2, 190, text='and Statistics Program', 
                           font=fontTitle)
        canvas.create_text(mode.width/2, 300, text=mode.msg, font=fontMsg)

    def keyPressed(mode, event):
        if event.key == 'Tab':
            mode.app.setActiveMode(mode.app.testUsingET)
            return

        firstName = mode.app.getUserInput("Competitor's First Name: ")
        if (firstName == None):
            mode.app.showMessage = 'You canceled!'
        else:
            lastName = mode.app.getUserInput("Competitor's Last Name: ")
            if (lastName == None):
                mode.app.showMessage = 'You canceled!'
            else:
                firstName = firstName.title()
                lastName = lastName.title()
                mode.name = firstName + ' ' + lastName
                mode.msg = f'Pulling results for {firstName} {lastName}... \n'
                mode.msg += 'Please Wait. This may take a few moments.'
                mode.dancerSet = True
                mode.firstName = firstName
                mode.lastName = lastName

    def resetApp(mode):
        Competition.competitions = None
        mode.dancerSet = False
        mode.msg = 'Press any key to enter a dancer!'            

    def timerFired(mode):
        if mode.dancerSet == True:
            mode.app.dancer = Dancer(mode.firstName, mode.lastName)
            if mode.app.dancer.competitions == ['No Results on File']: 
                mode.app.showMessage(f'No Results on O2CM for {mode.name}.\n' +
                                      'Please re-enter dancer name.')
                mode.resetApp()
                return
            mode.app.setActiveMode(mode.app.menuMode)

class YCNMode(Mode): 
    def appStarted(mode):
        mode.rows = 28
        mode.cols = 6
        mode.app.margin = 50

        mode.styleOrder = ['Smooth', 'Standard', 'Rhythm', 'Latin']
        
        smoothDances = ['', 'Waltz', 'Tango', 'Foxtrot', 'V. Waltz', 'Total', '']
        stdDances = ['Waltz', 'Quickstep', 'Tango', 'Foxtrot', 'V. Waltz', 'Total', '']
        rhythmDances = ['Cha Cha', 'Rumba', 'Swing', 'Mambo', 'Bolero', 'Total', '']
        latinDances = ['Cha Cha', 'Rumba', 'Samba', 'Jive', 'Paso Doble', 'Total', '']

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
        gridWidth  = mode.app.width - 2*mode.app.margin
        gridHeight = mode.app.height - 2*mode.app.margin
        columnWidth = gridWidth / mode.cols
        rowHeight = gridHeight / mode.rows
        x0 = mode.app.margin + col * columnWidth
        x1 = mode.app.margin + (col+1) * columnWidth
        y0 = mode.app.margin + row * rowHeight
        y1 = mode.app.margin + (row+1) * rowHeight
        return (x0, y0, x1, y1)

    def redrawAll(mode, canvas):
        canvas.create_text(mode.app.width/2, mode.app.margin/2, 
                           text = 'YCN Points Tally', font = 'Arial 25 bold')

        text = ('Totals in Red indicate that a dancer has pointed out of ' +
                'that style and level. Empty cells indicate that no points '+
                'have been earned.\n')
        text += 'Press any key to return to the Main Menu'
        canvas.create_text(mode.app.width/2, 
                           mode.app.height - mode.app.margin/2, 
                           text = text, fill = 'red')

        for row in range(mode.rows):
            if row in [1, 7, 14, 21]: continue
            
            if row == 0: fill = 'light blue'
            else: fill = None
            for col in range(mode.cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill = fill)
        mode.drawTableHeader(canvas)
        mode.drawDances(canvas)
        mode.addYCNPoints(canvas)
        
    
    def drawTableHeader(mode, canvas):
       
        xheaders = ['Style', 'Dance', 'Newcomer', 'Bronze', 'Silver', 'Gold']
        yheaders = [('Smooth', 2), ('Standard', 8), 
                   ('Rhythm', 15), ('Latin', 22)]
        font = 'Bold'
        for col in range(mode.cols):
            row = 0
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            canvas.create_text(x1+(x0-x1)/2, y1+(y0-y1)/2, 
                               text = xheaders[col], font = font)
        
        for style,row in yheaders:
            col = 0
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            canvas.create_text(x1+(x0-x1)/2, y1+(y0-y1)/2, 
                               text = style, font = font)
    
    def drawDances(mode, canvas):
        col = 1
        startRow = 1
        for row in range(startRow, mode.rows):
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            text = mode.dances[row-1]
            font = 'Arial 10'
            if text == 'Total':
                font = 'Arial 10 bold'
            canvas.create_text(x1+(x0-x1)/2, y1+(y0-y1)/2, 
                               text = text, font = font)
    
    def addYCNPoints(mode, canvas):
        levelOrder = ['Newcomer', 'Bronze', 'Silver', 'Gold']
        col = 2
        row = 1
        for level in levelOrder:
            for style in mode.styleOrder:
                for dance in mode.styleAndDanceDict[style]:
                    if dance == '':
                        row += 1
                        continue

                    points = mode.app.dancer.ycnDict[level][style][dance]
                    if points != 0:
                        font = 'Arial 10'
                        fill = 'black'
                        if dance == 'Total': 
                            font = 'Arial 10 bold'
                            if points >= 7: fill = 'red'
                        (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                        canvas.create_text(x1+(x0-x1)/2, y1+(y0-y1)/2, 
                                           text = points, font = font, 
                                           fill = fill)
                    row += 1
            col += 1
            row = 1

class YCNModeCondensed(Mode): 

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.menuMode)

    def appStarted(mode):
        mode.rows = 5
        mode.cols = 5
        mode.app.margin = 50

        mode.styleOrder = ['Smooth', 'Standard', 'Rhythm', 'Latin']

    # From https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCellBounds(mode, row, col):
        gridWidth  = mode.app.width - 2*mode.app.margin
        gridHeight = mode.app.height - 2*mode.app.margin
        columnWidth = gridWidth / mode.cols
        rowHeight = gridHeight / mode.rows
        x0 = mode.app.margin + col * columnWidth
        x1 = mode.app.margin + (col+1) * columnWidth
        y0 = mode.app.margin + row * rowHeight
        y1 = mode.app.margin + (row+1) * rowHeight
        return (x0, y0, x1, y1)

    def redrawAll(mode, canvas):
        canvas.create_text(mode.app.width/2, mode.app.margin/2, 
                           text = 'YCN Points Tally (Condensed)', 
                           font = 'Arial 25 bold')

        text = ('Totals in Red indicate that a dancer has pointed out of ' +
                'that style and level. Empty cells indicate that no points '+
                'have been earned.\n')
        text += 'Press any key to return to the Main Menu'
        canvas.create_text(mode.app.width/2, 
                           mode.app.height - mode.app.margin/2, 
                           text = text, fill = 'red')

        for row in range(mode.rows):            
            if row == 0: fill = 'light blue'
            else: fill = None
            for col in range(mode.cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill = fill)
        mode.drawTableHeader(canvas)
        mode.addYCNPoints(canvas)
        
    
    def drawTableHeader(mode, canvas):
       
        xheaders = ['Style', 'Newcomer', 'Bronze', 'Silver', 'Gold']
        yheaders = ['Smooth', 'Standard', 'Rhythm', 'Latin']
        font = 'Bold'
        for col in range(mode.cols):
            row = 0
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            canvas.create_text(x1+(x0-x1)/2, y1+(y0-y1)/2, 
                               text = xheaders[col], font = font)
        
        for row in range(1, mode.rows):
            col = 0
            style = yheaders[row-1]
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            canvas.create_text(x1+(x0-x1)/2, y1+(y0-y1)/2, 
                               text = style, font = font)
    
    
    def addYCNPoints(mode, canvas):
        levelOrder = ['Newcomer', 'Bronze', 'Silver', 'Gold']
        col = 1
        row = 1
        for level in levelOrder:
            for style in mode.styleOrder:
                points = mode.app.dancer.ycnDict[level][style]['Total']
                if points != 0:
                    fill = 'black'
                    font = 'Arial 20 bold'
                    if points >= 7: fill = 'red'
                    (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                    canvas.create_text(x1+(x0-x1)/2, y1+(y0-y1)/2, 
                                        text = points, font = font, 
                                        fill = fill)
                row += 1
            col += 1
            row = 1
         
class testUsingET(Mode):
    def appStarted(mode):
        mode.app.dancer = ElliottToy(mode)
        mode.app.setActiveMode(mode.app.menuMode)

class MenuMode(Mode):
    def keyPressed(mode, event):
        if event.key == '1':
            mode.app.splashScreenMode.resetApp()
            mode.app.setActiveMode(mode.app.splashScreenMode)
        elif event.key == '2':
            mode.app.setActiveMode(mode.app.ycnMode)
        elif event.key == '3':
            mode.app.setActiveMode(mode.app.ycnModeCondensed)
        elif event.key == '4':
            mode.app.setActiveMode(mode.app.compPicker)

        # More will be added later
    
    def redrawAll(mode, canvas):
        menuText = '\t\tMenu \n\n'
        menuText += 'Press 1 - To return to the start screen\n'
        menuText += 'Press 2 - To view to the YCN points chart (expanded)\n'
        menuText += 'Press 3 - To view to the YCN points chart (condensed)\n'
        menuText += 'Press 4 - To view to the Recall Rate Graph\n'
        menuText += 'Press 5 - To view to the Competetive Summary\n'
        menuText += 'Press 6 - To view to the Raw Results\n'
        
        canvas.create_text(mode.app.width/2, mode.app.height/2, 
                           text = menuText, font = 'Arial 20')

class CompPicker(Mode):
    def appStarted(mode):
        mode.text = mode.getOptionsString()
        
    def keyPressed(mode, event):
        compIndex = event.key
        numComps = mode.app.dancer.competitionList
        if compIndex.isnumeric:
            compIndex = int(compIndex)
            if compIndex < len(numComps):
                compSel = mode.app.dancer.competitionList[compIndex]
                print(compSel)

    def redrawAll(mode, canvas):
        canvas.create_text(mode.app.width/2, mode.app.height/2, 
                           text = mode.text
                           )
        pass
    
    def getOptionsString(mode):
        optionsStr = ('Please enter the number of the competition to generate'+ 
                      ' a recall rate graph: \n') 
        for i in range(len(mode.app.dancer.competitionList)):
            compName = str(mode.app.dancer.competitionList[i])
            optionsStr += ('\tPress ' + str(i) + ':\t' + compName + '\n')
        return optionsStr

        
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
        app.setActiveMode(app.splashScreenMode)
        app.timerDelay = 50

app = O2CMApp(width=1000, height=650)




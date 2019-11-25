from bs4 import BeautifulSoup
from mechanize import Browser
import urllib.request, time

class Competition(object):

    competitions = dict()
    def __init__(self, html, name):
        self.name = name
        self.html = BeautifulSoup(html, features='html.parser')
        self.getEvents(html)
        self.number = None
        Competition.competitions[self.name] = self
        print('done comp')
    
    def getEvents(self, html):
        self.events = dict()
        for link in self.html.find_all('a'):
            evtName = link.string.strip()
            self.events[evtName] = Event(link.get('href'), evtName)
    
    def __repr__(self):
        compStr = ''
        for Event in self.events:
            compStr += (str(self.events[Event]) + '\n')
        return compStr


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
        self.eventSoup = BeautifulSoup(content, features='html.parser')

        self.style = ''
        self.place = 0
        self.dance = []
        self.rounds = 0
        self.level = ''
        self.YCNPoints = 0
        
        self.getStyleAndDance()
        self.getRounds()
        self.getPlace()
        self.getLevel()
        self.getYCNPoints()
        
        endtime = time.time()

        print(f'done event: {self.eventName} ' + "%6.3fs" % (endtime - starttime))

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
        
        # print(self.dance, self.style)
        

    
    def getDanceFromEventPage(self):
        dances = self.eventSoup.find_all('td', attrs={'class':'h3'})[0:-1]
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
     
        self.rounds = len(self.eventSoup.find_all('option'))
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
        return eventStr

def testProgram():

    firstName  = input('Enter Competetor First Name: ')
    lastName  = input('Enter Competetor Last Name: ')

    firstName = 'austin'
    lastName = 'lin'

    resultsURL = f'http://results.o2cm.com/individual.asp?szLast={lastName}&szFirst={firstName}'


    content = urllib.request.urlopen(resultsURL).read()
    resultsPage = BeautifulSoup(content, features='html.parser')
    results = resultsPage.find_all('table')[0]
    resultsPageHTML = results.prettify()

    competitions = []
    for competition in results.find_all('b'):
        competitions.append(competition.string)

    for i in range(len(competitions)):
        compName = competitions[i]
        if i < len(competitions)-1:
            nextCompName = competitions[i+1]
            endIndex = resultsPageHTML.find(nextCompName)
        else:
            endIndex = len(resultsPageHTML)-1
        startIndex = resultsPageHTML.find(compName)
        compHTML = resultsPageHTML[startIndex:endIndex]
        Competition(compHTML, compName)

    print(Competition.competitions)

testProgram()




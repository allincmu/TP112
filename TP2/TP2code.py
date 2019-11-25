from bs4 import BeautifulSoup
from mechanize import Browser
import urllib.request, time

class Competition(object):

    competitions = dict()
    def __init__(self, html, name, Person):
        self.name = name
        self.html = BeautifulSoup(html, features='html.parser')
        self.getEvents(html, Person)
        self.number = None
        Competition.competitions[self.name] = self
        print('done comp')
    
    def getEvents(self, html, Person):
        self.eventsURL = dict()
        for link in self.html.find_all('a'):
            evtName = link.string.strip()
            event = Event(link.get('href'), evtName)
            self.eventsURL[evtName] = event
            if event.level in Person.eventsByLevel:
                Person.eventsByLevel[event.level].append(event)
            else:
                Person.eventsByLevel[event.level] = [event]
            
    
    def __repr__(self):
        compStr = ''
        for Event in self.eventsURL:
            compStr += (str(self.eventsURL[Event]) + '\n')
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
        self.eventHTML = BeautifulSoup(content, features='html.parser')

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

        # print(f'done event: {self.eventName} ' + "%6.3fs" % (endtime - starttime))

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
        
class Person(object):
    def __init__(self, firstName, lastName):
        self.firstName = firstName
        self.lastName = lastName
        self.resultsURL = (f'http://results.o2cm.com/individual.asp?' +
                           f'szLast={lastName}&szFirst={firstName}')
        self.eventsByLevel = {'Gold':[], 'Silver':[], 'Bronze':[], 'Newcomer':[]}
        self.getCompetitions()
        self.YCNTotals = {'Newcomer':0, 'Bronze':0, 'Silver':0, 'Gold':0}
        self.newcomerYCNs = dict()
        self.bronzeYCNs = dict()
        self.silverYCNs = dict()
        self.goldYCNs = dict()
        self.createYCNDictionary(self.newcomerYCNs)
        self.createYCNDictionary(self.bronzeYCNs)
        self.createYCNDictionary(self.silverYCNs)
        self.createYCNDictionary(self.goldYCNs)

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
            if i < len(self.competitions)-1:
                nextCompName = self.competitions[i+1]
                endIndex = self.resultsPageHTML.find(nextCompName)
            else:
                endIndex = len(self.resultsPageHTML)-1
            startIndex = self.resultsPageHTML.find(compName)
            compHTML = self.resultsPageHTML[startIndex:endIndex]
            self.competitionList.append(Competition(compHTML, compName, self))
    
    def createYCNDictionary(self, d):
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
        self.getnewcomerYCN()
        
        print(self.newcomerYCNs)
        print(self.bronzeYCNs)
        print(self.silverYCNs)
        print(self.goldYCNs)
    
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
    
    def getnewcomerYCN(self):
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
    
def testProgram():
    print('The default competetor is:')
    print('\t First Name: Arthur \n\t Last Name: Barelli')

    choice = input('Use default? (y/n) ')
    if choice == 'y':
        firstName = 'Arthur'
        lastName = 'Barelli'
    else:
        firstName  = input('Enter Competetor First Name: ')
        lastName  = input('Enter Competetor Last Name: ')
    
    Competetor = Person(firstName, lastName)

    

testProgram()




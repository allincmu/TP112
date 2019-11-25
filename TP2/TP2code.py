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
            self.events[evtName] = Event(link.get('href'), link.string.strip())
    
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

    def __init__(self, url, eventName):
        starttime = time.time()
        self.eventName = eventName
        self.url = url
        content = urllib.request.urlopen(self.url).read()
        self.eventSoup = BeautifulSoup(content, features='html.parser')

        self.style = ''
        self.place = ''
        self.dance = ''
        self.rounds = 0
        
        self.getStyleAndDance()
        self.getDance()
        self.getRounds()
        self.getPlace()
        
        endtime = time.time()

        print(f'done event: {self.eventName} ' + "%6.3fs" % (endtime - starttime))

    def getStyleAndDance(self):

        print(self.eventName)
        if 'Am.' in self.eventName:

            for dance in Event.smoothDances:
                print(True, dance)
                if dance in self.eventName:
                    self.dance = dance
                    self.style = 'Smooth'
                    break

            for dance in Event.rhythmDances:
                if dance in self.eventName:
                    self.dance = dance
                    self.style = 'Rhythm'
                    break

        elif 'Intl.' in self.eventName:
            for dance in Event.stdDances:
                if dance in self.eventName:
                    self.dance = dance
                    self.style = 'Standard'
                    break

            for dance in Event.latinDances:
                if dance in self.eventName:
                    self.dance = dance
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
        
        # print(self.dance, self.style)
        

    
    def getDance(self):
        pass

    def getRounds(self):
     
        self.rounds = len(self.eventSoup.find_all('option'))
        if self.rounds == 0:
            self.rounds = 1
        
        if self.rounds == 0:
            print('error')
        
    
    def getPlace(self):
        endIndex = self.eventName.find(')')
        self.place = self.eventName[0:endIndex]
        

    def __repr__(self):
        eventStr = f'Event Name: {self.eventName} \n'
        eventStr += f'\tURL: {self.url}'
        eventStr += f'\tStyle: {self.style}'
        eventStr += f'\tDance: {self.dance}'
        eventStr += f'\tRounds: {self.rounds}'
        eventStr += f'\tPlace: {self.place}'
        return eventStr

def testProgram():

    firstName  = input('Enter Competetor First Name: ')
    lastName  = input('Enter Competetor Last Name: ')

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



# {'10-26-19 - Keystone Dancesport Classic': {'12) Amateur Collegiate Bronze Am. Waltz': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322838, '21) Amateur Collegiate Bronze Am. Cha Cha': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322848, '20) Amateur Collegiate Bronze Am. Rumba': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322849, '24) Amateur Collegiate Bronze Am. Swing': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032284A, '10) Amateur Collegiate Bronze Am. Mambo': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032284C, '12) Amateur Collegiate Bronze Am. Foxtrot': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032283A, '15) Amateur Collegiate Silver Standard': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40323010, '14) Amateur Collegiate Silver Standard': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40323011, '7) Amateur Collegiate Silver Smooth': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40323030, '3) Amateur Collegiate Silver Smooth': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40323031, '3) Amateur Collegiate Bronze Am. V. Waltz': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032283B, '3) Amateur Collegiate Bronze Am. Tango': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322839, '8) Amateur Collegiate Bronze Intl. Waltz': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322818, '7) Amateur Collegiate Bronze Intl. Foxtrot': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032281B, '8) Amateur Collegiate Bronze Intl. Tango': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322819, '6) Amateur Collegiate Bronze Intl. Quickstep': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032281C}}
# {'10-26-19 - Keystone Dancesport Classic': Competition Name 10-26-19 - Keystone Dancesport Classic: 
# {'12) Amateur Collegiate Bronze Am. Waltz': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322838, '21) Amateur Collegiate Bronze Am. Cha Cha': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322848, '20) Amateur Collegiate Bronze Am. Rumba': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322849, '24) Amateur Collegiate Bronze Am. Swing': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032284A, '10) Amateur Collegiate Bronze Am. Mambo': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032284C, '12) Amateur Collegiate Bronze Am. Foxtrot': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032283A, '15) Amateur Collegiate Silver Standard': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40323010, '14) Amateur Collegiate Silver Standard': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40323011, '7) Amateur Collegiate Silver Smooth': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40323030, '3) Amateur Collegiate Silver Smooth': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40323031, '3) Amateur Collegiate Bronze Am. V. Waltz': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032283B, '3) Amateur Collegiate Bronze Am. 
# Tango': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322839, '8) Amateur Collegiate Bronze Intl. Waltz': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322818, '7) Amateur Collegiate Bronze Intl. Foxtrot': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032281B, '8) Amateur Collegiate Bronze Intl. Tango': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=40322819, '6) Amateur Collegiate Bronze Intl. Quickstep': http://results.o2cm.com/scoresheet3.asp?event=kdc19b&heatid=4032281C}}      
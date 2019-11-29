from bs4 import BeautifulSoup
import urllib.request
import requests
from mechanize import Browser
import time

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
def print2dList(a, compact = False, number = 120):
    foundNum = False
    a.pop(0)
    if (a == []):
        # So we don't crash accessing a[0]
        print([])
        return
    rows = len(a)
    cols = len(a[0])
    fieldWidth = maxItemLength(a)
    print("[ ", end="")
    for row in range(rows):
        if (row > 0):
            if compact == True:
                if a[row][0] != str(number): 
                    foundNum = True
                    continue
            print("\n  ", end="")
        print("[ ", end="")
        for col in range(cols):
            if (col > 0): print(", ", end="")
            # The next 2 lines print a[row][col] with the given fieldWidth
            formatSpec = "%" + str(fieldWidth) + "s"
            print(formatSpec % str(a[row][col]), end="")
        print(" ]", end="")
        if foundNum == True:
            break
    print("]")

def getRoundName(i):
    roundNames = ['Final', 'Semi-Final', 'Quarter-Final']
    if i <= 2:
        return roundNames[i]
    else:
        deno = 2**i
        return "1/" + str(deno) + "-Final"



def getResultsTable(url, i):
    br = Browser()
    br.addheaders = [('User-agent', 'Firefox')]
    br.open(url)
    if i != None:
        br.select_form(name="selectRound")
        br['selCount'] = [str(i)]
        br.submit()
    else:
        i = 0
    soup = BeautifulSoup(br.response().read(), features='html.parser')
    data = []
    
    
    table = soup.find('table', attrs={'class':'t1n'})
    

    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols]) # Get rid of empty values
    print()
    print(getRoundName(i))

    # print2dList(data, False)
    





firstName  = input('Enter Competetor First Name: ')
lastName  = input('Enter Competetor Last Name: ')

resultsURL = f'http://results.o2cm.com/individual.asp?szLast={lastName}&szFirst={firstName}'



if not requests.get(resultsURL).status_code == 200:
    crash()
content = urllib.request.urlopen(resultsURL).read()

soup = BeautifulSoup(content, features='html.parser')



events = dict()
for link in soup.find_all('a'):
    events[link.string] = link.get('href')

print(f'\n\n\n\n\t\t\tCompetetor Records for {firstName} {lastName}\n\n')
print()
for event in events:
    print('\n\nEvent: ', event)
    url = events[event]
    if not requests.get(url).status_code == 200:
        break
    print('\tUrl: ', url)
    content = urllib.request.urlopen(url).read()
    result = BeautifulSoup(content, features='html.parser')

    rounds = 0
    print('\tRounds: ')
    for heat in result.find_all('option'):
        print('\t\t', heat.string)
        rounds += 1
    
    print('\tNumber of rounds: ', rounds)

    start = time.time()
    for i in range(1, rounds):
        getResultsTable(url, i)
    end = time.time()
    print(end-start)


    print()







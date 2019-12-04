import time
import urllib.request
import decimal
from tkinter import *

from bs4 import BeautifulSoup
# From https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
from cmu_112_graphics import *
from mechanize import Browser

from ballroom_objects import *
from objects_for_testing import *


############################## Helper Functions ###############################

# From: https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))



################################## O2CM App ##################################


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
        mode.columnWidth = gridWidth / mode.cols
        mode.rowHeight = gridHeight / mode.rows
        x0 = mode.app.margin + col * mode.columnWidth
        x1 = mode.app.margin + (col + 1) * mode.columnWidth
        y0 = mode.app.margin + row * mode.rowHeight
        y1 = mode.app.margin + (row + 1) * mode.rowHeight
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
        mode.axisStartRow = 100
        mode.axisStartCol = 1
        mode.rows = 101
        mode.app.margin = 50
        mode.resetMode()

    def resetMode(mode):
        mode.compSelection.getRecallPercentagesForComp()
        numJudges = len(mode.compSelection.recallPercentages)

        mode.cols = numJudges * 2 + 1

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
        return x0, y0, x1, y1

    def redrawAll(mode, canvas):
        canvas.create_text(mode.app.width / 2, mode.app.margin / 2,
                           text='YCN Points Tally', font='Arial 25 bold')

        mode.drawBars(canvas)
        mode.drawAxis(canvas)

        text = 'Press any key to return to the Competition Selection Menu'
        canvas.create_text(mode.app.width / 2,
                           mode.app.height - mode.app.margin / 2 / 2,
                           text=text, fill='red')

    def drawBars(mode, canvas):
        colIndex = 1
        for judge in mode.compSelection.recallPercentages:
            percentage = mode.compSelection.recallPercentages[judge]
            barYBottom = 100
            barYTop = barYBottom - percentage
            for rowIndex in range(barYBottom, barYTop + 1, -1):
                (x0, y0, x1, y1) = mode.getCellBounds(rowIndex, colIndex)
                canvas.create_rectangle(x0, y0, x1, y1, fill='light blue',
                                        outline='light blue')
            mode.drawJudgeName(canvas, colIndex, judge)
            colIndex += 2

    def drawJudgeName(mode, canvas, colIndex, judge):
        nameRowIndex = 101
        (x0, y0, x1, y1) = mode.getCellBounds(nameRowIndex, colIndex)
        canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2, text=judge)

    def drawAxis(mode, canvas):
        pass


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

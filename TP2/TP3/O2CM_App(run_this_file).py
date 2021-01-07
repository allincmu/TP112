# Contains the classes for the UI

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


# Gets image passed as url and returns it
def importBackground(app, url, appWidth=1000):
    background = app.loadImage(url)
    photoWidth, photoHeight = background.size
    background = app.scaleImage(background,
                                appWidth /
                                min(photoWidth, photoHeight))
    return background


################################## O2CM App ##################################


class SplashScreenMode(Mode):

    # Sets up initial values needed for the mode
    def appStarted(mode):
        url = 'https://cdn.hipwallpaper.com/i/37/47/1l7FCt.jpg'
        mode.background = mode.app.loadImage(url)
        mode.background = mode.app.scaleImage(mode.background, 2 / 3)

        mode.msg = 'Press any key to enter a dancer!'
        mode.dancerSet = False

    # Resets values that need to be wiped when a new competitor is entered
    def resetMode(mode):
        Competition.competitions = dict()
        mode.dancerSet = False
        mode.msg = 'Press any key to enter a dancer!'

    # Prompts the user to enter a dancer's name when a key is pressed
    def keyPressed(mode, event):
        if event.key == 'Tab':
            mode.app.setActiveMode(mode.app.testUsingET)
            return

        firstName = mode.app.getUserInput("Competitor's First Name: ")
        if firstName is None or firstName == '':
            mode.app.showMessage('First Name cannot be blank!')
        else:
            lastName = mode.app.getUserInput("Competitor's Last Name: ")
            if lastName is None or lastName == '':
                mode.app.showMessage('Last Name cannot be blank!')
            else:
                firstName = firstName.title()
                lastName = lastName.title()
                mode.name = firstName + ' ' + lastName
                mode.msg = f'Pulling results for {firstName} {lastName}... \n'
                mode.msg += 'Please Wait. This may take a few moments.'
                mode.dancerSet = True
                mode.firstName = firstName
                mode.lastName = lastName

    # Checks to see if the user has entered a dancer and creates a dancer object
    # Then changes to menu mode.
    def timerFired(mode):
        if mode.dancerSet:
            mode.app.competitor = Dancer(mode.firstName, mode.lastName)
            if mode.app.competitor.competitions == ['No Results on File']:
                mode.app.showMessage(f'No Results on O2CM for {mode.name}.\n' +
                                     'Please re-enter dancer name.')
                mode.resetMode()
                return
            mode.app.setActiveMode(mode.app.menuMode)

    def redrawAll(mode, canvas):
        canvas.create_image(mode.width / 2, mode.height / 2,
                            image=ImageTk.PhotoImage(mode.background))
        fontTitle = 'Arial 24 bold'
        fontMsg = 'Arial 18 bold'

        textCenterX = 325
        canvas.create_text(textCenterX, 240,
                           text='Ballroom Competition Recall Statistics',
                           font=fontTitle)
        canvas.create_text(textCenterX, 280,
                           text='and YCN Points Calculator',
                           font=fontTitle)
        canvas.create_text(textCenterX, 380, text=mode.msg,
                           font=fontMsg)


class YCNMode(Mode):
    # initializes the background
    def createBackground(mode):
        url = ('https://wallpapertag.com/wallpaper/full/3/2/4/142440-cool-' +
               'blue-ombre-background-2560x1600-tablet.jpg')
        mode.background = importBackground(mode.app, url)

    # Sets up initial values needed for the mode
    def appStarted(mode):
        mode.createBackground()

        mode.rows = 28
        mode.cols = 6

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

    # returns the user to the menu when they press a key
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
        canvas.create_image(mode.width / 2, mode.height / 2,
                            image=ImageTk.PhotoImage(mode.background))
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
                fill = 'orange'
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

    # Defines the headers for the chart
    def setUpHeaders(mode):

        mode.xheaders = ['Style', 'Dance', 'Newcomer', 'Bronze', 'Silver',
                         'Gold']
        mode.yheaders = [('Smooth', 2), ('Standard', 8),
                         ('Rhythm', 15), ('Latin', 22)]

    # Draws the row headers
    def drawTableXHeaders(mode, canvas):
        font = 'Bold'
        for col in range(mode.cols):
            row = 0
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2,
                               text=mode.xheaders[col], font=font)

    # Draws column headers
    def drawTableYHeaders(mode, canvas):
        font = 'bold'
        for style, row in mode.yheaders:
            col = 0
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2,
                               text=style, font=font)

    # Adds dances to the chart
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

    # Puts points earned into the chart
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
        super().createBackground()
        mode.rows = 5
        mode.cols = 5

        mode.styleOrder = ['Smooth', 'Standard', 'Rhythm', 'Latin']

    def redrawAll(mode, canvas):
        canvas.create_image(mode.width / 2, mode.height / 2,
                            image=ImageTk.PhotoImage(mode.background))
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
                fill = 'orange'
            else:
                fill = None
            for col in range(mode.cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill=fill)

        mode.setUpHeaders()
        mode.drawTableXHeaders(canvas)  # Inherited from superclass
        mode.drawTableYHeaders(canvas)
        mode.addYCNPointsToTable(canvas)

    # Defines the headers for the chart
    def setUpHeaders(mode):
        mode.xheaders = ['Style', 'Newcomer', 'Bronze', 'Silver', 'Gold']
        mode.yheaders = ['Smooth', 'Standard', 'Rhythm', 'Latin']

    # Draws the header row
    def drawTableYHeaders(mode, canvas):
        font = 'Bold'
        for row in range(1, mode.rows):
            col = 0
            style = mode.yheaders[row - 1]
            (x0, y0, x1, y1) = mode.getCellBounds(row, col)
            canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2,
                               text=style, font=font)

    # Draws the header col
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
    def appStarted(mode):
        url = 'https://wallpapercave.com/wp/wp2004203.jpg'
        mode.background = mode.app.loadImage(url)
        photoWidth = 1440
        mode.background = mode.app.scaleImage(mode.background,
                                              mode.app.width / photoWidth)

    # Determines what to when a menu option is selected
    def keyPressed(mode, event):
        if event.key == '4':
            mode.app.setActiveMode(mode.app.splashScreenMode)
            mode.app.splashScreenMode.resetMode()
        elif event.key == '1':
            mode.app.setActiveMode(mode.app.ycnMode)
        elif event.key == '2':
            mode.app.setActiveMode(mode.app.ycnModeCondensed)
        elif event.key == '3':
            mode.app.setActiveMode(mode.app.compPicker)
            mode.app.compPicker.resetMode()

        # More will be added later

    def redrawAll(mode, canvas):
        canvas.create_image(mode.width / 2, mode.height / 2,
                            image=ImageTk.PhotoImage(mode.background))
        menuText = '\t\tMain Menu \n\n'
        menuText += 'Press 1 - View YCN points chart (Detailed)\n'
        menuText += 'Press 2 - View YCN points chart (Summary)\n'
        menuText += 'Press 3 - Generate Recall Rate Graph\n'
        menuText += 'Press 4 - To Enter a Different Competitor\n'
        # menuText += 'Press 5 - To view to the Competetive Summary\n'
        # menuText += 'Press 6 - To view to the Raw Results\n'

        yshift = 50
        xshift = 100

        canvas.create_text(741,
                           mode.app.height / 4,
                           text=menuText, font='Arial 17', fill='white')

class CompPicker(Mode):
    def createBackground(mode):
        url = ('http://wallpaperping.com/wp-content/uploads/2018/10/blur-' +
               'blue-gradient-cool-background-sp-2048x1152.jpg')
        mode.background = importBackground(mode.app, url)

    # initializes varibles the first time the mode is called
    def appStarted(mode):
        mode.createBackground()
        mode.resetMode()

    # resets variables that need to be reset everytime the mode is called
    def resetMode(mode):
        mode.compSelected = False
        mode.getMsg()

    # determines if a competition was selected
    # calls function to get recall graphs
    def timerFired(mode):
        if mode.compSelected:
            mode.compSelection.getResultsTablesForComp()
            mode.app.recallGraphMode.compSelection = mode.compSelection
            mode.app.setActiveMode(mode.app.recallGraphMode)
            mode.app.recallGraphMode.resetMode()

    # determines if input is menu item selection or return to main menu
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
        canvas.create_image(mode.width / 2, mode.height / 2,
                            image=ImageTk.PhotoImage(mode.background))
        font = 'Arial 20'
        canvas.create_text(mode.app.width / 2, mode.app.height / 2,
                           text=mode.msg, font=font)

        text = 'Press any nonnumerical key to return to the Main Menu'
        canvas.create_text(mode.app.width / 2,
                           mode.app.height - mode.app.margin / 4,
                           text=text, fill='red')

    # changes the message when a competition is selected
    def getMsg(mode):
        if mode.compSelected:
            mode.msg = f'Pulling recall data for {mode.compSelection} \n'
            mode.msg += 'Please Wait... This will take several minutes.'

        else:
            mode.msg = ('Please enter the number of the competition to ' +
                        'generate a recall rate graph: \n')
            for i in range(len(mode.app.competitor.competitionList)):
                compName = str(mode.app.competitor.competitionList[i])
                mode.msg += ('\tPress ' + str(i) + ':\t' + compName + '\n')


class RecallGraphMode(Mode):
    # gets background image
    def createBackground(mode):
        url = ('http://wallpaperping.com/wp-content/uploads/2018/10/blur-' +
               'blue-gradient-cool-background-sp-2048x1152.jpg')
        mode.background = importBackground(mode.app, url)

    # Initializes variables the first time the mode is called
    def appStarted(mode):
        mode.createBackground()
        mode.axisStartRow = 100
        mode.axisStartCol = 0
        mode.rows = 101
        mode.axisFontSize = 'Arial 12'
        mode.axisTickLength = 10
        mode.axisTickFrequency = 10
        mode.resetMode()

    # Resets attributes to their default values when the mode is called
    def resetMode(mode):
        mode.compSelection.getRecallPercentagesForComp()
        numJudges = len(mode.compSelection.recallPercentages)

        mode.cols = numJudges * 2 + 1

    # returns user to comp selection screen when key is pressed
    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.compPicker)
        mode.app.compPicker.resetMode()

    # From https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    # With slight edits
    def getCellBounds(mode, row, col):
        gridWidth = mode.app.width - 2 * mode.app.margin
        gridHeight = mode.app.height - 2 * mode.app.margin
        columnWidth = gridWidth / (mode.cols + 1)
        rowHeight = gridHeight / (mode.rows + 5)
        x0 = mode.app.margin + (col + 1) * columnWidth
        x1 = mode.app.margin + (col + 2) * columnWidth
        y0 = mode.app.margin + row * rowHeight
        y1 = mode.app.margin + (row + 1) * rowHeight
        if row == 101:
            y1 = mode.app.margin + (row + 4) * rowHeight
        return x0, y0, x1, y1

    def redrawAll(mode, canvas):
        canvas.create_image(mode.width / 2, mode.height / 2,
                            image=ImageTk.PhotoImage(mode.background))
        canvas.create_text(mode.app.width / 2, mode.app.margin / 2,
                           text=f'Recall Percentage Graph for '
                                f'{mode.compSelection}',
                           font='Arial 15 bold')

        mode.drawBars(canvas)
        mode.drawAxis(canvas)

        canvas.create_text(mode.app.width / 2,
                           mode.app.height - mode.app.margin * (1 - 1 / 4),
                           text='Judge Number', font=mode.axisFontSize)

        canvas.create_text(mode.app.margin / 2, mode.app.height / 2,
                           text='Recall Percentage (%)',
                           font=mode.axisFontSize, angle=90)

        text = 'Press any key to return to the Competition Selection Menu'
        canvas.create_text(mode.app.width / 2,
                           mode.app.height - mode.app.margin / 4,
                           text=text, fill='orange')

    # Draws bars
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

            percentageRow = barYBottom - 3
            (x0, y0, x1, y1) = mode.getCellBounds(percentageRow, colIndex)
            canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2,
                               text=f'{percentage}%')
            mode.drawJudgeName(canvas, colIndex, judge)
            colIndex += 2

    # Draws the Judge's number below each bar
    def drawJudgeName(mode, canvas, colIndex, judge):
        nameRowIndex = 101
        (x0, y0, x1, y1) = mode.getCellBounds(nameRowIndex, colIndex)
        canvas.create_text(x1 + (x0 - x1) / 2, y1 + (y0 - y1) / 2, text=judge)

    # draws the axis
    def drawAxis(mode, canvas):
        (bx0, by0, bx1, by1) = mode.getCellBounds(mode.axisStartRow,
                                                  mode.axisStartCol)
        (tx0, ty0, tx1, ty1) = mode.getCellBounds(0, mode.axisStartCol)
        (rx0, ry0, rx1, ry1) = mode.getCellBounds(mode.axisStartRow,
                                                  mode.cols - 1)

        canvas.create_line(bx0, by1, tx0, ty0)
        canvas.create_line(bx0, by1, rx1, ry1)

        mode.drawAxisTicks(mode.axisTickFrequency, canvas)

    # draws the axis ticks and values
    def drawAxisTicks(mode, frequency, canvas):
        for tick in range(0, mode.axisStartRow, frequency):
            x0, y0, x1, y1 = mode.getCellBounds(tick, mode.axisStartCol)
            tickY = y0
            tickX1 = x0 - mode.axisTickLength / 2
            tickX2 = x0 + mode.axisTickLength / 2
            canvas.create_line(tickX1, tickY, tickX2, tickY)

            tickValue = 100 - tick
            canvas.create_text(tickX1 - 5, tickY, text=tickValue, anchor='e')


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
        app.margin = 50


app = O2CMApp(width=1000, height=650)

 def getYCN(self, level, currYCNDict, prevYCNDict):

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



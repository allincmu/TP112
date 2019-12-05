from ballroom_objects import Competition


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
        competition = TestCompetition('Ohio Star Ball')
        self.competitionList = [competition]


class TestCompetition(Competition):
    def __init__(self, name):
        self.name = name
        self.recallPercentages = {'12': 65, '13': 74, '15': 20, '16': 41,
                                  '17': 26, '18': 10, '19': 21, '21': 26,
                                  '14': 63, '20': 22, '10': 73, '11': 70}

    # Overrides the superclass's function because the call to this function
    # is unnecessary as self.recallPercentages has been manually defined
    def getRecallPercentagesForComp(self):
        pass

    # Overrides the superclass's function because the call to this function
    # is unnecessary for the test class
    def getResultsTablesForComp(self):
        pass

#Benjamin Roderick

import musicalbeeps
from note import Note

class Melody:
    
    def __init__(self, filename):
        '''
        (NoneType) -> NoneType
        
        Constructor for the Melody object type.
        
        >>>bday = Melody('birthday.txt')
        >>>bday.title
        'Happy Birthday'
        >>>bday.author
        'Patty and Mildred J. Hill'
        >>>print(bday.notes[2])
        0.5 E 4 natural
        
        >>>hotcross = Melody('hotcrossbuns.txt')
        >>>len(hotcross.notes)
        17
        
        >>>tetris = Melody('tetris.txt')
        >>>tetris.author
        'Nikolay Nekrasov, Hirokazu Tanaka'
        '''
        fobj = open(filename, 'r')
        
        content = []
        
        for line in fobj:
            content.append(line.strip('\n'))
        
        fobj.close()
        
        self.title = content[0]
        
        self.author = content[1]
        
        self.notes = []
        
        placeholder = []
        
        pairings = []
        
        song = content[2:]
        
        for i in range(len(song)):
            if song[i].count('true') == 1:
                placeholder.append(i)

                if len(placeholder) == 2:
                    pairings.append([placeholder[0],placeholder[1]])
                    
                    placeholder = []
        
        
        for i in range(len(pairings))[::-1]:

            song = song[:(pairings[i][1]+1)] + song[pairings[i][0]:(pairings[i][1]+1)] + song[(pairings[i][1]+1):]
        
        for i in song:
            placeholder = i.split()
            
            if placeholder[0].count('.') == 1:
                placeholder[0] = '0' + placeholder[0]
            
            if placeholder[1] == 'R':
                self.notes.append(Note(float(placeholder[0]), placeholder[1]))
                
            else:
                self.notes.append(Note(float(placeholder[0]), placeholder[1], int(placeholder[2]), placeholder[3].lower()))
            
            placeholder = []
            
    def play(self, player):
        for i in self.notes:
            i.play(player)
            
    def get_total_duration(self):
        '''
        (NoneType) -> float
        
        Calculates the total duration of the Note objects in a Melody object's notes instance attribute.
        
        >>>bday = Melody('birthday.txt')
        >>>bday.get_total_duration()
        13.0
        
        >>>elise = Melody('fur_elise.txt')
        >>>elise.get_total_duration()
        25.799999999999944
        
        >>>tetris = Melody('tetris.txt')
        >>>tetris.get_total_duration()
        15.5
        '''
        time_total = 0
        
        for i in self.notes:
            time_total += i.duration
            
        return time_total
    
    def change_octave(self, direction_max, increment):
        '''
        Helper function for the lower_octave and upper_octave functions.
        '''
        no_octave = True
        
        for i in self.notes:
            if i.pitch == 'R':
                continue
            
            elif i.octave == direction_max:
                no_octave = False
            
        if no_octave:
            for i in self.notes:
                if i.pitch != 'R':
                    i.octave += increment
                
        return no_octave
        
    def lower_octave(self):
        '''
        (NoneType) -> bool
        
        Lowers the octave of all non-rest notes in a Melody object and whether the operation was executed or not.
        
        >>>bday = Melody('birthday.txt')
        >>> print(bday.notes[2])
        0.5 E 4 natural
        >>>bday.lower_octave()
        True
        >>>print(bday.notes[2])
        0.5 E 3 natural
        
        >>>hotcross = Melody('hotcrossbuns.txt')
        >>> print(hotcross.notes[2])
        1.0 G 4 natural
        >>>hotcross.lower_octave()
        True
        >>> print(hotcross.notes[2])
        1.0 G 3 natural
        
        >>>tetris = Melody('tetris.txt')
        >>> print(tetris.notes[2])
        0.25 C 5 natural
        >>>tetris.lower_octave()
        True
        >>> print(tetris.notes[2])
        0.25 C 4 natural
        '''
        return self.change_octave(1, -1)
    
    def upper_octave(self):
        '''
        (NoneType) -> bool
        
        Raises the octave of all non-rest notes in a Melody object and whether the operation was executed or not.
        
        >>>bday = Melody('birthday.txt')
        >>> print(bday.notes[2])
        0.5 E 4 natural
        >>>bday.upper_octave()
        True
        >>>print(bday.notes[2])
        0.5 E 5 natural
        
        >>>hotcross = Melody('hotcrossbuns.txt')
        >>> print(hotcross.notes[2])
        1.0 G 4 natural
        >>>hotcross.upper_octave()
        True
        >>> print(hotcross.notes[2])
        1.0 G 5 natural
        
        >>>tetris = Melody('tetris.txt')
        >>> print(tetris.notes[2])
        0.25 C 5 natural
        >>>tetris.upper_octave()
        True
        >>> print(tetris.notes[2])
        0.25 C 6 natural
        '''
        return self.change_octave(7, 1)
    
    def change_tempo(self, factor):
        '''
        (float) -> NoneType
        
        Multiplies the duration of each Note in the Melody.
        
        >>>bday = Melody('birthday.txt')
        >>> print(bday.notes[2])
        0.5 E 4 natural
        >>>bday.change_tempo(2)
        >>>print(bday.notes[2])
        1.0 E 4 natural
        
        >>>hotcross = Melody('hotcrossbuns.txt')
        >>> print(hotcross.notes[2])
        1.0 G 4 natural
        >>>hotcross.change_tempo(1.5)
        >>> print(hotcross.notes[2])
        1.5 G 4 natural
        
        >>>tetris = Melody('tetris.txt')
        >>> print(tetris.notes[2])
        0.25 C 5 natural
        >>>tetris.change_tempo(3)
        >>> print(tetris.notes[2])
        0.75 C 5 natural
        '''
        for i in self.notes:
            i.duration *= factor
#Benjamin Roderick

import musicalbeeps

OCTAVE_MIN = 1
    
OCTAVE_MAX = 7
    
PITCH_VALUES = ["A","B","C","D","E","F","G","R"]
    
ACCIDENTALS = ["natural","sharp","flat"]

class Note:
        
    def __init__(self, duration, pitch, octave=1, accidental='natural'):
        '''
        (NoneType) -> NoneType
        
        Constructor for the Note object type.
        
        >>>note1 = Note(2.0, "B", 4, "natural")
        >>>note1.duration
        2.0
        >>>note1.pitch
        'B'
        >>>note1.octave
        4
        >>>note1.accidental
        'natural'
        
        >>>note2 = Note(-3.0, "B", 4, "natural")
        AssertionError: Invalid duration
        
        >>>note3 = Note(1.0,'Z',3,'natural')
        AssertionError: Invalid pitch
        '''
        
        if [type(duration),type(pitch),type(octave),type(accidental)] != [float,str,int,str]:
            raise AssertionError("Invalid input types")        
        
        if duration <= 0:
            raise AssertionError("Invalid duration")
                
        elif pitch not in PITCH_VALUES:
            raise AssertionError("Invalid pitch")
        
        elif (octave < OCTAVE_MIN) or (octave > OCTAVE_MAX):
            raise AssertionError("Invalid octave")
        
        elif accidental not in ACCIDENTALS:
            raise AssertionError("Invalid accidental")
        
        self.duration = duration
        self.pitch = pitch
        self.octave = octave        
        self.accidental = accidental
        
    def __str__(self):
        '''
        (NoneType) -> NoneType
        
        Defines how the Note object is interpreted as a string.
        
        >>>note1 = Note(2.0, "B", 4, "natural")
        >>>print(note1)
        2.0 B 4 natural
        
        >>>note2 = Note(1.0, 'R')
        >>>print(note2)
        1.0 R
        
        >>>note3 = Note(1.4, 'A', 7, 'sharp')
        >>>print(note3)
        1.4 A 7 sharp
        '''
        if self.pitch == 'R':
            return str(self.duration) + ' ' + self.pitch
        
        else:
            return str(self.duration) + ' ' + self.pitch + ' ' + str(self.octave) + ' ' + self.accidental
    
    def play(self, player):
        if self.pitch == "R":
            player_input = "pause"
            
        elif self.accidental == 'sharp':
            player_input = self.pitch + str(self.octave) + '#'
            
        elif self.accidental == 'flat':
            player_input= self.pitch + str(self.octave) + 'b'
        
        else:
            player_input = self.pitch + str(self.octave)
            
        player.play_note(player_input, self.duration)
    
    
    
    
        
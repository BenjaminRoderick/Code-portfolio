'''
This is a small program that parses a .txt file, and plays musical notes based upon its contents.
'''



import musicalbeeps
from melody import Melody

if __name__ == "__main__":
    player = musicalbeeps.Player()
    melody = Melody("Megalovania.txt")
    melody.play(player)
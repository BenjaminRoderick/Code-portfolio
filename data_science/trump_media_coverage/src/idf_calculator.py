import os
import math

class Term:
    def __init__(self, word):
        self.word = word
        self.count = 1
        self.IDF = 0

    def __str__(self):
        return f'{self.word},{self.IDF}'

def main():
    path = os.path.dirname(__file__)[:-3]
    in_path = path + 'out/data_files/word_lists/'
    term_list = []
    num_categories = 0

    for filename in os.listdir(in_path):
        term_list = count_occurences(in_path, filename, term_list)
        num_categories = num_categories + 1
    
    for term in term_list:
        term.IDF = math.log(num_categories / term.count)

    with open(path + 'out/data_files/IDF_values.csv', 'w') as f:
        for term in term_list:
            f.write(str(term) + '\n')

def count_occurences(in_path, filename, term_list):
    with open(in_path + filename, 'r') as f:
        for line in f:
            found = False
            for term in term_list:
                if(term.word == line.rstrip()):
                    term.count = term.count + 1
                    found = True
                    break
            
            if(not found):
                term_list.append(Term(line.rstrip()))

    return term_list

def compute_IDF():
    pass

if __name__ == '__main__':
    main()
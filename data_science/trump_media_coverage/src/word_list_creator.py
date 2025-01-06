import os
import pandas as pd # type: ignore
import re

def main():
    dir_path = os.path.dirname(__file__)[:-3]
    in_path = dir_path + 'out/data_files/filtered_data/'
    out_path = dir_path + 'out/data_files/word_lists/'

    for filename in os.listdir(in_path):
        find_word_list(in_path, out_path, filename)

def find_word_list(in_path, out_path, filename):
    df = pd.read_csv(in_path + filename, usecols=[2,3])
    regex = "[|\'\"!?,‚Ä¶òôù¢î.:;\r]+|<.*>"
    word_set = set()

    for index, row in df.iterrows():
        words = trim_split(row['title'], regex)
        word_set = word_set.union(set(words))
        words = trim_split(row['content'], regex)
        word_set = word_set.union(set(words))

    file = filename[:-4]
    with open(out_path + f'{file}_words.txt', 'w') as f:
        for word in word_set:
            f.write(word + '\n')

def trim_split(text, regex):
    return re.sub('\n|¬†', ' ', re.sub(regex, '', text)).lower().split(' ')[:-2]
    

if __name__ == '__main__':
    main()
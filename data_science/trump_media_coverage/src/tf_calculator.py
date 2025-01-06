import os
import pandas as pd # type: ignore
import re
    
def main():
    dir_path = os.path.dirname(__file__)[:-3]
    in_path = dir_path + 'out/data_files/filtered_data/'
    out_path = dir_path + 'out/data_files/TF_data/'

    for filename in os.listdir(in_path):
        find_word_list(in_path, out_path, filename)

def find_word_list(in_path, out_path, filename):
    df = pd.read_csv(in_path + filename, usecols=[2,3])
    regex = "[|\'\"!?,‚Ä¶òôù¢î.:;\r]+|<.*>"
    file = filename[:-4]

    words_not_repeating = set()
    word_all_articles = []

    for index, row in df.iterrows():
        words = trim_split(row['title'], regex) + trim_split(row['content'], regex)
        words_not_repeating = words_not_repeating.union(set(words))
        word_all_articles.append(words)

    with open(out_path + f'{file}_TF.csv', 'w') as f:
        for word in words_not_repeating:
            individual_word_count = 0
            for article in word_all_articles:
                individual_word_count = individual_word_count + article.count(word)

            to_write = individual_word_count / len(words_not_repeating)
            f.write(f'{word},{to_write}\n')

def trim_split(text, regex):
    return re.sub('\n|¬†', ' ', re.sub(regex, '', text)).lower().split(' ')[:-2]
    

if __name__ == '__main__':
    main()
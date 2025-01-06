import os
import argparse
import json
import csv

def main(output):
    path = os.path.dirname(__file__)[:-3]
    input_path = path + 'data/'#change this to choose the input folder
    output_path = path + 'out/' + output
    header = ['source', 'date_published', 'title', 'content', 'url']

    with open(output_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    for filename in os.listdir(input_path):
        dump_csv(input_path + filename, output_path)

def dump_csv(input, output):
    with open(input, 'r') as f:
        data = json.load(f)

    articles = data['articles']

    to_write = []

    for article in articles:
        line = []
        line.append(article['source']['name'])
        line.append(article['publishedAt'][:10])
        line.append(article['title'])
        line.append(article['content'])
        line.append(article['url'])
        to_write.append(line)

    with open(output, 'a') as f:
         writer = csv.writer(f)
         writer.writerows(to_write)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output')
    args = parser.parse_args()

    main(args.output)
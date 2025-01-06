#
#Example of input to run file: python src/random_articles.py out/trump_oct26-nov25.csv 500 out/500_Trump_Articles.csv out/north_american_sources.txt

import pandas as pd
import os
import argparse
import random

def load_sources(sources_file):
    if not os.path.exists(sources_file):
        print(f"Error: The file '{sources_file}' was not found.")
        return []
    
    with open(sources_file, 'r') as file:
        sources = [line.strip() for line in file.readlines()]
    return sources

def select_random_articles(input_csv, num_articles, output_csv, sources):
    try:
        data = pd.read_csv(input_csv)

        filtered_data = data[data['source'].isin(sources)]
        
        if num_articles > len(filtered_data):
            raise ValueError(f"Requested {num_articles} articles, but only {len(filtered_data)} are available.")

        selected_articles = filtered_data.sample(n=num_articles, random_state=random.randint(0, 10000))

        selected_articles.to_csv(output_csv, index=False)
        
        print(f"Successfully saved {num_articles} random articles to '{output_csv}'.")
    except FileNotFoundError:
        print(f"Error: The file '{input_csv}' was not found.")
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select random articles from a CSV file.")
    parser.add_argument("input_csv", help="Relative or absolute path to the input CSV file.")
    parser.add_argument("num_articles", type=int, help="Number of articles to select.")
    parser.add_argument("output_csv", help="Relative or absolute path to save the output CSV file.")
    parser.add_argument("sources_file", help="Path to the sources file (north_american_sources.txt).")

    args = parser.parse_args()

    sources = load_sources(args.sources_file)

    if not sources:
        print("No sources found. Exiting.")
    else:
        select_random_articles(args.input_csv, args.num_articles, args.output_csv, sources)







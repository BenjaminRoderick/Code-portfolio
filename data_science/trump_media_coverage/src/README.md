# Scripts

## How to use these scripts to do the project yourself
1. Create a newsapi account and create an api key, then save it in /trump_media_coverage/credentials/api_key.md
2. Create the directory /trump_media_coverage/data/ then run the article_collection.py script.
3. Run the json_to_csv.py script in the unix cli with:

```
python json_to_csv.py all_articles.csv
```

4. Use a tool such as grep or excel to remove duplicate articles based on title, then run the random_articles.py script to take a sample of 500 articles from North American sources.
5. Use the typology in /out/typology.md to annotate the articles by hand. This will end with each article having a topic and a sentiment.
6. Separate the articles by topic based on the annotation you gave them (this is the step of the files saved in /out/data_files/filtered_data/)
7. Use the BASH script:

```
bash src/run_tf-idf.sh
```

This will produce a term frequency-inverse document frequency (TF-IDF) analysis csv for each category in /out/data_files/TF-IDF_by_category/.

8. Use the Jupyter notebook in /out/data_files/TF-IDF_by_category/bar_plots.ipynb to get a bar plot for the top 10 most relevant words in each category.
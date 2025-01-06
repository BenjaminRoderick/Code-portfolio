import os.path
from argparse import ArgumentParser
import pandas as pd # type: ignore
from datetime import datetime

def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--filename", help="Name of file", required=True)
    parser.add_argument("-s", "--startdate", help="Start date", required=True)
    parser.add_argument("-e", "--enddate", help="End date", required=True)
    parser.add_argument("-o", "--output", help="Name of output file", required=False)

    args = parser.parse_args()
    filename = args.filename
    startdate = pd.to_datetime(args.startdate, format="%m/%d/%y")
    enddate = pd.to_datetime(args.enddate, format="%m/%d/%y")
    print (startdate)
    print (enddate)
    output = args.output
    process_csv (filename, startdate, enddate, output)


def process_csv (filename, startdate, enddate, output):
    filepath = os.path.dirname(__file__)[:-3] + "data/" + filename
    dataframe = pd.read_csv(filepath, usecols=[1,2,5,25], names=["start", "end", "type", "borough"]).dropna()
    date_filtered = dataframe[dataframe["start"] >= startdate] & dataframe[dataframe["end"] <= enddate]
    print (date_filtered.head())

if (__name__ == "__main__"):
    main()
import pandas as pd # type: ignore
import os.path
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", help="name of file", required=True)
    
    args = parser.parse_args()
    filename = args.input
    #pie_chart(filename)
    print (count_unique(filename))

def count_unique(filename):
    filepath = os.path.dirname(__file__)[:-3] + "data/" + filename
    df = pd.read_csv(filepath, usecols=[1,2], names=["descriptor", "building_type"])
    return df.groupby("building_type")["descriptor"].nunique()
    #print (df)


if __name__ == '__main__':
    main()
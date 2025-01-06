import pandas as pd # type: ignore
import os.path
from argparse import ArgumentParser
import matplotlib.pyplot as plt
import numpy as np

def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", help="name of file", required=True)
    
    args = parser.parse_args()
    filename = args.input
    #pie_chart(filename)
    print (count_unique(filename))

def count_unique(filename):
    filepath = os.path.dirname(__file__)[:-3] + "data/" + filename
    df = pd.read_csv(filepath, names=["complaint_type", "descriptor"])
    return df.groupby("descriptor")["complaint_type"].nunique()
    #print (df)

def pie_chart(filename):
    df = count_unique(filename)
    titles = df[0].tolist()
    values = df[1].tolist()
    y = np.array(values)
    plt.pie(y, labels = titles)
    plt.show


if __name__ == '__main__':
    main()
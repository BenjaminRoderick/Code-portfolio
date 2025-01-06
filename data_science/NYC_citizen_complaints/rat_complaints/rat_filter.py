import pandas as pd # type: ignore
import os.path
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", help="name of file", required=True)
    
    args = parser.parse_args()
    filename = args.input
    do_operations(filename)

def do_operations(filename):
    dirname = os.path.dirname(__file__)[:-3] + "data/" + filename
    with open (dirname, 'r') as data:
        chunks = pd.read_csv(data, usecols=[5,6,8], names=["complaint_type", "descriptor", "building_type"], iterator=True, chunksize=1000)
        for chunk in chunks:
            chunk.to_csv("out.csv", mode='a', index=False, header=False)

if __name__ == "__main__":
    main()
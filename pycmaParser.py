import argparse
import numpy as np


def format_and_save(line,i):
    splited = line.split()
    print(splited[1],splited[4])
    splited = splited[5:]
    splited[-1] = splited[-1][0:-1]
    splited = np.array([float(x) for x in splited])
    np.save("pycmabest_"+str(i),splited)

parser = argparse.ArgumentParser()
parser.add_argument("--file", type=str, help="file")
parser.add_argument("--best", type=bool, help="find best individual",default = False)
args = parser.parse_args()


if args.best:
    minimum = 1000
    bestline = ""
    with open(args.file) as f:
        next(f)
        for line in f:
            splited = line.split()
            if float(splited[4])<minimum:
                minimum = float(splited[4])
                bestline = line
    format_and_save(bestline, 0)
            
    
else:
    i = 1000
    last = None
    
    with open(args.file) as f:
        for line in f:
            if last:
                splited = line.split()
                if int(splited[1]) > i:
                    format_and_save(last, i)
                    i += 1000
            last = line
    
            
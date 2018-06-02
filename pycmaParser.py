import argparse
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument("--file", type=str, help="file")
args = parser.parse_args()
last = ""
with open(args.file) as f:
    for line in f:
        last = line

last = last.split(sep=" ")
last = last[5:]
last[-1] = last[-1][0:-1]

last = np.array([float(x) for x in last])
np.save("pycmabest_0",last)
print(last)
            
            
import numpy as np
import argparse
import StairsEvolution

parser = argparse.ArgumentParser()
parser.add_argument("--genome", default='.', type=str, help="file with the npy saved genome")
args = parser.parse_args()

genome = np.load(args.genome)
fitness = StairsEvolution.simulate(genome, False,1000)
print("Individual with fitness " + str(fitness))
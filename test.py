import numpy as np
import argparse
import StairsEvolution

parser = argparse.ArgumentParser()
parser.add_argument("--genomes", type=str, help="file with the npy saved genomes")
args = parser.parse_args()

genomes = np.load(args.genomes)
fitness = StairsEvolution.simulate(genomes[0], False,500)
print("Individual with fitness " + str(fitness))
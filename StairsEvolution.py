import pyrosim
import numpy as np
import Stairs
import argparse
import cma

import Robot
import OriginalRobot
import SimpleRobot
import DenseRobot

from evostra import EvolutionStrategy

ROBOT_TYPE = None
MATRIX_SHAPE = None
GENOME_LENGTH = None

POPULATION_SIZE = 30
ELITISM = 5

MUTATION_PROBABILITY = 0.1
MUTATION_VARIANCE = 0.3

CROSSOVER_PROBABILITY = 0.5
TOURNAMENT_PROBABILITY = 0.8
SIM_TIME = 350

STEP = 0
STAIR_HEIGHT = 0.01

class Individual:
    fitness = -1000
    def __init__(self, genome):
        self.genome = genome
    def evaluate(self):
        self.fitness = simulate(self.genome,True, SIM_TIME,STAIR_HEIGHT)

def simulate(individual,blind,time,height):
    sim = pyrosim.Simulator(eval_time=time,play_blind=blind,debug=False, xyz = [-1,-1,1], hpr=[45,-27.5,0.0])
    builder = Stairs.StairBuilder(sim,[0.7,0.7,0],0.2)
    builder.build(20,height)
    
    weight_matrix = np.reshape(individual, MATRIX_SHAPE)
    if ROBOT_TYPE == "Robot":
        robot = Robot.Robot(sim,weight_matrix)
    elif ROBOT_TYPE == "OriginalRobot":
        robot = OriginalRobot.Robot(sim,weight_matrix)
    elif ROBOT_TYPE == "SimpleRobot":
        robot =  SimpleRobot.Robot(sim,weight_matrix)
    elif ROBOT_TYPE == "DenseRobot":
        robot =  DenseRobot.Robot(sim,weight_matrix)
    fitness_sensor = robot.build()
    
    sim.create_collision_matrix('intra')
    sim.start()
    results = sim.wait_to_finish()

    return min(sim.get_sensor_data(fitness_sensor, svi=1)[-1], sim.get_sensor_data(fitness_sensor, svi=0)[-1])
    #return sim.get_sensor_data(fitness_sensor, svi=0)[-1]

def initializeIndividual():
    genome = np.random.rand(GENOME_LENGTH)
    genome[:] = genome[:]*2.-1.
    return Individual(genome)
    
def initializePopulation():
    population = [initializeIndividual() for _ in range(POPULATION_SIZE)]
    return population

def mutate(individual):
    genome = individual.genome
    for i in range(GENOME_LENGTH):
        if np.random.rand() < MUTATION_PROBABILITY:
            genome[i] = genome[i] + np.random.normal(0,MUTATION_VARIANCE)
    return individual

def crossover(parent1, parent2):
    parent1 = parent1.genome
    parent2 = parent2.genome
    if np.random.rand() < CROSSOVER_PROBABILITY:
        index = np.random.randint(1, GENOME_LENGTH-1)
        child1 = np.concatenate((parent1[0:index], parent2[index:]))
        child2 = np.concatenate((parent2[0:index], parent1[index:]))
        return [Individual(child1), Individual(child2)]
    return [Individual(np.copy(parent1)), Individual(np.copy(parent2))]
 
def evaluate(population):
    for individual in population:
        individual.evaluate() 

def Tournament(individual1, individual2):
    better = individual1 if individual1.fitness > individual2.fitness else individual2
    worse = individual1 if individual1.fitness <= individual2.fitness else individual2
    if np.random.rand() < TOURNAMENT_PROBABILITY:
        return better
    return worse

def roulette(population):
        max     = sum([ind.fitness for ind in population])
        pick    = np.random.rand() * max
        current = 0
        for i in range(POPULATION_SIZE):
            current += fitnesses[i]
            if current > pick:
                return population[i]
            
def choose_parent(population):
    i1 = np.random.randint(0,POPULATION_SIZE)
    i2 = np.random.randint(0,POPULATION_SIZE)
    return Tournament(population[i1],population[i2])
    #return roulette(population, fitnesses)

def evolution_step(population):
    
    evaluate(population)
    population.sort(key = lambda x: x.fitness, reverse = True)
    elite = population[0:ELITISM]
    
    print("Best fitness " + str(population[0].fitness))
    print("Average fitness " + str(np.mean([ind.fitness for ind in population])))
    
    new_population = elite
    for i in range((POPULATION_SIZE-ELITISM)//2):
        p1 = choose_parent(population)
        p2 = choose_parent(population)
        offsprings = crossover(p1, p2)
        new_population = new_population + offsprings
        
    for i in range(ELITISM,POPULATION_SIZE):
        new_population[i] = mutate(new_population[i])
    return new_population

def run_evolution(population, start):
    
    elite = population[0]
    for i in range(start,200000):
        population = evolution_step(population)
        if i%50 == 0:
            #np.save('best_' + str(i), population[0])
            save(population, i)
            #simulate(population[0], False,1000)

def get_reward(weights):
    return simulate(weights,True,SIM_TIME,STAIR_HEIGHT)

def run_ES(population,i):
    model = population[0].genome

    es = EvolutionStrategy(model, get_reward, population_size=POPULATION_SIZE, sigma=0.1, learning_rate=0.03, decay=0.996, num_threads=1)
    es.run(5000, print_step=5, start=i)
    optimized = es.get_weights()
    
def run_CMA(ind):
    
    def fitness(Individual):
        return -1*simulate(Individual, True, SIM_TIME, STAIR_HEIGHT)
    
    height = 0.01
    bestind = ind
    while height <= 0.4:
        STAIR_HEIGHT = height
        print("--------------{}----------------".format(STAIR_HEIGHT))
        es = cma.CMAEvolutionStrategy(bestind, 0.5,{'bounds':[-3,3]})
        while True:
            X = es.ask()
            fit = [fitness(x) for x in X]
            es.tell(X, fit)
            best = es.best
            es.disp()
            if best.f < -1:
                bestind = best.x
                np.save("ind_{}".format(height), bestind)
                break

            #es.optimize(fitness)
        height += 0.02
        
    
    
def defineRobot(name):
    global MATRIX_SHAPE,GENOME_LENGTH, ROBOT_TYPE
    
    if name == "Robot":
        robot = Robot.Robot(None,None)
    elif name == "OriginalRobot":
        robot = OriginalRobot.Robot(None,None)
    elif name == "SimpleRobot":
        robot = SimpleRobot.Robot(None,None)
    elif name == "DenseRobot":
        robot =  DenseRobot.Robot(None,None)
        
    MATRIX_SHAPE = robot.MATRIX_SHAPE
    GENOME_LENGTH = robot.GENOME_LENGTH
    ROBOT_TYPE = name
    
def save(population,i):
    population = [ind.genome for ind in population]
    np.save('population_'+str(i), population)

def load(file):
    #population = [Individual(genome) for genome in np.load(args.genomes)]
    population = [Individual(np.load(args.genomes))]
    return population

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--genomes", type=str, help="file with the npy saved genomes")
    parser.add_argument("--robot", type=str,default="OriginalRobot", help="name of the file defining robot")
    parser.add_argument("--test", type=bool, default = False)
    args = parser.parse_args()
    defineRobot(args.robot)
    if args.genomes:
        population = load(args.genomes)
        start = int(args.genomes.split('_')[1].split('.')[0])
        STAIR_HEIGHT = STAIR_HEIGHT + (start/1000) * 0.02
    else:
        population = initializePopulation()
        start = 0
        
    if args.test:
        print("Fitness: ")
        print(STAIR_HEIGHT)
        print(simulate(population[0].genome, False, SIM_TIME, STAIR_HEIGHT))
    else:
        #run_evolution(population,start)
        #run_ES(population,start)
        run_CMA(population[0].genome)
   

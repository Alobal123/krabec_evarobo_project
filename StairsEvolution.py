import pyrosim
import numpy as np
import Stairs
import argparse

import Robot
import OriginalRobot

ROBOT_TYPE = None
MATRIX_SHAPE = None
GENOME_LENGTH = None

POPULATION_SIZE = 25

MUTATION_PROBABILITY = 0.1
MUTATION_VARIANCE = 0.3

CROSSOVER_PROBABILITY = 0.5
TOURNAMENT_PROBABILITY = 0.8

def simulate(individual, blind, time):
    sim = pyrosim.Simulator(eval_time=time,play_blind=blind,debug=False, xyz = [-1,-1,1], hpr=[45,-27.5,0.0])
    builder = Stairs.StairBuilder(sim,[0.6,0.6,0],0.2)
    #builder.build(25)
    

    weight_matrix = np.reshape(individual, MATRIX_SHAPE)
    if ROBOT_TYPE == "Robot":
        robot = Robot.Robot(sim,weight_matrix)
    elif ROBOT_TYPE == "OriginalRobot":
        robot = OriginalRobot.Robot(sim,weight_matrix)
    fitness_sensor = robot.build()
    
    sim.create_collision_matrix('intra')
    sim.start()
    results = sim.wait_to_finish()

    return min(sim.get_sensor_data(fitness_sensor, svi=1)[-1], sim.get_sensor_data(fitness_sensor, svi=0)[-1])
    #return sim.get_sensor_data(fitness_sensor, svi=0)[-1]

def initializeIndividual():
    individual = np.random.rand(GENOME_LENGTH)
    individual[:] = individual[:]*2.-1.
    return individual
    
def initializePopulation():
    population = [initializeIndividual() for _ in range(POPULATION_SIZE)]
    return population

def mutate(individual):
    for i in range(GENOME_LENGTH):
        if np.random.rand() < MUTATION_PROBABILITY:
            individual[i] = individual[i] + np.random.normal(0,MUTATION_VARIANCE)
    return individual

def crossover(parent1, parent2):
    if np.random.rand() < CROSSOVER_PROBABILITY:
        index = np.random.randint(1, GENOME_LENGTH-1)
        child1 = np.concatenate((parent1[0:index], parent2[index:]))
        child2 = np.concatenate((parent2[0:index], parent1[index:]))
        return [child1, child2]
    return [np.copy(parent1), np.copy(parent2)]
 
def evaluate(population):
    return [simulate(individual, True, 350) for individual in population]

def Tournament(individual1,fitness1, individual2, fitness2):
    better = individual1 if fitness1 > fitness2 else individual2
    worse = individual1 if fitness1 <= fitness2 else individual2
    if np.random.rand() < TOURNAMENT_PROBABILITY:
        return better
    return worse

def roulette(population, fitnesses):
        max     = sum(fitnesses)
        pick    = np.random.rand() * max
        current = 0
        for i in range(POPULATION_SIZE):
            current += fitnesses[i]
            if current > pick:
                return population[i]
            
def choose_parent(population, fitnesses):
    i1 = np.random.randint(0,POPULATION_SIZE)
    i2 = np.random.randint(0,POPULATION_SIZE)
    return Tournament(population[i1], fitnesses[i1],population[i2], fitnesses[i2])
    #return roulette(population, fitnesses)

def evolution_step(population):
    
    fitnesses = evaluate(population)
    elite_index = int(np.argmax(fitnesses))
    elite = population[elite_index]
    
    print("Best fitness " + str(fitnesses[elite_index]))
    print("Average fitness " + str(np.mean(fitnesses)))
    
    new_population = [elite]
    for i in range(POPULATION_SIZE//2):
        p1 = choose_parent(population, fitnesses)
        p2 = choose_parent(population, fitnesses)
        offsprings = crossover(p1, p2)
        new_population = new_population + offsprings

    for i in range(1,POPULATION_SIZE):
        new_population[i] = mutate(new_population[i])
    return new_population

def run_evolution(population, start):
    
    elite = population[0]
    for i in range(start,200000):
        population = evolution_step(population)
        if i%50 == 0 and i>1:
            #np.save('best_' + str(i), population[0])
            np.save('population_'+str(i), population)
            #simulate(population[0], False,1000)


def defineRobot(name):
    global MATRIX_SHAPE,GENOME_LENGTH, ROBOT_TYPE
    
    if name == "Robot":
        robot = Robot.Robot(None,None)
    elif name == "OriginalRobot":
        robot = OriginalRobot.Robot(None,None)
        
    MATRIX_SHAPE = robot.MATRIX_SHAPE
    GENOME_LENGTH = robot.GENOME_LENGTH
    ROBOT_TYPE = name

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--genomes", type=str, help="file with the npy saved genomes")
    parser.add_argument("--robot", type=str,default="OriginalRobot", help="name of the file defining robot")
    args = parser.parse_args()
    defineRobot(args.robot)
    if args.genomes:
        population = np.load(args.genomes) 
        start = int(args.genomes.split('_')[1].split('.')[0])
        
    else:
        population = initializePopulation()
        start = 0
    run_evolution(population,start)
   
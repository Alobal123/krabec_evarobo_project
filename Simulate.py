import pyrosim
import numpy as np
import Stairs
import Robot

def simulate():
    sim = pyrosim.Simulator(eval_time=1000, debug=False, xyz = [-2,0,1], hpr=[0,-27.5,0.0])
    builder = Stairs.StairBuilder(sim,[1,0,0],0.2)
    builder.build(20)
    
    num_sensors = 4
    num_motors = 8
    weight_matrix = np.random.rand(num_sensors+num_motors,
                                   num_sensors+num_motors, 4)
    weight_matrix[:, :, 0:1] = weight_matrix[:, :, 0:1]*2.-1.
    print(weight_matrix)
    
    robot = Robot.Robot(sim,weight_matrix)
    robot.build()
    
    sim.create_collision_matrix('intra')
    sim.start()
    
    
if __name__ == "__main__":
    simulate()
import pyrosim
import Stairs

def simulate():
    sim = pyrosim.Simulator(eval_time=1000, debug=True, xyz = [-1,0,0.5], hpr=[0,-27.5,0.0])
    builder = Stairs.StairBuilder(sim,[0,0,0],0.1)
    builder.build(10)
    sim.start()
    
    
if __name__ == "__main__":
    simulate()
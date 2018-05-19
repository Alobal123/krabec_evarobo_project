import pyrosim
import math

class StairBuilder:
    
    STAIR_HEIGHT = 0.8
    
    def __init__(self, simulator,beginning_coordinates, size): 
        self.beginning_coordinates = beginning_coordinates
        self.size = size
        self.simulator = simulator
    
    def build(self, number):
        for i in range(number):
            x = self.beginning_coordinates[0]+i*self.size*2
            y = self.beginning_coordinates[1]+i*self.size*2
            z = self.beginning_coordinates[2]+(i+1)*self.size/2
            
            length = 6
            height = self.size*2*math.sqrt(2)
            width = (i+1)*self.size*self.STAIR_HEIGHT
            
            z = self.beginning_coordinates[2]+width/2
            
            self.simulator.send_box(x=x, y=y, z=z, r1=1, r2=1, r3=0, mass=10000, length=length,
                                     width = width, height = height,collision_group='env')
            
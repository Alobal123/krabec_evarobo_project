import pyrosim
import math

class StairBuilder:
    

    def __init__(self, simulator,beginning_coordinates, size): 
        self.beginning_coordinates = beginning_coordinates
        self.size = size
        self.simulator = simulator

    def build(self, number, stair_height):
        for i in range(number):
            x = self.beginning_coordinates[0]+i*self.size*2
            y = self.beginning_coordinates[1]+i*self.size*2
            length = 6
            height = self.size*2*math.sqrt(2)
            width = (i+1)*self.size*stair_height
            z = self.beginning_coordinates[2]+width/2
            self.simulator.send_box(x=x, y=y, z=z, r1=1, r2=1, r3=0, mass=10000, length=length,
                                 width = width, height = height,collision_group='env')
            
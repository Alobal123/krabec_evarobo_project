import pyrosim

class StairBuilder:
    
    def __init__(self, simulator,beginning_coordinates, size): 
        self.beginning_coordinates = beginning_coordinates
        self.size = size
        self.simulator = simulator
    
    def build(self, number):
        for i in range(number):
            x = self.beginning_coordinates[0]+i*self.size*3
            y = self.beginning_coordinates[1]
            z = self.beginning_coordinates[2]+(i+1)*self.size/2
            length = 6
            width = self.size*3
            height = (i+1)*self.size
            self.simulator.send_box(x=x, y=y, z=z, length=length, width = width, height = height,collision_group='env')
            
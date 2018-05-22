import numpy as np
import math
import pyrosim



class Robot:
    Height = 0.3
    EPS = 0.05
    MATRIX_SHAPE = (4,3,2)
    GENOME_LENGTH = 4*3*2
    
    def __init__(self, simulator, weight_matrix):
        self.simulator = simulator
        self.weight_matrix = weight_matrix
    
    def build(self):
        main_body = self.simulator.send_box(x=0, y=0, z=self.Height+self.EPS,
                             length=self.Height, width=self.Height,
                             height=self.EPS*2.0, mass=1, collision_group='robot')
        

        
        # id arrays
        thighs = [0]*4
        shins = [0]*4
        hips = [0]*4
        knees = [0]*4
        foot_sensors = [0]*4
        hip_sensors = [0]*4
        knee_sensors = [0]*4
        sensor_neurons = [0]*12
        motor_neurons = [0]*8
    
        delta = float(math.pi)/2.0
            # quadruped is a box with one leg on each side
        # each leg consists thigh and shin cylinders
        # with hip and knee joints
        # each shin/foot then has a touch sensor
        for i in range(4):
            theta = delta*i
            x_pos = math.cos(theta)*self.Height
            y_pos = math.sin(theta)*self.Height
    
            thighs[i] = self.simulator.send_cylinder(x=x_pos, y=y_pos, z=self.Height+self.EPS,
                                          r1=x_pos, r2=y_pos, r3=0,
                                          length=self.Height, radius=self.EPS, capped=True
                                          )
    
            hips[i] = self.simulator.send_hinge_joint(main_body, thighs[i],
                                           x=x_pos/2.0, y=y_pos/2.0, z=self.Height+self.EPS,
                                           n1=-y_pos, n2=x_pos, n3=0,
                                           lo=-math.pi/4.0, hi=math.pi/4.0,
                                           speed=1.0)
            hip_sensors[i] = self.simulator.send_proprioceptive_sensor(hips[i])
            sensor_neurons[3*i] = self.simulator.send_sensor_neuron(hip_sensors[i])
            motor_neurons[i] = self.simulator.send_motor_neuron(joint_id=hips[i])
    
            x_pos2 = math.cos(theta)*1.5*self.Height
            y_pos2 = math.sin(theta)*1.5*self.Height
    
            shins[i] = self.simulator.send_cylinder(x=x_pos2, y=y_pos2, z=(self.Height+self.EPS)/2.0,
                                         r1=0, r2=0, r3=1,
                                         length=self.Height, radius=self.EPS,
                                         mass=1., capped=True)
    
            knees[i] = self.simulator.send_hinge_joint(thighs[i], shins[i],
                                            x=x_pos2, y=y_pos2, z=self.Height+self.EPS,
                                            n1=-y_pos, n2=x_pos, n3=0,
                                            lo=-math.pi/4.0, hi=math.pi/4.0)
    
            knee_sensors[i] = self.simulator.send_proprioceptive_sensor(knees[i])
            sensor_neurons[3*i+1] = self.simulator.send_sensor_neuron(knee_sensors[i])
            
            motor_neurons[i+4] = self.simulator.send_motor_neuron(knees[i])
            foot_sensors[i] = self.simulator.send_touch_sensor(shins[i])
            sensor_neurons[3*i+2] = self.simulator.send_sensor_neuron(foot_sensors[i])
    
            # developing synapses linearly change from the start value to the
            # end value over the course of start time to end time
            # Here we connect each sensor to each motor, pulling weights from
            # the weight matrix
            for source_id in range(3):
                for target_id in range(2):
                    source = source_id
                    target = target_id
                    weight = self.weight_matrix[i,source, target]
                    self.simulator.send_synapse(sensor_neurons[source_id], motor_neurons[target_id],weight)
                                               
        positions_sensor = self.simulator.send_position_sensor(main_body)
        return positions_sensor
   


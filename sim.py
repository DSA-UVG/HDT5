import random as rd
import simpy
import numpy as np
import matplotlib.pyplot as plt

RANDOM_SEED = 42

class ProcessSimulator:
    def __init__(self, env: simpy.Environment, ram_capacity: int, num_cpus: int, cpu_speed: int):
        self.env = env
        self.ram = simpy.Container(env, init=ram_capacity, capacity=ram_capacity)
        self.cpu = simpy.Resource(env, capacity=num_cpus)
        self.cpu_speed = cpu_speed
        self.process_times = []
    def run(self, num_processes, interval):
        def process_generator():
            for i in range(num_processes):
                self.env.process(self.process(f'Proceso {i}'))
                yield self.env.timeout(rd.expovariate(1.0 / interval))
        
        self.env.process(process_generator())
        self.env.run()
        return self.process_times
   

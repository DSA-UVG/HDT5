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

    def process(self, name):
        memory_needed = rd.randint(1, 10)
        total_instructions = rd.randint(1, 10)
        start_time = self.env.now
        
        # Se obtiene la memoria necesaria
        with self.ram.get(memory_needed) as req:
            yield req
            
            while total_instructions > 0:
                with self.cpu.request() as req_cpu:
                    yield req_cpu
                    executed = min(self.cpu_speed, total_instructions)
                    total_instructions -= executed
                    yield self.env.timeout(1)
                    
                    if total_instructions > 0 and rd.randint(1, 21) == 1:
                        yield self.env.timeout(1) # Se interrumpe el proceso por 1 unidad de tiempo
            
        self.ram.put(memory_needed)
        self.process_times.append(self.env.now - start_time)
   

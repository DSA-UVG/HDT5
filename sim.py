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
   
def run_simulation_scenarios(process_counts: list, intervals: list, scenarios: list):
    rd.seed(RANDOM_SEED)
    
    # Simular escenarios
    results = {}
    for scenario in scenarios:
        scenario_results = {}
        for interval in intervals:
            interval_results = {}
            for num_processes in process_counts:
                env = simpy.Environment()
                simulator = ProcessSimulator(env, scenario['ram'], scenario['num_cpus'], scenario['cpu_speed'])
                process_times = simulator.run(num_processes, interval)
                interval_results[num_processes] = {'avg_time': np.mean(process_times), 'std_time': np.std(process_times)}
            scenario_results[interval] = interval_results
        results[f"RAM:{scenario['ram']}, CPU_speed:{scenario['cpu_speed']}, CPUs:{scenario['num_cpus']}"] = scenario_results
    
    # Graficar resultados
    plt.figure(figsize=(15, 10))
    for scenario, scenario_data in results.items():
        for interval, interval_data in scenario_data.items():
            plt.subplot(len(results), len(scenario_data), list(results.keys()).index(scenario) * len(scenario_data) + list(scenario_data.keys()).index(interval) + 1)
            process_counts = list(interval_data.keys())
            avg_times = [interval_data[count]['avg_time'] for count in process_counts]
            plt.plot(process_counts, avg_times, marker='o')
            plt.title(f'{scenario}, Interval: {interval}')
            plt.xlabel('Number of Processes')
            plt.ylabel('Average Process Time')
    
    plt.tight_layout()
    plt.show()

def main():
    # Numero de procesos a simular
    process_counts = [25, 50, 100, 150, 200]
    # Intervalos de tiempo para la generacion de procesos
    intervals = [10, 5, 1]
    # Escenarios a simular
    scenarios = [
        {'ram': 100, 'cpu_speed': 3, 'num_cpus': 1},
        {'ram': 200, 'cpu_speed': 3, 'num_cpus': 1},
        {'ram': 100, 'cpu_speed': 6, 'num_cpus': 1},
        {'ram': 100, 'cpu_speed': 3, 'num_cpus': 2}
    ]

    run_simulation_scenarios(process_counts, intervals, scenarios)

main()
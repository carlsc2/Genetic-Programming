"""
gptest.py

A test of genetic programming with python and brainfuck.

"""
import cbrainfuck
from genalg import GeneticAlgorithm

def evaluate(chromo):
    #try to evaluate the code
    target_string='marmelade'
    try:
        result = cbrainfuck.evaluate(chromo.s,.005)
        if len(result) != 0:
            f = 0
            for i in range(max(len(target_string),len(result))):
                try:
                    f += abs(ord(result[i]) - ord(target_string[i]))
                except IndexError:
                    f += 1000
            chromo.fitness = f
        else:
            chromo.fitness = 0x454d505459
    except Exception as e:
        print(e)
        chromo.fitness = 0x4552524f52

def main():
    genetic_code = ['>','<','+','-','.',',','[',']','#']
    GA = GeneticAlgorithm(genetic_code,
                          evaluate,
                          use_elitism=True,
                          positive_fitness=False,
                          selection_function='tournament_16',
                          crossover_function='delimited',
                          #crossover_function='uniform',
                          chromosome_size=-1)
    GA.run(None,100,max_fitness=0)
if __name__ == "__main__":
    main()
    #import cProfile
    #cProfile.run("main()",sort=1)
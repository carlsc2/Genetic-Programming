"""
gptest.py

A test of genetic programming with python and brainfuck.

"""

import brainfuck
from genalg import GeneticAlgorithm

#note: it turns out edit distance is a terrible fitness function
#because it can only close the gap so much and the algorithm
#doesn't know where to go from there
def edit_distance(s1, s2):
    m=len(s1)+1
    n=len(s2)+1

    tbl = {}
    for i in range(m): tbl[i,0]=i
    for j in range(n): tbl[0,j]=j
    for i in range(1, m):
        for j in range(1, n):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            tbl[i,j] = min(tbl[i, j-1]+1, tbl[i-1, j]+1, tbl[i-1, j-1]+cost)

    return tbl[i,j]

target_string = "marmelade"

def evaluate(chromo):
    #try to evaluate the code
    try:
        result = brainfuck.evaluate(chromo.s,.05)
        if len(result) != 0:
            #print("result: ",result)
            #chromo.fitness = edit_distance(result,target_string) + abs(len(result) - len(target_string))
            f = 0
            for i in range(max(len(target_string),len(result))):
                #print("i: ",i)
                try:
                    f += abs(ord(result[i]) - ord(target_string[i]))
                except IndexError:
                    f += 1000
            chromo.fitness = f
        else:
            chromo.fitness = 0x454d505459
    except Exception as e:
        ##print("Exception: ",e)
        chromo.fitness = 0x4552524f52

def main():
    genetic_code = ['>','<','+','-','.',',','[',']']
    GA = GeneticAlgorithm(genetic_code,
                          evaluate,
                          use_elitism=True,
                          positive_fitness=False,
                          selection_function='tournament',
                          chromosome_size=-1)
    GA.run(1000,50,'+,+>++[++,+[<<+++<<>+<+,+],<+->.,.[++.[.---..---[---...')


if __name__ == "__main__":
    main()
    #import cProfile
    #cProfile.run("main()",sort=1)
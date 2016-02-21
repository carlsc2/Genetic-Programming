"""
gptest.py

A test of genetic programming with python and brainf__k.
"""

import brainf__k
from genalg import GeneticAlgorithm

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

target_string = "hello_world"

def evaluate(chromo):
    #try to evaluate the code
    try:
        result = brainf__k.evaluate(chromo.s,.1)
    except:
        result = ''

    #evaluate fitness
    if result:
        chromo.fitness = edit_distance(result,target_string)
    else:
        chromo.fitness = 100000

def main():
    genetic_code = ['>','<','+','-','.',',','[',']']
    GA = GeneticAlgorithm(genetic_code,evaluate,True,False,'tournament')
    GA.run(100,100)


if __name__ == "__main__":
    main()

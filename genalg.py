"""
genalg.py

Contains functionality for multi-purpose genetic algorithm.

"""

import random
import cbrainfuck
import time
import itertools


class Chromosome:
    """Chromosome class; stores gene and fitness data"""

    def __init__(self, genes=""):
        self.s = genes
        self.fitness = 0


class GeneticAlgorithm():

    """A general-purpose genetic algorithm class

    The evaluate function should be overridden for each specific use.

    """

    def __init__(self, genetic_alphabet,
                 eval_func,
                 use_elitism=False,
                 positive_fitness=True,
                 selection_function="roulette",
                 crossover_function="one_point",
                 chromosome_size=-1):
        """
        genetic_alphabet (list<string>):
            This is a list of all chars in the genetic alphabet used to define
            the chromosomes. This is used for mutation purposes.

        eval_func (function):
            This is the function to use for chromosome evaluation.Note: this
            function should take one argument (the chromosome object) and set
            its fitness score. Does not return anything.

        use_elitism (bool):
            Flag to determine whether or not the best chromosome for each
            population is passed on (as-is) to the next generation.

        positive_fitness (bool):
            True if higher value == more fit
            False if lower value == more fit

        selection_function (string):
            Determines which selection function to use.
            Currently supported:
                'roulette' => roulette wheel sampling
                'tournament' => tournament selection

            Note: For tournament selection the default tournament size
            is 2. To use a different size, use 'tournament_x' where x
            is the tournament size.

        crossover_function (string):
            Determines which crossover function to use.
            Currently supported:
                'one_point' => perform crossover at one point
                'uniform' => perform crossover at multiple points,
                             based on mixing ratio. Use uniform_x
                             to define mixing ratio (0 <= x <= 1)
                'delimited' => delimiter-based, will do crossover
                               on partitions, in order. Delimiter must
                               be part of the genetic alphabet. Use
                               delimited_x to specify x as delimiter.

        chromosome_size (int):
            If set to -1, chromosomes can change in size
            via mutation.
            Otherwise, the chromosomes will be limited to
            this size and will only be mutated via substitution.

        logfile(string):
            If specified, data will be written to this file
            for each generation.

        """
        self.genetic_alphabet = genetic_alphabet
        self.crossover_rate = .9
        self.mutation_rate = .05
        self.evaluate = eval_func
        self.use_elitism = use_elitism
        self.positive_fitness = positive_fitness
        self.chromosome_size = chromosome_size

        if selection_function == 'roulette':
            self.selection_function = self.roulette_selection
        elif 'tournament' in selection_function:
            tmp = selection_function.split("_")
            if len(tmp) == 2:
                k = int(tmp[-1]) #get tournament size
                self.selection_function = lambda pop: self.tournament_selection(pop,k)
            else:
                self.selection_function = self.tournament_selection
        else:
            print(("%s is not a supported selection function, "
                   "defaulting to roulette wheel sampling") % selection_function)
            self.selection_function = self.roulette_selection

        if crossover_function == 'one_point':
            self.crossover_function = self.one_point_crossover
        elif 'uniform' in crossover_function:
            tmp = crossover_function.split("_")
            if len(tmp) == 2:
                mr = float(tmp[-1]) #get mixing ratio
                self.crossover_function = lambda ch1,ch2: self.uniform_crossover(ch1,ch2,mr)
            else:
                self.crossover_function = self.uniform_crossover
        elif 'delimited' in crossover_function:
            tmp = crossover_function.split("_")
            if len(tmp) == 2:
                self.crossover_function = lambda ch1,ch2: self.delimited_crossover(ch1,ch2,tmp[-1])
            else:
                self.crossover_function = self.delimited_crossover

    def mutate(self, chromo):
        """mutate a chromosome and return a new, mutated one

        possible mutations (based on genetic alphabet):
            - insertion
            - deletion
            - substitution
        """

        def choose_mutation():
            def insertion(x):
                return random.choice(self.genetic_alphabet) + x

            def deletion(x):
                return ""

            def substitution(x):
                return random.choice(self.genetic_alphabet)

            if self.chromosome_size == -1:
                return random.choice((insertion,deletion,substitution))
            else:
                return substitution

        ch = "" # create new genes for chromo
        for gene in chromo.s:
            if random.random() < self.mutation_rate: # do mutation
                ch += choose_mutation()(gene)
            else:
                ch += gene

        return Chromosome(ch)

    def one_point_crossover(self, ch1, ch2):
        """Perform one point crossover between two chromosomes

        The chromosomes can be different sizes; the crossover
        point is proportional to each.

        """

        ch1 = ch1.s
        ch2 = ch2.s
        r = random.random()
        r1 = int(len(ch1) * r)
        r2 = int(len(ch2) * r)
        return Chromosome(ch1[:r1] + ch2[r2:]), Chromosome(ch2[:r2] + ch1[r1:])

    def uniform_crossover(self, ch1, ch2, mixing_ratio=.5):
        """Randomly partition the chromosomes and swap their partitions

        The chromosomes can be different sizes; it is ratio based,

        """
        ch1 = ch1.s
        ch2 = ch2.s

        len1 = len(ch1)
        len2 = len(ch2)
        crosspoints = sorted([random.random() for x in range(int(min(len1,len2)*mixing_ratio))])
        prev1 = prev2 = i = 0
        out1 = ""
        out2 = ""
        for i,x in enumerate(crosspoints):
            tmp1 = int(len1*x)
            tmp2 = int(len2*x)
            if i&1:
                out1 += ch1[prev1:tmp1]
                out2 += ch2[prev2:tmp2]
            else:
                out1 += ch2[prev2:tmp2]
                out2 += ch1[prev1:tmp1]
            prev1 = tmp1
            prev2 = tmp2
        if (i+1)&1:
            out1 += ch1[prev1:]
            out2 += ch2[prev2:]
        else:
            out1 += ch2[prev2:]
            out2 += ch1[prev1:]

        return Chromosome(out1), Chromosome(out2)

    def delimited_crossover(self, ch1, ch2, delimiter="#"):
        """Partition the chromosomes and swap their partitions based on delimiter

        The chromosomes can be different sizes; it is ratio based,

        """

        p1 = ch1.s.split(delimiter)
        p2 = ch2.s.split(delimiter)

        o1 = ""
        o2 = ""

        for i in range(min(len(p1),len(p2))):
            if i&1:
                o1 += p1[i]
                o2 += p2[i]
            else:
                o1 += p2[i]
                o2 += p1[i]

        return Chromosome(o1),Chromosome(o2)



    def roulette_selection(self, population):
        """Roulette wheel sampling

        Note: Roulette wheel cannot be used for minimization because of the
        scaling. It also cannot be used when there are negative or null
        fitnesses because their probability would be negative or null.
        """
        maxval = sum([c.fitness for c in population])
        pick = random.uniform(0, maxval)
        current = 0
        for chromosome in population:
            current += chromosome.fitness
            if current > pick:
                return chromosome
        return population[0]

    def tournament_selection(self, population, k=4):
        """Tournament selection

        Randomly selects the most fit candidate from a tournament of size k.
        This works for both maximizing and minimizing fitnesses.

        """
        best = random.choice(population)
        for i in range(k):
            chromo = random.choice(population)
            if self.positive_fitness and chromo.fitness > best.fitness:
                best = chromo
            elif not self.positive_fitness and chromo.fitness < best.fitness:
                best = chromo
        return best

    def breed(self, ch1, ch2):
        """Perform crossover and mutation based on two chromosomes"""
        # rate dependent crossover of selected chromosomes
        if random.random() < self.crossover_rate:
            newCh1, newCh2 = self.crossover_function(ch1, ch2)
        else:
            newCh1, newCh2 = ch1, ch2

        # mutate crossovered chromos
        newnewCh1 = self.mutate(newCh1)
        newnewCh2 = self.mutate(newCh2)

        return newnewCh1, newnewCh2

    def evaluate(self, chromo):
        """evaluate a chromosome, return the fitness score

        This function is meant to be overwritten for each specific use.
        """
        chromo.fitness = 0

    def generate_population(self, popSize):
        """generate and return the initial population"""
        chromos = []
        for eachChromo in range(popSize):
            chromo = Chromosome()
            if self.chromosome_size == -1:
                # arbitrary range of starting chromosome size
                numgenes = random.randint(5, 50)
            else:
                numgenes = self.chromosome_size
            for bit in range(numgenes):
                chromo.s += random.choice(self.genetic_alphabet)
            chromos.append(chromo)
        return chromos

    def generate_seeded_population(self, popSize, seed):
        """generate and return the initial population based on a seed gene"""
        chromos = [Chromosome(seed)]  # set first one as non-mutated
        for eachChromo in range(popSize - 1):
            chromos.append(self.mutate(Chromosome(seed)))
        return chromos

    def run(self, max_iterations=1000,
                  population_size=100,
                  seed=None,
                  fitness_threshold=None,
                  max_fitness=None,
                  logfile=None):
        """Run the genetic algorithm

        max_iterations(int):
            the number of generations to run
            if set to None, will run until max_fitness is reached
        population_size(int):
            the number of chromosomes per population
        seed(string):
            if specified, will create the initial population
            from an existing gene
        fitness_threshold(float):
            will discard anything with worse fitness than the
            threshold (so as not to pass down genes)
        max_fitness(float):
            if set, will break if that fitness is reached
        logfile(string):
            If specified, data will be written to this file
            for each generation.
        """

        logging = True if logfile != None else False

        if max_iterations == None and max_fitness == None:
            print("ERROR: no max fitness set. Cannot run indefinitely.")
            return

        if logging:
            outfile = open(logfile,"w+")
            outfile.write("GA run params:\n")
            outfile.write("\tmax_iterations: %d\n"%max_iterations)
            outfile.write("\tpopulation_size: %d\n"%population_size)
            outfile.write("\tseed: %r\n"%seed)
            outfile.write("\tfitness_threshold: %r\n"%fitness_threshold)
            outfile.write("\tmax_fitness: %r\n"%max_fitness)
            outfile.write("\n")


        start_time = time.time()
        def iterate_pop(pop):
            # iterate the current population

            newpop = []

            # elitism
            if self.use_elitism:  # use 5% of pop for elitism
                newpop.extend(pop[:int(population_size / 20)])
            if fitness_threshold is not None:
                for chromo in pop:
                    if self.positive_fitness and chromo.fitness < fitness_threshold:
                        pop.remove(chromo)
                    elif not self.positive_fitness and chromo.fitness > fitness_threshold:
                        pop.remove(chromo)

            if len(newpop) == 0:
                logstr = "Population extinct. Stopping."
                print(logstr)
                if logging:
                    outfile.write(logstr)
                return

            while len(newpop) < population_size:
                ch1 = self.selection_function(pop)
                ch2 = self.selection_function(pop)
                # breed them to create two new chromosomes
                ch1, ch2 = self.breed(ch1, ch2)
                newpop.append(ch1)  # and append to new population
                newpop.append(ch2)
            return newpop

        # initialize population
        if seed:
            pop = self.generate_seeded_population(population_size, seed)
        else:
            pop = self.generate_population(population_size)

        try:
            best = Chromosome()
            for i in itertools.count():
                i_start = time.time()
                # assign fitness values to all chromosomes
                for chromosome in pop:
                    self.evaluate(chromosome)
                avgf = sum([chromo.fitness for chromo in pop]) / len(pop)
                # sort population by fitness
                pop = sorted(pop, key=lambda x: x.fitness,
                             reverse=self.positive_fitness)
                best = pop[0]

                if max_fitness != None:
                    if self.positive_fitness and best.fitness >= max_fitness:
                        break
                    elif not self.positive_fitness and best.fitness <= max_fitness:
                        break

                logstr = "Generation %d:\n\tTime: %.5fs\n\tMax fitness: %.5f\n\tAverage Fitness: %.5f"%(i + 1, time.time()-i_start, best.fitness, avgf)
                print(logstr)
                if logging:
                    outfile.write(logstr)

                # iterate the population
                pop = iterate_pop(pop)

                if max_iterations != None and i > max_iterations:
                    break
        finally:
            # sort final population by fitness
            logstr = "Generation %d:\n\tTotal Runtime: %.5fs\n\tBest result:\n\tchromosome: %s\n\tfitness: %.5f"%(i + 1, time.time() - start_time, best.s, best.fitness)
            print(logstr)
            if logging:
                outfile.write(logstr)

            output_string = ''
            try:
                output_string = cbrainfuck.evaluate(best.s,1)
            finally:
                if output_string == '':
                    print('Output did not produce a string.')
                else:
                    print("Output of best result, (first 100 chars):%s" % output_string[:100])


"""
genalg.py

Contains functionality for multi-purpose genetic algorithm.

"""

import random
import brainfuck


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

        chromosome_size (int):
            If set to -1, chromosomes can change in size
            via mutation.
            Otherwise, the chromosomes will be limited to
            this size and will only be mutated via substitution.

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
                options = {0: insertion, 1: deletion, 2: substitution}
                return options[random.randint(0, 2)]
            else:
                return substitution

        ch = ""  # create new genes for chromo
        for i in chromo.s:
            if random.random() < self.mutation_rate:  # do mutation
                ch += choose_mutation()(i)
            else:  # add previous char
                ch += i

        return Chromosome(ch)

    def crossover(self, ch1, ch2):
        """Perform genetic crossover between two chromosomes


        The chromosomes can be different sizes; the crossover
        point is proportional to each.

        """
        a = Chromosome()
        b = Chromosome()
        ch1 = ch1.s
        ch2 = ch2.s
        r = random.random()
        r1 = int(len(ch1) * r)
        r2 = int(len(ch2) * r)
        a.s = ch1[:r1] + ch2[r2:]
        b.s = ch2[:r2] + ch1[r1:]
        return a, b

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

    def tournament_selection(self, population, k=2):
        """Tournament selection

        Randomly selects the most fit candidate from a tournament of size k.
        This works for both maximizing and minimizing fitnesses.

        """
        best = None
        for i in range(k):
            chromo = random.choice(population)
            if not best:
                best = chromo
            elif self.positive_fitness and chromo.fitness > best.fitness:
                best = chromo
            elif not self.positive_fitness and chromo.fitness < best.fitness:
                best = chromo
        return best

    def breed(self, ch1, ch2):
        """Perform crossover and mutation based on two chromosomes"""
        # rate dependent crossover of selected chromosomes
        if random.random() < self.crossover_rate:
            newCh1, newCh2 = self.crossover(ch1, ch2)
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

    def run(self, max_iterations=1000, population_size=100, seed=None):
        """Run the genetic algorithm

        max_iterations is the number of generations to run
        population_size is the number of chromosomes per population
        seed, if specified, will create the initial population
        from an existing gene
        """
        def iterate_pop(pop):
            # iterate the current population

            newpop = []

            # elitism
            if self.use_elitism:  # use 5% of pop for elitism
                newpop.extend(pop[:int(population_size / 20)])
            while len(newpop) < population_size:
                ch1 = self.selection_function(pop)
                ch2 = self.selection_function(pop)
                # breed them to create two new chromosomes
                ch1, ch2 = self.breed(ch1, ch2)
                newpop.append(ch1)  # and append to new population
                newpop.append(ch2)
            return newpop

        if seed:
            pop = self.generate_seeded_population(
                population_size, seed)  # initialize population
        else:
            pop = self.generate_population(
                population_size)  # initialize population

        best = Chromosome()
        for i in range(max_iterations):
            # assign fitness values to all chromosomes
            for chromosome in pop:
                self.evaluate(chromosome)

            avgf = sum([chromo.fitness for chromo in pop]) / len(pop)
            # sort population by fitness
            pop = sorted(pop, key=lambda x: x.fitness,
                         reverse=self.positive_fitness)
            best = pop[0]
            print("Generation %d: Max fitness: %.5f Average Fitness: %.5f" %
                  (i + 1, best.fitness, avgf))

            # iterate the population
            pop = iterate_pop(pop)

        # sort final population by fitness
        print("Best result:\n chromosome: %s \n fitness: %.5f" %
              (best.s, best.fitness))
        output_string = brainfuck.execute(best.s,1)
        if(output_string==''):
            print('Output did not produce a string.')
        else:
            print("Output of best result, truncated:%s") % output_string[:100]


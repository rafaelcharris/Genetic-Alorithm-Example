# Packages
import random
import math


## Original Parameters ##
#########################

periods = 10
#Define grid
rows_m = 100 # m rows
cols_n = 100 # n columns
black_dots = 100
value_per_dot = 1
columns_harvest = 10
gamma = 1
kappa = 0.01021
alpha = 32
c = 464.53
mutate_prob = 0.1
#Health
health = 70
slope = 1
base_degen = 10

## Class test parameters ##
###########################
periods  = 8
rows_m = 100 # m rows
cols_n = 100 # n columns
value_per_dot = 1
columns_harvest = 10
black_dots = 300
gamma = 1
kappa = 0.007
c = 700
alpha = 45
health = 60
mutate_prob = 0.1
slope = 4
base_degen = 15
###########

#Auxiliary functions
def rows_to_harvest(rows, health, gamma):
    return max(rows*(1 - gamma*(100-health)/100), 0)

def degeneration(period, slope, base_degen):
    return base_degen + slope*period

def health_regeneration(health_investment, health, kappa):
    return 100*(math.exp(kappa*health_investment)/(math.exp(kappa*health_investment) + (100 - health)/health)) - health

def life_enjoyment(life_investment, health, c, alpha):
    return c*(health/100)*(life_investment/(life_investment + alpha))

def harvesting(num_rows_to_harvest, value_per_dot, black_dots, rows_m):
    
    return value_per_dot*black_dots*num_rows_to_harvest/rows_m

# Create enviroment
def health_experiment(health, periods, kappa, gamma, alpha, c, investment_profile, black_dots):
    '''
    '''
    joy_per_period =[]
    for period in range(periods):
        #Rows to harvest 
        rows = rows_to_harvest(rows_m, health, gamma)
        #harvesting
        income = harvesting(rows, value_per_dot, black_dots, rows_m)
        #degeneration
        health = health - degeneration(period + 1, slope, base_degen)
        # check if person still alive. if health is below zero stop this
        if health <= 0:
            zeros = [0 for i in range(periods - period)] 
            joy_per_period.extend(zeros)
            break
        # health investiment
        health_investment = (1 - investment_profile[period])*income
        health += health_regeneration(health_investment, health, kappa)
        #print("Round " + str(period) + "###\nHealth: " + str(health))

        #round down
        health = int(health)
        #health check
        health = health if health <= 100 else 100
        #joy investment
        life_investment = investment_profile[period]*income
        joy = life_enjoyment(life_investment, health, c, alpha)
        joy_per_period.append(joy)

    total_joy = sum(joy_per_period)
    #print("Joy with this investment profile: " + str(total_joy))
    return total_joy

#Create Population of solutions
population_size = 1000
num_children = 500

def generate_population(population_size, periods):
    investment_profiles = [[random.uniform(0, 1) for i in range(periods)] for _ in range(population_size)] #what percentage to invest on joy
    return investment_profiles

## Mutation
def mutate_solution(solution, prob):
    l1  = [random.uniform(0.85, 1) for _ in range(len(solution))]
    l2  = [random.uniform(1, 1.15) for _ in range(len(solution))]
    for i in range(len(solution)):
       if random.random() < prob:
            if random.random() < 0.1:
                solution[i] = solution[i]*l1[i]   
            else:
                solution[i] =  min(solution[i]*l2[i] , 1)
    return solution

def generate_children(population, num_children, mutate_prob):
  children = []
  for _ in range(num_children//2):
      parents = random.sample(population , 2)
      divider = random.randint(0 , len(population[1])   -1)
                                    
      children.append(mutate_solution(parents[0][:divider] + parents[1][divider:], mutate_prob))  
      children.append(mutate_solution(parents[1][:divider] + parents[0][divider:], mutate_prob))  

  return children

#Survival: Select a couple of solutions
def tournament_survival(new_population, population_size):
    trimmed_population = []
    for i in range(population_size):
        investment_profile_1 = new_population[random.randint(0, len(new_population) - 1)]
        investment_profile_2 = new_population[random.randint(0, len(new_population) - 1)]
        if health_experiment(health, periods, kappa, gamma, alpha, c, investment_profile_1, black_dots) >= health_experiment(health, periods, kappa, gamma, alpha, c, investment_profile_2, black_dots):
            trimmed_population.append(investment_profile_1) 
        else:
            trimmed_population.append(investment_profile_2)
    return trimmed_population


## Everything


def ga_iteration(population, num_children, mutate_prob):
  children = generate_children(population, num_children, mutate_prob)
  return tournament_survival(population + children, len(population))

current_population = generate_population(population_size, periods)

for _ in range(1000):
    current_population = ga_iteration(current_population, num_children, mutate_prob)
        
print(str("Investment profile on joy each period: " + str(current_population[0]) + "\nTotal Joy: " + str(health_experiment(health, periods, kappa, gamma, alpha, c, current_population[0], black_dots))))

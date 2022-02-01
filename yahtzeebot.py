from collections import Counter 
from itertools import product
from multiprocessing import Value
from random import randint
from math import factorial as fact
from typing import *

'============================================================================================'
' UTILITY FUNCTIONS '

def fullrange(start_inclusive, end_inclusive):
    '''returns a range INCUSIVE of the given starting value AND ending value''' 
    # python your default behaviour sucks in this regard 
    return range(start_inclusive, end_inclusive+1) 

def n_take_r(n:int, r:int,ordered:bool=False,with_replacement:bool=False)->int:
    '''count of arrangements that can be formed from r selections, chosen from n items, 
       where order DOES or DOESNT matter, and WITH or WITHOUT replacement, as specified'''
    if (not ordered): # we're counting "combinations" where order doesn't matter, so there are less of these 
        if with_replacement:
            return fact(n+r-1) // ( fact(r)*fact(n-1) )
        else:
            return fact(n) // ( fact(r)*fact(n-r) ) # this matches math.comb()
    else: 
        if with_replacement:
            return n**r 
        else:
            return fact(n)//fact(n-r)

def chance_of_exactly_x_hits(x:int, n:int=5, s:int=6)->float:
    '''chance of rolling EXACTLY x target values using n dice with s sides'''
    p = 1/s
    nCx = n_take_r(n,x) 
    return nCx * p**x * (1-p)**(n-x) # this is the "binomial probability formula"

def chance_of_at_least_x_hits(x:int, n:int=5, s:int=6)->float:
    '''chance of rolling AT LEAST x target values using n dice with s sides'''
    running_sum = 0.0
    for i in fullrange(x,n):
        running_sum += chance_of_exactly_x_hits(i,n,s)
    return running_sum



def die_index_combos()->set[tuple[int,...]]:
    ''' the set of all ways to roll different dice, as represented by a set of indice sets'''
    ''' {(), (0), (1), (2), (3), (4), (0,0), (0,1), (0,2), (0,3), (0,4), (1,1), (1,2) ... etc}'''
    them:set[tuple[int,...]] = set(tuple()) 
    them.add(tuple()) # this first one represents rolling no dice -- an empty tuple containing no indices
    for i in fullrange(0,4):
        them.add(tuple(set([i])))
        for ii in fullrange(0,4):
            them.add(tuple(set(sorted([i,ii])))) # list (sortable) -> set (for unique values) -> tuple (suitable as a dict key later)
            for iii in fullrange(0,4):
                them.add(tuple(set(sorted([i,ii,iii]))))
                for iv in fullrange(0,4):
                    them.add(tuple(set(sorted([i,ii,iii,iv]))))
                    for v in fullrange(0,4):
                        them.add(tuple(set(sorted([i,ii,iii,iv,v])))) 
    return them


die_sides = [1,2,3,4,5,6] # values for all sides of a standard die
side_count = len(die_sides) 
index_combos: set[tuple[int,...]] = die_index_combos() # all options for which of 5 dice to roll
roll_outcomes_for_set_of_size = [list(product(die_sides,repeat=i)) for i in fullrange(0,5)] # all possible roll outcomes for different size die sets 

def ev(dievals: list[int], score_fn: Callable[[list[int]],float] ) -> tuple[float,list[tuple[int,...]]]:
    '''highest expected value for the next roll, with a given scoring function, starting with existing dievals.
       also returns a list of of die indice tuples that can be rolled to acheive this expected value'''

    chances = {}
    for indecis in index_combos: 
        die_count = len(indecis)
        outcomes = roll_outcomes_for_set_of_size[die_count]
        total=0.0
        for outcome in outcomes: # compose and score each roll possibility in turn
            newvals=list(dievals)
            j=0
            for i in indecis: 
                newvals[i]=outcome[j]
                j+=1
            total += score_fn(newvals) 
        outcome_count = side_count**die_count
        chances[indecis] = total/outcome_count

    max_ev = float(max(chances.values()))
    max_combos = [key for (key,value) in chances.items() if value == max_ev]
    return max_ev, max_combos

def score_upperbox(boxnum:int, dievals:list[int])->int:
    total = 0
    for x in dievals:
        if x==boxnum: total+=x
    return total

def score_n_of_a_kind(n:int,dievals:list[int])->int:
    inarow=1; maxinarow=1; lastval=-1; sum=0; 
    for x in sorted(dievals):
        if x==lastval: inarow = inarow + 1
        else: inarow=1 
        maxinarow = max(inarow,maxinarow)
        lastval = x
        sum+=x
    if maxinarow>=n: return sum 
    else: return 0

def straight_len(dievals:list[int])->int:
    inarow=1; maxinarow=1; lastval=-999
    sortedvals=sorted(dievals)
    for x in sortedvals:
        if x==lastval+1: inarow = inarow + 1
        else: inarow=1
        maxinarow = max(inarow,maxinarow)
        lastval = x
    return maxinarow 

def score_chance(dievals:list[int])->int: return sum(dievals) 
def score_aces(dievals:list[int])->int:  return score_upperbox(1,dievals)
def score_twos(dievals:list[int])->int:  return score_upperbox(2,dievals)
def score_threes(dievals:list[int])->int:return score_upperbox(3,dievals)
def score_fours(dievals:list[int])->int: return score_upperbox(4,dievals)
def score_fives(dievals:list[int])->int: return score_upperbox(5,dievals)
def score_sixes(dievals:list[int])->int: return score_upperbox(6,dievals)
def score_3ofakind(dievals:list[int])->int: return score_n_of_a_kind(3,dievals)
def score_4ofakind(dievals:list[int])->int:  return score_n_of_a_kind(4,dievals)
def score_sm_str8(dievals:list[int])->int: return (30 if straight_len(dievals) >= 4 else 0)
def score_lg_str8(dievals:list[int])->int: return (40 if straight_len(dievals) >= 5 else 0)
def score_fullhouse(dievals:list[int])->int: 
    counts = sorted(list(Counter(dievals).values() ))
    if (counts[0]==2 and counts[1]==3) or counts[0]==5: return 25
    else: return 0
def score_yahtzee(dievals:list[int])->int: return (50 if score_n_of_a_kind(5,dievals) > 0 else 0)
def score_bonus(dievals:list[int] )->int: return (100 if score_yahtzee(dievals) > 0 else 0)


# named indexes for the different slot types
CHANCE=0
ACES=1
TWOS=2
THREES=3
FOURS=4
FIVES=5
SIXES=6
THREE_OF_A_KIND=7
FOUR_OF_A_KIND=8
SMALL_STRAIGHT=9
LARGE_STRAIGHT=10
FULL_HOUSE=11
YAHTZEE=12
BONUS1=13
BONUS2=14
BONUS3=15
SLOT_COUNT=16

slot_points = [None]*16
slot_score_fns = [
    score_chance, 
    score_aces, 
    score_twos, 
    score_threes, 
    score_fours, 
    score_fives, 
    score_sixes, 
    score_3ofakind, 
    score_4ofakind, 
    score_sm_str8, 
    score_lg_str8, 
    score_fullhouse, 
    score_yahtzee,
    score_bonus,
    score_bonus,
    score_bonus,
]

class Slot:
    points:int 
    score_fn:Callable[[list[int]],int] 

class StateEV:
    avail_slot_indices:list[int] # 32768 possibilities per sum( [n_take_r(15,r,False,False) for r in fullrange(0,15)])
    rolls_remaining:int # 3 possibilities per len([0,1,2])
    dievals:list[int] # 362 possibilities per sum(n_take_r(6,r,False,True) for r in fullrange(0,5)]) 
    indices_to_roll:tuple[int] # 32 possibilites per sum(n_take_r(5,r,False,False) for r in fullrange(0,5)] 
    upper_bonus_deficit: int #<= 63 possibilities 
    ev:float # 71_741_472_768 possibilities per 32768*3*362*32*63 and 2_241_921_024 worth saving per 32768*3*362*63 


# def choose_dice(slot_options:list[Slot], dievals, rolls_remaining=1) -> tuple(float,tuple[int,...]): 
#     ''' returns indices of which dice to roll given scoring functions of available slots, current dievals, and rolls remaining '''

    # if len(slot_options) == 1:
    #     odds, best_choices= ev(dievals, slot_options[0])
    #     if rolls_remaining == 1:
    #         return best_choices[0] # as there is no more branching, just return the first one 
    #     else 
    #         for choice in best_choices 
    #         odds, die_sets = ev(dievals, slot_options[0])



'============================================================================================'
def main(): 
    #ad hoc testing code here for now

    dice = [randint(1,6) for _ in range(5)]
    print(dice)

    for i in range(0,SLOT_COUNT):
        available = True
        if i > YAHTZEE and slot_points[i-1]==None: available = False #bonus slots not always available
        slot_points[i], _ = ev(dice,slot_score_fns[i]) if available else None
        print( slot_score_fns[i].__name__ + "\t" + str(round(slot_points[i],2)) )


#########################################################
if __name__ == "__main__": main()
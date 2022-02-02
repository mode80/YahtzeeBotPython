from collections import Counter 
from itertools import product
from random import randint
from math import factorial as fact
from typing import *
from functools import * 

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


@cache
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


@cache
def roll_outcomes_for_set_of_size(size:int): 
    die_sides = [1,2,3,4,5,6] # values for all sides of a standard die
    return list(product(die_sides,repeat=size))  # all possible roll outcomes for different size die sets 

@cache
def score_upperbox(boxnum:int, sorted_dievals:tuple[int,...])->int:
    return sum([x for x in sorted_dievals if x==boxnum])

@cache
def score_n_of_a_kind(n:int,sorted_dievals:tuple[int,...])->int:
    inarow=1; maxinarow=1; lastval=-1; sum=0; 
    for x in sorted_dievals:
        if x==lastval: inarow = inarow + 1
        else: inarow=1 
        maxinarow = max(inarow,maxinarow)
        lastval = x
        sum+=x
    if maxinarow>=n: return sum 
    else: return 0

@cache
def straight_len(sorted_dievals:tuple[int,...])->int:
    inarow=1; maxinarow=1; lastval=-999
    for x in sorted_dievals:
        if x==lastval+1: inarow = inarow + 1
        else: inarow=1
        maxinarow = max(inarow,maxinarow)
        lastval = x
    return maxinarow 


'============================================================================================'
# named indexes for the different slot types

UPPER_BONUS=0
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
CHANCE=13
YAHTZEE_BONUS1=14
YAHTZEE_BONUS2=15
YAHTZEE_BONUS3=16

SLOT_COUNT=17
all_slot_indecis = range(SLOT_COUNT) 
independent_slot_indecis = fullrange(ACES,CHANCE) # independent slots don't depend on other slots for their value
IndependentSlotIndex = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]    

def score_aces(sorted_dievals:tuple[int,...])->int:  return score_upperbox(1,sorted_dievals)
def score_twos(sorted_dievals:tuple[int,...])->int:  return score_upperbox(2,sorted_dievals)
def score_threes(sorted_dievals:tuple[int,...])->int:return score_upperbox(3,sorted_dievals)
def score_fours(sorted_dievals:tuple[int,...])->int: return score_upperbox(4,sorted_dievals)
def score_fives(sorted_dievals:tuple[int,...])->int: return score_upperbox(5,sorted_dievals)
def score_sixes(sorted_dievals:tuple[int,...])->int: return score_upperbox(6,sorted_dievals)

def score_3ofakind(sorted_dievals:tuple[int,...])->int: return score_n_of_a_kind(3,sorted_dievals)
def score_4ofakind(sorted_dievals:tuple[int,...])->int:  return score_n_of_a_kind(4,sorted_dievals)
def score_sm_str8(sorted_dievals:tuple[int,...])->int: return (30 if straight_len(sorted_dievals) >= 4 else 0)
def score_lg_str8(sorted_dievals:tuple[int,...])->int: return (40 if straight_len(sorted_dievals) >= 5 else 0)

@cache
def score_fullhouse(sorted_dievals:tuple[int,...])->int: 
    counts = sorted(list(Counter(sorted_dievals).values() ))
    if (counts[0]==2 and counts[1]==3) or counts[0]==5: return 25
    else: return 0

@cache
def score_chance(sorted_dievals:tuple[int,...])->int: return sum(sorted_dievals) 

def score_yahtzee(sorted_dievals:tuple[int,...])->int: return (50 if score_n_of_a_kind(5,sorted_dievals) > 0 else 0)

def score_yahtzee_bonus1(dievals:tuple[int,...],is_available:bool)->int: return (100 if is_available and score_yahtzee(dievals) > 0 else 0)
def score_yahtzee_bonus2(dievals:tuple[int,...],is_available:bool)->int: return (100 if is_available and score_yahtzee(dievals) > 0 else 0)
def score_yahtzee_bonus3(dievals:tuple[int,...],is_available:bool)->int: return (100 if is_available and score_yahtzee(dievals) > 0 else 0)

def score_upper_bonus(dievals:list[int], upper_section_total:int)->int: return 35 if upper_section_total >= 63 else 0 

score_fns = [
    # score_upper_bonus,
    None,
    score_aces, score_twos, score_threes, score_fours, score_fives, score_sixes, 
    score_3ofakind, score_4ofakind, score_sm_str8, score_lg_str8, score_fullhouse, score_yahtzee, score_chance, 
    # score_yahtzee_bonus1, score_yahtzee_bonus2, score_yahtzee_bonus3,
]

def score_slot(slot_index:IndependentSlotIndex, sorted_dievals:tuple[int,...] )->int:
    return score_fns[slot_index](sorted_dievals) #type:ignore

def non_empty_slot_points(slot_points:list[int])->list[int]:
    return filter(bool,slot_points) #type:ignore 

def calc_total_points(slot_points:list[int])->int:
    return sum(filter(bool,non_empty_slot_points(slot_points) )) 

def calc_lower_points(slot_points:list[int])->int:
    return sum(filter(bool, [y for x,y in enumerate(non_empty_slot_points(slot_points)) if ACES <= y <= SIXES] ))

def calc_upper_points(slot_points:list[int])->int:
    return sum(filter(bool, [y for x,y in enumerate(non_empty_slot_points(slot_points)) if y > SIXES] ))

#TODO deprecate in favor of differenet approach
@cache #reminder: not thread safe
def ev_for_slot(slot_index:IndependentSlotIndex, sorted_dievals: tuple[int,...] ) -> tuple[float,list[tuple[int,...]]]:
    '''highest expected value for the next roll, for a given slot, starting with existing dievals.
    also returns a list of die indice tuples that can be rolled to acheive this expected value'''

    chances = {}
    for indecis in die_index_combos(): 
        die_count = len(indecis)
        outcomes = roll_outcomes_for_set_of_size(die_count)
        total=0.0
        for outcome in outcomes: # compose and score each roll possibility in turn
            newvals=list(sorted_dievals)
            for outcome_index, die_index in enumerate(indecis): 
                newvals[die_index]=outcome[outcome_index]
            total += score_slot(slot_index, tuple(sorted(newvals)) )
        outcome_count = SIDES**die_count
        chances[indecis] = total/outcome_count

    max_ev = float(max(chances.values()))
    max_combos = [key for (key,value) in chances.items() if value == max_ev]
    return max_ev, max_combos

'============================================================================================'
    
SIDES = 6
cache = dict() #type:ignore

# def new_ev_for_keystate(sorted_open_slots:tuple[int,...], sorted_dievals:tuple[int,...], upper_bonus_deficit:int, rolls_remaining:int) -> float: 
# ''' returns the additional expected value to come, given relevant game state'''

# if sorted_open_slots==0: return 0 # if there are no more slots open no new value can be added

# if rolls_remaining==0: 
#     for slot_index in sorted_open_slots:
#         ScoreCard.score_slot(slot_index,
#         pass

# pass

class KeyState: # captures relevant state variables for a distinct expected value of unknowns
    avail_slot_indices:list[int] # 32768 possibilities per sum( [n_take_r(15,r,False,False) for r in fullrange(0,15)])
    rolls_remaining:int # 3 possibilities per len([0,1,2])
    dievals:list[int] # 252 possibilities per n_take_r(6,5,False,True) 
    indices_to_roll:tuple[int] # 32 possibilities per sum(n_take_r(5,r,False,False) for r in fullrange(0,5)] 
    upper_bonus_deficit: int #<= 63 possibilities 
    ev_of_unknowns:float # 49_941_577_728 possibilities per 32768*3*362*32*63 and 1_560_674_304 worth saving per 32768*3*252*63 

def generate_odds():

    # start with all completed scorecard states with 0 rolls left
    # work backwards to all the 1 slot 1 roll remaining states
    # then 1 slot 2 roll remaining states
    # then 2 slot 1 roll
    # 2slot 2 roll
    # etc
    pass

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

    dice = tuple(sorted([randint(1,6) for _ in range(5)]))
    print(dice)

    slot_points:list[Optional[int]] = [None]*SLOT_COUNT

    for i in independent_slot_indecis:
        slot_points[i], _ = ev_for_slot(i, dice) 

    # slot_points[UPPER_BONUS] = score_upper_bonus(dice,calc_upper_points(slot_points)) 

    # for i in fullrange(YAHTZEE_BONUS1,YAHTZEE_BONUS3):
    #     slot_points[i], _ = ev_for_slot(i, dice) if slot_points[i-1]!=None else 0 
 
    for i in independent_slot_indecis:
        print( score_fns[i].__name__ + "\t" + str(round(slot_points[i],2)) )


#########################################################
if __name__ == "__main__": main()
from collections import Counter 
from itertools import combinations, permutations, product
from random import randint
from math import factorial as fact
from typing import *
from functools import *

from numpy import roll 

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
def all_outcomes_for_rolling_n_dice(size:int)->list[int]: 
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
    if sorted_dievals[0]==sorted_dievals[4]: return 5 # yahtzee counts as straight per rules 
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
YAHTZEE_BONUSES=14

point_slot_indecis = fullrange(UPPER_BONUS,YAHTZEE_BONUSES) # these correspond to available slots for storing points 
fn_slot_indecis = fullrange(ACES,CHANCE) # corresponds to available slot scoring functions 

def score_aces(sorted_dievals:tuple[int,...])->int:  return score_upperbox(1,sorted_dievals)
def score_twos(sorted_dievals:tuple[int,...])->int:  return score_upperbox(2,sorted_dievals)
def score_threes(sorted_dievals:tuple[int,...])->int:return score_upperbox(3,sorted_dievals)
def score_fours(sorted_dievals:tuple[int,...])->int: return score_upperbox(4,sorted_dievals)
def score_fives(sorted_dievals:tuple[int,...])->int: return score_upperbox(5,sorted_dievals)
def score_sixes(sorted_dievals:tuple[int,...])->int: return score_upperbox(6,sorted_dievals)

def score_3ofakind(sorted_dievals:tuple[int,...])->int: return score_n_of_a_kind(3,sorted_dievals)
def score_4ofakind(sorted_dievals:tuple[int,...])->int:  return score_n_of_a_kind(4,sorted_dievals)
def score_sm_str8(sorted_dievals:tuple[int,...])->int: return 30 if straight_len(sorted_dievals) >= 4 else 0
def score_lg_str8(sorted_dievals:tuple[int,...])->int: return 40 if straight_len(sorted_dievals) >= 5 else 0

@cache
def score_fullhouse(sorted_dievals:tuple[int,...])->int: 
    counts = sorted(list(Counter(sorted_dievals).values() ))
    if (counts[0]==2 and counts[1]==3) or counts[0]==5: return 25
    else: return 0

@cache
def score_chance(sorted_dievals:tuple[int,...])->int: return sum(sorted_dievals) 

def score_yahtzee(sorted_dievals:tuple[int,...])->int: return (50 if len(set(sorted_dievals))==1 else 0)

score_fns = [
    None, # we stub this out so indices align with dievals
    score_aces, score_twos, score_threes, score_fours, score_fives, score_sixes, 
    score_3ofakind, score_4ofakind, score_sm_str8, score_lg_str8, score_fullhouse, score_yahtzee, score_chance, 
]

def score_slot(slot_index:int , sorted_dievals:tuple[int,...] )->int:
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
@cache 
def ev_for_slot(slot_index:int, sorted_dievals: tuple[int,...] ) -> tuple[float,list[tuple[int,...]]]:
    '''highest expected value for the next roll, for a given slot, starting with existing dievals.
    also returns a list of die indice tuples that can be rolled to acheive this expected value'''

    evs = {}
    for indecis in die_index_combos(): 
        die_count = len(indecis)
        outcomes = all_outcomes_for_rolling_n_dice(die_count)
        total=0.0
        for outcome in outcomes: # compose and score each roll possibility in turn
            newvals=list(sorted_dievals)
            for outcome_index, die_index in enumerate(indecis): 
                newvals[die_index]=outcome[outcome_index]
            total += score_slot(slot_index, tuple(sorted(newvals)) )
        outcome_count = SIDES**die_count
        evs[indecis] = total/outcome_count

    max_ev = float(max(evs.values()))
    max_combos = [key for (key,value) in evs.items() if value == max_ev]
    return max_ev, max_combos

'============================================================================================'

def score_slot_with_bonus(slot:int, sorted_dievals:tuple[int,...], upper_bonus_deficit:int, yahtzee_zeroed:bool)->float:
    total = score_slot(slot,sorted_dievals)  # score slot itself 
    if slot <= SIXES and total >= upper_bonus_deficit : total+=35  # add possible upper bonus
    if not yahtzee_zeroed and (sorted_dievals[0]==sorted_dievals[4]) : total+=100 # extra yahtzee bonus  
    return total
 
SIDES = 6
ev_cache = dict() #type:ignore

def best_slot_for_dice(open_slots:tuple[int,...],upper_bonus_deficit:int, yahtzee_zeroed:bool, sorted_dievals:tuple[int,...]) -> tuple[int,float]:
    ''' ev_for_final_roll_among_slot_possibilities '''
    slot_sequence_total=0.0
    slot_sequences = permutations(open_slots, len(open_slots)) 
    slot_sequence_evs = {}
    for slot_sequence in slot_sequences:
        head_slot = slot_sequence[0]
        now_zeroed = yahtzee_zeroed
        now_deficit = upper_bonus_deficit 

        new_ev = new_ev_for_state(head_slot, 0, now_deficit, now_zeroed, sorted_dievals) 
        if not yahtzee_zeroed and (sorted_dievals[0]==sorted_dievals[4]) : new_ev+=100 # extra yahtzee bonus  
        if len(slot_sequence) == 1 and (now_deficit - new_ev)<= 0: new_ev +=35 # check for upper bonus on final slot
        slot_sequence_total += new_ev 

        if len(slot_sequence) > 1 : # proceed to also score remaining slots
            if head_slot==YAHTZEE and new_ev==0: now_zeroed=True
            if head_slot<=SIXES: now_deficit -= new_ev 
            tail_slots = slot_sequence[1:]
            slot_sequence_total += new_ev_for_state(tail_slots, now_deficit, 3, now_zeroed)
        slot_sequence_evs[slot_sequence] = slot_sequence_total 
    best_ev = max(slot_sequence_evs.values()) # this is a choice -- go with max 
    best_slot = [k for k,v in slot_sequence_evs.items() if v==best_ev][0]
    return best_slot, best_ev

def best_die_selection(open_slots:tuple[int,...], rolls_remaining:int, upper_bonus_deficit:int, yahtzee_zeroed:bool, sorted_dievals:tuple[int,...]) -> tuple[tuple[int,...],float]: 

    newvals=list(sorted_dievals) 

    while rolls_remaining >= 1:

        "per die selection possibility" #this is a choice -- go with max
        selection_evs = {}
        for selection in die_index_combos(): 

            "per roll outcome possibility" #this is not a choice -- go with average 
            rolled_outcomes_total = 0.0
            rolled_outcome_possibilities = all_outcomes_for_rolling_n_dice(len(selection))
            for rolled_outcome in rolled_outcome_possibilities: 
                for rolled_index, dieval_index in enumerate(selection): newvals[dieval_index]=rolled_outcome[rolled_index]
                _, best_slot_ev = best_slot_for_dice(open_slots, upper_bonus_deficit, yahtzee_zeroed, sorted(newvals)) 
                rolled_outcomes_total += best_slot_ev

            avg_outcome_ev_for_selection = rolled_outcomes_total/len(rolled_outcome_possibilities)
            selection_evs[selection] = avg_outcome_ev_for_selection
        
        best_ev = max(v for k,v in selection_evs.values()) # final ev will stick on last roll 
        rolls_remaining -= 1

    best_selection = [k for k,v in selection_evs.items() if v==best_ev][0]
    return best_selection, best_ev



def new_ev_for_state(open_slots:tuple[int,...], rolls_remaining:int, upper_bonus_deficit:int, yahtzee_zeroed:bool, sorted_dievals:tuple[int,...]=(0,0,0,0,0,)) -> float: 
    ''' returns the additional expected value to come, given relevant game state.
        (sorted_open_slots can be in the range from 1 to 13; ACES thru CHANCE, excludes bonus slots)''' 
    
    # try for cache hit first
    if (open_slots, rolls_remaining, upper_bonus_deficit, yahtzee_zeroed, sorted_dievals) in ev_cache :      #type:ignore
        return ev_cache[(open_slots, rolls_remaining, sorted_dievals, upper_bonus_deficit, yahtzee_zeroed, sorted_dievals)]  #type:ignore

    if rolls_remaining==0 and len(open_slots)==1: # this is the last move. there's nothing to do but score it 
        slot = open_slots[0]
        ev = score_slot(slot,sorted_dievals)  # score slot itself 
        if not yahtzee_zeroed and (sorted_dievals[0]==sorted_dievals[4]) : ev+=100 # extra yahtzee bonus  
        if slot<=SIXES: upper_bonus_deficit -= ev 
        if upper_bonus_deficit <= 0: ev+=35  # add possible upper bonus

    elif rolls_remaining == 0 :
        _, ev = best_slot_for_dice(open_slots, upper_bonus_deficit, yahtzee_zeroed, sorted_dievals) 

    else: # rolls_remaining >= 1 
        _, ev = best_die_selection(open_slots, upper_bonus_deficit, yahtzee_zeroed, sorted_dievals) 
 
    # cache and return final result
    ev_cache[(open_slots, sorted_dievals, upper_bonus_deficit, rolls_remaining, yahtzee_zeroed)] = ev #type:ignore
    return ev


            


# class KeyState: # captures relevant state variables for a distinct expected value of unknowns
#     avail_slot_indices:list[int] # 32768 possibilities per sum( [n_take_r(15,r,False,False) for r in fullrange(0,15)])
#     rolls_remaining:int # 3 possibilities per len([0,1,2])
#     dievals:list[int] # 252 possibilities per n_take_r(6,5,False,True) 
#     indices_to_roll:tuple[int] # 32 possibilities per sum(n_take_r(5,r,False,False) for r in fullrange(0,5)] 
#     upper_bonus_deficit: int #<= 36 possibilities len(fullrange(0,5))*6 
#     ev_of_unknowns:float # 40,995,127,296 possibilities per 32768*3*362*32*36 and 891,813,888 worth saving per 32768*3*252*36 


'============================================================================================'
def main(): 
    #ad hoc testing code here for now

    dice = tuple(sorted([randint(1,6) for _ in range(5)]))
    print(dice)

    slot_points:list[Optional[int]] = [None]*len(point_slot_indecis)

    for i in fn_slot_indecis:
        slot_points[i], _ = ev_for_slot(i, dice) 

    # slot_points[UPPER_BONUS] = score_upper_bonus(dice,calc_upper_points(slot_points)) 

    # for i in fullrange(YAHTZEE_BONUS1,YAHTZEE_BONUS3):
    #     slot_points[i], _ = ev_for_slot(i, dice) if slot_points[i-1]!=None else 0 
 
    for i in fn_slot_indecis:
        print( score_fns[i].__name__ + "\t" + str(round(slot_points[i],2)) )


#########################################################
if __name__ == "__main__": main()
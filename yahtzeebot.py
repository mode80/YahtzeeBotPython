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
def all_outcomes_for_rolling_n_dice(size:int)->list[tuple[int,...]]: 
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

ALL_DICE = (0,1,2,3,4)
SIDES = 6

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
    None, # stub this out so indices align more intuitively with categories 
    score_aces, score_twos, score_threes, score_fours, score_fives, score_sixes, 
    score_3ofakind, score_4ofakind, score_sm_str8, score_lg_str8, score_fullhouse, score_yahtzee, score_chance, 
]

def score_slot(slot_index:int , sorted_dievals:tuple[int,...] )->int:
    '''reports the score for a set of dice in a given slot w/o regard for exogenous gamestate (bonuses, yahtzee wildcards etc)'''
    return score_fns[slot_index](sorted_dievals) #type:ignore

def non_empty_slot_points(slot_points:list[int])->list[int]:
    return filter(bool,slot_points) #type:ignore 

def calc_total_points(slot_points:list[int])->int:
    return sum(filter(bool,non_empty_slot_points(slot_points) )) 

def calc_lower_points(slot_points:list[int])->int:
    return sum(filter(bool, [y for x,y in enumerate(non_empty_slot_points(slot_points)) if ACES <= y <= SIXES] ))

def calc_upper_points(slot_points:list[int])->int:
    return sum(filter(bool, [y for x,y in enumerate(non_empty_slot_points(slot_points)) if y > SIXES] ))

'============================================================================================'


slot_ev_cache = {} #type:ignore

def best_slot_ev(open_slots:tuple[int,...], sorted_dievals:tuple[int,...], upper_bonus_deficit:int=63, yahtzee_zeroed:bool=True) -> tuple[int,float]:
    ''' returns the best slot and corresponding ev for final dice, given the slot possibilities and other relevant state '''

    if (open_slots,sorted_dievals,upper_bonus_deficit,yahtzee_zeroed) in slot_ev_cache:
        return slot_ev_cache[open_slots,sorted_dievals,upper_bonus_deficit,yahtzee_zeroed]

    slot_sequences = permutations(open_slots, len(open_slots)) 
    evs = {}
    for slot_sequence in slot_sequences:
        total=0.0
        head_slot = slot_sequence[0]
        zeroed_now = yahtzee_zeroed
        upper_deficit_now = upper_bonus_deficit 

        head_ev = score_slot(head_slot,sorted_dievals)  # score slot itself w/o regard to game state adjustments
        yahtzee_rolled = (sorted_dievals[0]==sorted_dievals[4]) # go on to adjust the raw ev for exogenous game state factors
        if yahtzee_rolled and not yahtzee_zeroed : 
            head_ev+=100 # extra yahtzee bonus per rules
            if head_slot==SMALL_STRAIGHT: head_ev=30 # extra yahtzees are valid straights per wildcard rules
            if head_slot==LARGE_STRAIGHT: head_ev=40 
        if head_slot <=SIXES and head_ev>0 : upper_deficit_now = max(upper_deficit_now - head_ev, 0) 
        if len(slot_sequence) == 1 and upper_deficit_now == 0: head_ev +=35 # check for upper bonus on final slot
        total+=head_ev

        if len(slot_sequence) > 1 : # proceed to also score remaining slots
            if head_slot==YAHTZEE and head_ev==0: zeroed_now=True
            tail_slots = slot_sequence[1:]
            _, tail_ev = best_dice_ev(tail_slots, 3, upper_deficit_now, zeroed_now) # <---------
            total += tail_ev
        evs[total] = slot_sequence #we're clobbering any previous tie values here, but this is ok

    best_ev = max(evs.keys()) # slot is a choice -- use max ev
    best_sequence = evs[best_ev]
    best_slot = best_sequence[0]

    slot_ev_cache[open_slots,sorted_dievals,upper_bonus_deficit,yahtzee_zeroed] = (best_slot, best_ev)
    return best_slot, best_ev


selection_ev_cache = {} #type:ignore

def best_dice_ev(open_slots:tuple[int,...], rolls_remaining:int=3, upper_bonus_deficit:int=63, yahtzee_zeroed:bool=True, sorted_dievals:tuple[int,...]=(0,0,0,0,0) ) -> tuple[tuple[int,...],float]: 
    ''' returns the best selection of dice and corresponding ev, given slot possibilities and any existing dice and other relevant state '''

    if (open_slots, rolls_remaining, upper_bonus_deficit, yahtzee_zeroed, sorted_dievals) in selection_ev_cache: # try for cache hit first
        return selection_ev_cache[open_slots, rolls_remaining, upper_bonus_deficit, yahtzee_zeroed, sorted_dievals]

    if rolls_remaining==0: # if no rolls, then the "best" possible selection is empty set and ev is that of the best slot

        best_selection = set() 
        _, best_ev = best_slot_ev(open_slots, sorted_dievals, upper_bonus_deficit, yahtzee_zeroed) # <---------------

    else:

        "per die selection possibility" #selection is a choice -- track max ev
        selection_evs = {}
        if rolls_remaining==3: die_combos = {ALL_DICE} # we must select all dice on the first roll
        else: die_combos= die_index_combos() # otherwise try them all
        for selection in die_combos: 

            "per roll outcome possibility" #outcomes are not a choice -- track average ev
            total = 0.0
            outcomes = all_outcomes_for_rolling_n_dice(len(selection))
            for outcome in outcomes: 
                newvals=list(sorted_dievals) 
                for i, j in enumerate(selection): newvals[j]=outcome[i]
                sorted_newvals = tuple(sorted(newvals))
                _, ev = best_dice_ev(open_slots, rolls_remaining-1, upper_bonus_deficit, yahtzee_zeroed, sorted_newvals)
                total += ev

            avg_ev = total/len(outcomes)
            selection_evs[avg_ev] = selection 
        
        best_ev = max(selection_evs.keys()) 
        best_selection = selection_evs[best_ev] 

    selection_ev_cache[open_slots, rolls_remaining, upper_bonus_deficit, yahtzee_zeroed, sorted_dievals] = (best_selection, best_ev) #cache it
    return best_selection, best_ev


def ev_for_state(open_slots:tuple[int,...], upper_bonus_deficit:int=63, yahtzee_zeroed:bool=True, rolls_remaining:int = 3, sorted_dievals:tuple[int,...]=(0,0,0,0,0,)) -> float: 
    ''' returns the additional expected value to come, given relevant game state.
        (sorted_open_slots can be in the range from 1 to 13; ACES thru CHANCE, excludes bonus slots)''' 
    
    if rolls_remaining == 0 :
        _, ev = best_slot_ev(open_slots, sorted_dievals, upper_bonus_deficit, yahtzee_zeroed) 
    else: 
        _, ev = best_dice_ev(open_slots, rolls_remaining, upper_bonus_deficit, yahtzee_zeroed, sorted_dievals) 
            


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

    avail_slots = (CHANCE,)
    dice = (4,4,4,4,3)
    #result = best_slot_ev(avail_slots, dice)
    print ()
    print (avail_slots)
    print (dice)
    # result = best_dice_ev(avail_slots, rolls_remaining=1, sorted_dievals=dice)
    result = best_slot_ev(avail_slots, sorted_dievals=dice)
    print (result)



#########################################################
if __name__ == "__main__": main()
#########################################################

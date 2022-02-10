from collections import Counter 
from itertools import combinations, permutations, product
from random import randint
from math import factorial as fact
from typing import *
from functools import *
from timeit import timeit
from tqdm import tqdm

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
SM_STRAIGHT=9
LG_STRAIGHT=10
FULL_HOUSE=11
YAHTZEE=12
CHANCE=13
YAHTZEE_BONUSES=14

ALL_DICE = (0,1,2,3,4)
UNROLLED_DIEVALS = (0,0,0,0,0)
SIDES = 6

# point_slot_indecis = fullrange(UPPER_BONUS,YAHTZEE_BONUSES) # these correspond to available slots for storing points 
# fn_slot_indecis = fullrange(ACES,CHANCE) # corresponds to available slot scoring functions 

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


def best_slot_ev(open_slots:tuple[int,...], sorted_dievals:tuple[int,...], upper_bonus_deficit:int=63, yahtzee_zeroed:bool=True) -> tuple[int,float]:
    ''' returns the best slot and corresponding ev for final dice, given the slot possibilities and other relevant state '''

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
            if head_slot==SM_STRAIGHT: head_ev=30 # extra yahtzees are valid straights per wildcard rules
            if head_slot==LG_STRAIGHT: head_ev=40 
        if head_slot <=SIXES and head_ev>0 : upper_deficit_now = max(upper_deficit_now - head_ev, 0) 
        if len(slot_sequence) == 1 and upper_deficit_now == 0: head_ev +=35 # check for upper bonus on final slot
        total+=head_ev

        if len(slot_sequence) > 1 : # proceed to also score remaining slots
            if head_slot==YAHTZEE and head_ev==0: zeroed_now=True
            tail_slots = slot_sequence[1:]
            tail_ev = ev_for_state(tail_slots, None, 3, upper_deficit_now, zeroed_now) # <---------
            total += tail_ev
        evs[total] = slot_sequence #we're clobbering any previous tie values here, but this is ok

    best_ev = max(evs.keys()) # slot is a choice -- use max ev
    best_sequence = evs[best_ev]
    best_slot = best_sequence[0]

    return best_slot, best_ev


def best_dice_ev(open_slots:tuple[int,...], sorted_dievals:tuple[int,...]=None, rolls_remaining:int=3, upper_bonus_deficit:int=63, yahtzee_zeroed:bool=True) -> tuple[tuple[int,...],float]: 
    ''' returns the best selection of dice and corresponding ev, given slot possibilities and any existing dice and other relevant state '''

    selection_evs = {}
    if sorted_dievals==None: # we must select all dice on the first roll
        sorted_dievals = UNROLLED_DIEVALS
        die_combos = {ALL_DICE} 
    else: die_combos= die_index_combos() # otherwise we must try all possible combos

    for selection in die_combos: 
        total = 0.0
        outcomes = all_outcomes_for_rolling_n_dice(len(selection))
        for outcome in outcomes: 
            newvals=list(sorted_dievals) 
            for i, j in enumerate(selection): newvals[j]=outcome[i]
            sorted_newvals = tuple(sorted(newvals))
            ev = ev_for_state(open_slots, sorted_newvals, rolls_remaining-1, upper_bonus_deficit, yahtzee_zeroed)
            total += ev
        avg_ev = total/len(outcomes) #outcomes are not a choice -- track average ev
        selection_evs[avg_ev] = selection 
    
    best_ev = max(selection_evs.keys()) #selection is a choice -- track max ev
    best_selection = selection_evs[best_ev] 
    return best_selection, best_ev

# Counts of cachable states 
    # 252 dieval combo possibilities 
    #     n_take_r(6,5,False,True) 
    # 8191 sorted empty slot scenarios 
    #    sum([n_take_r(13,r,ordered=False,with_replacement=False) for r in fullrange(1,13)] )
    # 36 upper_bonus_deficit possibilities 
    #     len(fullrange(0,5))*6 
    # 2 yahtzee_zeroed possiblities 
    # 4 rolls_remaining possibilities
    #     len([0,1,2,3])
    # 252*8191*36*2*4==594_470_016  


progress_bar=None #tqdm(total=594_470_016) # we'll increment each time we calculate the best ev without a cache hit
ev_cache={}

def ev_for_state(sorted_open_slots:tuple[int,...], sorted_dievals:tuple[int,...]=None, rolls_remaining:int=3, upper_bonus_deficit:int=63, yahtzee_zeroed:bool=False) -> float: 
    ''' returns the additional expected value to come, given relevant game state.'''

    if (sorted_open_slots, sorted_dievals, rolls_remaining, upper_bonus_deficit, yahtzee_zeroed) in ev_cache: # try for cache hit first
        return ev_cache[sorted_open_slots, sorted_dievals, rolls_remaining, upper_bonus_deficit, yahtzee_zeroed]

    global progress_bar
    if progress_bar is None: 
        lenslots=len(sorted_open_slots)
        iterations = 252 * 36 * 2 * 4 * sum([n_take_r(lenslots,r,False,False) for r in fullrange(1,lenslots)] )
        progress_bar = tqdm(total=iterations) 
    
    if rolls_remaining == 0 :
        _, ev = best_slot_ev(sorted_open_slots, sorted_dievals, upper_bonus_deficit, yahtzee_zeroed) 
    else: 
        _, ev = best_dice_ev(sorted_open_slots, sorted_dievals, rolls_remaining, upper_bonus_deficit, yahtzee_zeroed) 
            
    ev_cache[sorted_open_slots, sorted_dievals, rolls_remaining, upper_bonus_deficit, yahtzee_zeroed] = ev

    progress_bar.update(1) 

    return ev    


# Final scorecard configurations: (mostly irrelevant)
#   . 6 ways to score Aces. Ditto for other upper slots. So 6**6 ways to score top = 46_656
#     (some will have a bonus, others not, but this doesn't add to the total configurations)
#   . 4ofakind has 6 types of matching dice, each with a spare die of 6 different possibilities = 36 configurations here
#   . 3ofakind is 6 trips plus 11 possible totals for remaining 2 dice = 66     len(Counter(list(x+y for x,y in product([1,2,3,4,5,6],repeat=2))))==11
#   . full house is 2 possibilities  -- either 25 or 0  -- even though full house is 6 pairs * 6 trips = 36
#   . lgstraight 2 possibilities, 0 or 40       even though 12345 and 23456
#   . smstraight 2 possibilities, 0 or 30       even though 1234 and 2345 and 3456, each with 6 possible spares = 3*6=18
#   . yahtzee 2 possilities                     even though 6 different matching dice
#   . chance is only 26 totals per Counter(list(a+b+c+d+e for a,b,c,d,e in product([1,2,3,4,5,6],repeat=5))) even though n_take_r(6,5,ordered=False,with_replacement=True) possibilities = 252
#   6*6*6*6*6*6 * 36 * 66 * 2 * 2 * 2 * 2 * 26 = 461_155_368_964
#   . a yahtzee bonus scenario is yet another way to score 12 of the above slots with +100 points, so x12 above == ... 
#   ===============
#   553_386_442_752
#   ===============

# Things to calculate and cache
#  with 0-rolls left, final slot 
#   . score every possible final slot against every dievals combo scenario 
#       there are 3348 of these to calc/cache
#       dieval combos: 252=n_take_r(6,5,ordered=False,with_replacement=True) 
#       for the 6 yahtzee dieval scenarios there's an additional way to score 12 of the (non-yahtzee) slots
#           6*12=72 
#       13 * (252) + 72 = 3348
#       (ignore for now the upper_bonus_deficits: 36 possibilities len(fullrange(0,5))*6)
#  with 1-rolls left, final slot 
#   . for each of 13 possible final slots, we're looking at one of 252 dieval combos and 32 possible die selections, so 104_832 scenarios 
#       104_832 = 13*252*32
#       32 = sum( [n_take_r(5,r,ordered=False,with_replacement=False) for r in fullrange(0,5)])
#   . for each scenario, calc/cache an average of its possible outcome scores (we're averaging between 1 & 252 scores per scenario)  
#       that's 104_832 EVs to calc/cache (purgable)
#   . this cache lets us lookup the EV for any dievals/oneslot/selection scenario, even the bad options
#   . as we go, we calc/cache the max EV among selections for each oneslot/dievals combo
#       13 * 252 = 3276 
#   . 104_832 of those were intermediary calcuations and can (should?) be excluded from the cache, leaving 6624 things 
#   . those 6624 things lets us lookup the 1-roll-left EV for any dievals, final-slot scenario
#  with 2 rolls left, final slot
#   . for each of 13 possible final slots... 
#   . and for each of the 252 dieval combos you might be going into the 2nd roll with...
#   . and for all 32 possible die selections...  
#   . lookup the 1-roll EVs for all the possible selection outcomes (1 to 252 of them)  and calc/cache the average 
#   . this is 13*252*32=104_832 new EVs to calc/cache (purgable)
#   . as we go, we calc/cache store the max (best) EV among each of the 32 selections 
#       104832/32 = 3276 of them 
#  with 3 rolls left, final slot
#   . ditto above, but looking up the 2-roll EVs
#   . as we go, we calc/cache store the max (best) EV among each of the 32 selections 
#       104832/32 = 3276 of them 
#  altogether we've now calced 3348 + 3*(104_832 + 3276) = 327,672 things . but we only need to cache 13,176 of them 
##
#  with 2 final slots   
#   with 0-rolls left, n-final-slots
#   . for each of 156 possible final slots sequences... 
#       156=n_take_r(13,2,ordered=True,with_replacement=False) 
#   . lookup the score for the current dievals against the first in the sequence then...
#   . lookup the 3-roll-remaining EV for the remainder of the sequence (not each remaining slot in turn)
#   . keep track of these slot sequence results and calc/cache the max
#   . for two final slots we're calc/caching 156 things
#   . we can't compose our result from cached 1-final-slot scenarios because optimal play can involve targeting multiple slots 
#       (e.g. going for either a small or a large straight is very different than rolling for a straight or yahtzee) 
#  
#  with 13 final slots  
#   . for the case of 13 final slots remaining (empty scorecard) there are 
#   . ikes fucking 6_227_020_800 sequence possibilities
#       6_227_020_800=n_take_r(13,13,ordered=True,with_replacement=False) 
#   . the calcs for each of these amount to taking a max of several (1 to 252) lookups
#   . we need these for each of 252 dieval combos 
#   . and we separately need all that for every 12-slot sequence, 11-slot sequence, etc...
#   . so we're looking at 16_926_797_486 * 252 = 4_265_552_966_472 calcs
#      16_926_797_486 = sum([n_take_r(13,r,ordered=True,with_replacement=False) for r in fullrange(0,13)] )
#      252=n_take_r(6,5,ordered=False,with_replacement=True) 
#   . if each billion calcs takes a minute that's ~3 days on a single core processor
#   . we only need to cache the EV for the -best- sequence per dieval combo, which should only be 8191 * 252 = 2,064,132
#     8191=sum([n_take_r(13,r,ordered=False,with_replacement=False) for r in fullrange(1,13)] )
   

'============================================================================================'
def main(): 
    #ad hoc testing code here for now

    avail_slots = tuple((ACES,CHANCE)) 
    result = ev_for_state(avail_slots)
    print(ev_cache)


#########################################################
if __name__ == "__main__": main()
#########################################################

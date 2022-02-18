from collections import Counter 
from itertools import chain, permutations, product
from random import randint
from math import factorial as fact
from typing import *
from functools import *
from timeit import timeit
from tqdm import tqdm
from datetime import datetime
import pickle 

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

'============================================================================================'

@lru_cache(maxsize=None)
def die_index_combos()->set:
    ''' the set of all ways to roll different dice, as represented by a set of indice sets'''
    ''' {(), (0), (1), (2), (3), (4), (0,0), (0,1), (0,2), (0,3), (0,4), (1,1), (1,2) ... etc}'''
    them:set = set(tuple()) 
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


@lru_cache(maxsize=None)
def all_outcomes_for_rolling_n_dice(size:int)->list: 
    die_sides = [1,2,3,4,5,6] # values for all sides of a standard die
    return list(product(die_sides,repeat=size))  # all possible roll outcomes for different size die sets 

@lru_cache(maxsize=None)
def score_upperbox(boxnum:int, sorted_dievals:tuple)->int:
    return sum([x for x in sorted_dievals if x==boxnum])

@lru_cache(maxsize=None)
def score_n_of_a_kind(n:int,sorted_dievals:tuple)->int:
    inarow=1; maxinarow=1; lastval=-1; sum=0; 
    for x in sorted_dievals:
        if x==lastval: inarow = inarow + 1
        else: inarow=1 
        maxinarow = max(inarow,maxinarow)
        lastval = x
        sum+=x
    if maxinarow>=n: return sum 
    else: return 0

@lru_cache(maxsize=None)
def straight_len(sorted_dievals:tuple)->int:
    inarow=1; maxinarow=1; lastval=-999
    for x in sorted_dievals:
        if x==lastval+1: inarow = inarow + 1
        else: inarow=1
        maxinarow = max(inarow,maxinarow)
        lastval = x
    return maxinarow 


# named indexes for the different slot types
ACES=1; TWOS=2; THREES=3; FOURS=4; FIVES=5; SIXES=6
THREE_OF_A_KIND=7; FOUR_OF_A_KIND=8; 
SM_STRAIGHT=9; LG_STRAIGHT=10; FULL_HOUSE=11; YAHTZEE=12; CHANCE=13

ALL_DICE = (0,1,2,3,4)
UNROLLED_DIEVALS = (0,0,0,0,0)
SIDES = 6

# point_slot_indecis = fullrange(UPPER_BONUS,YAHTZEE_BONUSES) # these correspond to available slots for storing points 
# fn_slot_indecis = fullrange(ACES,CHANCE) # corresponds to available slot scoring functions 

def score_aces(sorted_dievals:tuple)->int:  return score_upperbox(1,sorted_dievals)
def score_twos(sorted_dievals:tuple)->int:  return score_upperbox(2,sorted_dievals)
def score_threes(sorted_dievals:tuple)->int:return score_upperbox(3,sorted_dievals)
def score_fours(sorted_dievals:tuple)->int: return score_upperbox(4,sorted_dievals)
def score_fives(sorted_dievals:tuple)->int: return score_upperbox(5,sorted_dievals)
def score_sixes(sorted_dievals:tuple)->int: return score_upperbox(6,sorted_dievals)

def score_3ofakind(sorted_dievals:tuple)->int: return score_n_of_a_kind(3,sorted_dievals)
def score_4ofakind(sorted_dievals:tuple)->int:  return score_n_of_a_kind(4,sorted_dievals)
def score_sm_str8(sorted_dievals:tuple)->int: return 30 if straight_len(sorted_dievals) >= 4 else 0
def score_lg_str8(sorted_dievals:tuple)->int: return 40 if straight_len(sorted_dievals) >= 5 else 0

@lru_cache(maxsize=None)
def score_fullhouse(sorted_dievals:tuple)->int: 
    # The official rule is that a Full House is "three of one number and two of another"
    counts = sorted(list(Counter(sorted_dievals).values() ))
    if len(counts)==2 and (counts[0]==2 and counts[1]==3) : return 25
    else: return 0

@lru_cache(maxsize=None)
def score_chance(sorted_dievals:tuple)->int: return sum(sorted_dievals) 

def score_yahtzee(sorted_dievals:tuple)->int: return (50 if len(set(sorted_dievals))==1 else 0)

score_fns = [
    None, # stub this out so indices align more intuitively with categories 
    score_aces, score_twos, score_threes, score_fours, score_fives, score_sixes, 
    score_3ofakind, score_4ofakind, score_sm_str8, score_lg_str8, score_fullhouse, score_yahtzee, score_chance, 
]

def score_slot(slot_index:int , sorted_dievals:tuple )->int:
    '''reports the score for a set of dice in a given slot w/o regard for exogenous gamestate (bonuses, yahtzee wildcards etc)'''
    return score_fns[slot_index](sorted_dievals) #type:ignore

'============================================================================================'


def best_slot_ev(sorted_open_slots:tuple, sorted_dievals:tuple, upper_bonus_deficit:int=63, yahtzee_is_wild:bool=False) -> tuple:
    ''' returns the best slot and corresponding ev for final dice, given the slot possibilities and other relevant state '''

    slot_sequences = permutations(sorted_open_slots, len(sorted_open_slots)) 
    evs = {}
    for slot_sequence in slot_sequences:
        total=0.0
        head_slot = slot_sequence[0]
        upper_deficit_now = upper_bonus_deficit 

        head_ev = score_slot(head_slot,sorted_dievals)  # score slot itself w/o regard to game state adjustments
        yahtzee_rolled = (sorted_dievals[0]==sorted_dievals[4]) # go on to adjust the raw ev for exogenous game state factors
        if yahtzee_rolled and yahtzee_is_wild : 
            head_ev+=100 # extra yahtzee bonus per rules
            if head_slot==SM_STRAIGHT: head_ev=30 # extra yahtzees are valid in any lower slot per wildcard rules
            if head_slot==LG_STRAIGHT: head_ev=40 
            if head_slot==FULL_HOUSE: head_ev=25 
        if head_slot <=SIXES and upper_deficit_now>0 and head_ev>0 : 
            if head_ev >= upper_deficit_now: head_ev+=35 # add upper bonus when needed total is reached
            upper_deficit_now = max(upper_deficit_now - head_ev, 0) 
        total+=head_ev

        if len(slot_sequence) > 1 : # proceed to also score remaining slots
            wild_now=True if head_slot==YAHTZEE and yahtzee_rolled else yahtzee_is_wild
            tail_slots = tuple(sorted(slot_sequence[1:]))
            tail_ev = ev_for_state(tail_slots, None, 3, upper_deficit_now, wild_now) # <---------
            total += tail_ev
        evs[total] = slot_sequence #we're clobbering any previous tie values here, but this is ok

    best_ev = max(evs.keys()) # slot is a choice -- use max ev
    best_sequence = evs[best_ev]
    best_slot = best_sequence[0]

    return best_slot, best_ev


def best_dice_ev(sorted_open_slots:tuple, sorted_dievals:tuple=None, rolls_remaining:int=3, upper_bonus_deficit:int=63, yahtzee_is_wild:bool=True) -> tuple: 
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
            ###### HOT CODE PATH #######
            newvals=list(sorted_dievals) 
            for i, j in enumerate(selection): 
                newvals[j]=outcome[i]
            sorted_newvals = tuple(sorted(newvals))
            ev = ev_for_state(sorted_open_slots, sorted_newvals, rolls_remaining-1, upper_bonus_deficit, yahtzee_is_wild)
            total += ev
            ############################
        avg_ev = total/len(outcomes) #outcomes are not a choice -- track average ev
        selection_evs[avg_ev] = selection 
    
    best_ev = max(selection_evs.keys()) #selection is a choice -- track max ev
    best_selection = selection_evs[best_ev] 
    return best_selection, best_ev


progress_bar=None#tqdm(total=594_470_016) # we'll increment each time we calculate the best ev without a cache hit
ev_cache=dict()
done = set()

def ev_for_state(sorted_open_slots:tuple, sorted_dievals:tuple=None, rolls_remaining:int=3, upper_bonus_deficit:int=63, yahtzee_is_wild:bool=False) -> float: 
    ''' returns the additional expected value to come, given relevant game state.'''

    global progress_bar, log, done, ev_cache

    if progress_bar is None: 
        lenslots=len(sorted_open_slots)
        open_slot_combos = sum(n_take_r(lenslots,r,False,False) for r in fullrange(1,lenslots)) 
        done = set(s for s,_,r,_,_ in ev_cache.keys() if r==3)
        iterations=open_slot_combos-len(done)
        progress_bar = tqdm(total=iterations) 

    if upper_bonus_deficit > 0 and sorted_open_slots[0]>SIXES: # trim the statespace by ignoring upper total variations when no more upper slots are left
        upper_bonus_deficit=63

    if (sorted_open_slots, sorted_dievals, rolls_remaining, upper_bonus_deficit, yahtzee_is_wild) in ev_cache: # try for cache hit first
        return ev_cache[sorted_open_slots, sorted_dievals, rolls_remaining, upper_bonus_deficit, yahtzee_is_wild]

    if rolls_remaining == 0 :
        _, ev = best_slot_ev(sorted_open_slots, sorted_dievals, upper_bonus_deficit, yahtzee_is_wild)                   # <-----------------
    else: 
        _, ev = best_dice_ev(sorted_open_slots, sorted_dievals, rolls_remaining, upper_bonus_deficit, yahtzee_is_wild)  # <-----------------
            
    log_line = f'{rolls_remaining:<2}\t{str(_):<15}\t{ev:6.2f}\t{str(sorted_dievals):<15}\t{upper_bonus_deficit:<2}\t{yahtzee_is_wild}\t{str(sorted_open_slots)}' 
    progress_bar.write(log_line)
    print(log_line,file=log)

    ev_cache[sorted_open_slots, sorted_dievals, rolls_remaining, upper_bonus_deficit, yahtzee_is_wild] = ev

    if rolls_remaining==3: # periodically update progress and save
        if sorted_open_slots not in done:
            done.add(sorted_open_slots)
            progress_bar.update(1) 
            if len(done) % 80 == 0 :
                with open('ev_cache.pkl','wb') as f: pickle.dump(ev_cache,f)
 
    return ev    


'============================================================================================'
def main(): 
    #ad hoc testing code here for now

    # avail_slots = tuple(sorted(fullrange(YAHTZEE,CHANCE)))
    avail_slots = tuple(sorted(fullrange(ACES,CHANCE)))

    global log
    log = open('yahtzeebot.log','a') #open(f'{datetime.now():%Y-%m-%d-%H-%M}.log','w')
    print(f'rolls_remaining\tresult\tev\tsorted_dievals\tupper_bonus_deficit\tyahtzee_is_wild\tsorted_open_slots)' , file=log)

    # try to load cache from disk
    global ev_cache
    
    try:
        with open('ev_cache.pkl','rb') as f: ev_cache = pickle.load(f)
    except:
        pass

    result = ev_for_state(avail_slots)

    # with open('ev_cache.pkl','wb') as f: pickle.dump(ev_cache,f)

    log.close


#########################################################
if __name__ == "__main__": main()
#########################################################

# Counts of cachable states 
    # 252 dieval combo possibilities 
    #     n_take_r(6,5,False,True) 
    # 8191 sorted empty slot scenarios 
    #    sum([n_take_r(13,r,ordered=False,with_replacement=False) for r in fullrange(1,13)] )
    # 64 upper_bonus_deficit possibilities 
    #     len([x for x in possible_top_scores() if x <=63])
    # 2 yahtzee_is_wild possiblities 
    # 2 rolls_remaining possibilities with die selection choices
    #     len([1,2])



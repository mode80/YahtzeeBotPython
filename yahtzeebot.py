from collections import *
from itertools import permutations
import math
from random import randint
from math import factorial as fact

''' EV FINDER FUNCTIONS '''

EV_FOR_DIE_NOT = { 1: 4, 2: 3.8, 3: 3.6, 4: 3.4, 5: 3.2, 6: 3 } 
'''expected value for one roll of a die where we know it did not come up as _keyval_'''

def count_of_n_choose_x_combos(n:int, x:int):
    '''number of "n choose x" combinations (where order doesnt matter)'''
    return math.comb(n,x) # fact(n) / ( fact(x)*fact(n-x) )

def chance_of_exactly_x_hits(x:int, n:int=5, s:int=6)->float:
    '''chance of rolling EXACTLY x target values using n dice with s sides'''
    p = 1/s
    nCx = count_of_n_choose_x_combos(n,x) 
    return nCx * p**x * (1-p)**(n-x) # this is the "binomial probability formula"

def chance_of_at_least_x_hits(x:int, n:int=5, s:int=6)->float:
    '''chance of rolling AT LEAST x target values using n dice with s sides'''
    running_sum = 0
    for i in range(x,n+1):
        running_sum += chance_of_exactly_x_hits(i,n,s)
    return running_sum

def sim_ev_upperbox1_3rolls(trials:int=100000) -> float:
    '''simulated expected value for an upperbox n with 3 rolls remaining'''
    sum = 0
    for trial in range(trials):
        dice_to_roll_next = 5
        for roll in range(3):
            hits_this_roll = 0
            for die in range(dice_to_roll_next):
                if randint(1,6) == 1: hits_this_roll+=1
            sum += hits_this_roll
            dice_to_roll_next -= hits_this_roll
    return sum/trials

def ev_upperbox_3rolls(box_n:int) -> float:
    '''expected value for an upperbox n with 3 rolls remaining'''
    ev_upperbox1 = 2.1064814814814823 # 5*1/6 + (5-5/6)*1/6 + ( 5 - 5/6 - (5-5/6)*1/6 )*1/6
    return ev_upperbox1 * box_n

def sim_ev_upperbox(n:int, dicevals:list[int],rolls:int=1,trials:int=100000): 
    '''simulated expected value for an upperbox n with existing dicevals and rolls remaining'''
    starting_hits = Counter(dicevals)[n]
    dice_count = 5-starting_hits
    hits=0
    for trial in range(trials):
        dice_remaining = dice_count
        for roll in range(rolls,0,-1):
            for dienum in range(1,dice_remaining+1):
                if randint(1,6)==1:
                    hits +=1
                    dice_remaining += -1
    return n * (starting_hits + hits/trials)

def ev_upperbox(n:int, dicevals:list[int],rolls:int=1): 
    '''expected value for an upperbox n with existing dicevals and rolls remaining'''
    starting_hits = Counter(dicevals)[n]
    dice_count = 5-starting_hits
    hits=0.0
    for roll in range(rolls,0,-1):
        hits += dice_count*( (1/6) * (5/6)**(rolls-roll) )
    return n * (starting_hits + hits)

def sim_ev_n_of_a_kind(n:int, dicevals:list[int], target_val:int=-1, trials:int=1_000_000 ) -> float:
    '''simulated expected value for an n-of-a-kind with existing dicevals and 1 roll remaining'''

    # supply smart target_val if not given one 
    # TODO this isn't always smartest! It's sometime better to shoot for 6s over taking more 1s
    counts = Counter(dicevals)
    if target_val == -1: target_val = max(counts, key=counts.get() )
    if not (1 <= target_val <= 6): raise Exception()
    starting_hits = counts[target_val]
    starting_pips = starting_hits * target_val

    hits_needed = max(0, n - starting_hits)
    to_roll_count = 5-starting_hits
    running_sum=0
    target_acheived=0
    rolled=list(range(to_roll_count)) #prep list of correct size

    for trial in range(trials):
        hits=0
        for die_index in range(to_roll_count):
            rolled_val = randint(1,6)
            rolled[die_index]=rolled_val
            if rolled_val==target_val: hits +=1
        if hits >= hits_needed: 
            target_acheived+=1
            running_sum += starting_pips + sum(rolled) 
    return running_sum/trials

def ev_n_of_a_kind(n:int, dicevals:list[int], target_val:int=-1 ) -> float:
    '''expected value for an n-of-a-kind with existing dicevals and 1 roll remaining'''
    starting_hits = Counter(dicevals)[target_val]
     # supply smart target_val if not given one 
    # TODO this isn't always smartest! It's sometime better to shoot for 6s over taking more 1s
    counts = Counter(dicevals)
    if target_val == -1: target_val = max(counts, key=counts.get )
    if not (1 <= target_val <= 6): raise Exception()
    starting_hits = counts[target_val]

    to_roll_count = 5-starting_hits
    ev =0 
    for i in range(0,to_roll_count+1):
        p = chance_of_exactly_x_hits(i, to_roll_count) 
        hit_count = starting_hits+i
        value_when_acheived = hit_count*target_val + (5-hit_count)*EV_FOR_DIE_NOT[target_val]
        ev += p * value_when_acheived * (hit_count>=n)
    return ev 

def sim_ev_fullhouse(dicevals:list[int],trials:int=-1) -> float:
    '''simulated expected value for a full house given existing dicevals and 1 roll remaining'''

    sortedvals=sorted(dicevals)
    newvals=[0,0,0,0,0]
    hits = 0
    uniques = len(set(dicevals))
    if trials==-1: trials = 1 + 1_000_000 * (uniques-1) # more unique values require more trials

    for t in range(trials): 
        vals=sortedvals
        for i in range(len(vals)):
            should_roll = False
            if i==0: #first
                if vals[i] != vals[i+1]: should_roll = True
            elif i==4: #last
                if vals[i] != vals[i-1]: should_roll = True
            else: #middle
                if vals[i] != vals[i-1] and vals[i]!=vals[i+1]: should_roll = True
            if should_roll: newvals[i] = randint(1,6)
            else: newvals[i] = vals[i]
        if score_fullhouse(newvals) > 0: hits +=1

    return hits/trials * 25


def ev_fullhouse(dicevals:list[int]) -> float:
    '''expected value for a full house given existing dicevals and 1 roll remaining'''
    counts = sorted( list( Counter(dicevals).values() ), reverse=True)
    most = counts[0]
    second_most = counts[1] if len(counts)>1 else 0
    p = 0.0 # p is for probability 
    if most==5:             # e.g.[1,1,1,1,1]
        p=1                 # yahtzees count as a full house 
    elif most==4:           # e.g.[1,1,1,1,2]
        p=1/6               # best chance at full house is to roll the single oddball die
    elif most==3:   
       if second_most==2:   # e.g.[1,1,1,2,2]
           p = 1            # trips and a pair means we have a full house already 
       elif second_most==1: # e.g.[1,1,1,2,3]
           p = 1/6          # it's a 1 in 6 chance that rolling one oddball die will match the other 
    elif most==2:
        if second_most==2:  # e.g.[1,1,2,2,3]
            p = 2/6         # there are 2 out of 6 target values for the single oddball die to match the others
        if second_most==1:  # e.g.[1,1,2,3,4]
            # per Excel table, there are 216 permutations of the last 3 dice, 
            # and 21 of those will combine with the pair for a full house 
            p = 0.09722222222222222 # 21/216
    elif most==1:
        # per count_full_houses.py there are 306 ways out of 7776 to roll a full house on one try
        p = 0.039351851851851858 # 306/7776
    return p * 25

def sim_ev_straight(dicevals:list[int],length:int=5):
    '''simulated expected value for a straight of given length using existing dicevals and 1 roll remaining'''

    sortedvals=sorted(dicevals)
    newvals=[0,0,0,0,0]
    total = 0

    if length==5 :
        score_straight = score_lg_straight 
    elif length==4: 
        score_straight = score_sm_straight
    else:
        raise Exception("length must be 4 or 5")

    longest_run_idx = 0
    longest_run_len = 0
    in_a_row=1
    for i in range(1,len(sortedvals)):
        if sortedvals[i]-1 == sortedvals[i-1]: 
            in_a_row+=1
            if in_a_row > longest_run_len:
                longest_run_len = in_a_row 
                longest_run_idx = i-(in_a_row-1)
        else:
            in_a_row=1
    trials = 1 + 1_000_000 * (5-longest_run_len) # too many?

    for t in range(trials): 
        for i in range(0,len(sortedvals)):
            if longest_run_idx <= i <= (longest_run_idx+longest_run_len-1): #keep the values in the longest run 
                newvals[i] = sortedvals[i]
            else:
                newvals[i] = randint(1,6)

        total += score_straight(newvals) 

    return total/trials 

def dice_to_roll_for_str8(dicevals:list[int], str8len:int=5):
    '''returns a tuple containing a string representation of dice to roll, and a float of the probability. 
       e.g. ("010100", 0.1) to roll 2nd and 4th die with 10% chance of a straight'''

    newvals = list(dicevals)
    i=ii=iii=iv=v=0
    roll_mask_hits= {}
    roll_mask_attempts= {}
    roll_mask_chances= {}
    for i in [0,1,2,3,4,5,6]:
        newvals[0]=i if i>0 else dicevals[0]
        if i>0: newvals[0]=i
        for ii in [0,1,2,3,4,5,6]:
            newvals[1]=ii if ii>0 else dicevals[1]
            for iii in [0,1,2,3,4,5,6]:
                newvals[2]=iii if iii>0 else dicevals[2]
                for iv in [0,1,2,3,4,5,6]:
                    newvals[3]=iv if iv>0 else dicevals[3]
                    for v in [0,1,2,3,4,5,6]:
                        newvals[4]=v if v>0 else dicevals[4]
                        indices=[i,ii,iii,iv,v]
                        roll_mask = \
                            ("1" if i!=0 else "0") + \
                            ("1" if ii!=0 else "0") + \
                            ("1" if iii!=0 else "0") + \
                            ("1" if iv!=0 else "0") + \
                            ("1" if v!=0 else "0") 
                        if not roll_mask in roll_mask_attempts: roll_mask_attempts[roll_mask]=0
                        roll_mask_attempts[roll_mask] += 1 
                        if straight_len(newvals) >= str8len: 
                            if not roll_mask in roll_mask_hits: roll_mask_hits[roll_mask]=0
                            roll_mask_hits[roll_mask] += 1 
                        if roll_mask in roll_mask_hits: 
                            roll_mask_chances[roll_mask] = roll_mask_hits[roll_mask]/roll_mask_attempts[roll_mask] 
    best_chance=0
    best_roll_mask=""
    for roll_mask, chance in roll_mask_chances.items():
        if chance > best_chance: 
            best_roll_mask = roll_mask
            best_chance = chance 

    return best_roll_mask, best_chance

 
def ev_straight(dicevals:list[int],str8len:int=5):
    '''expected value for a straight of given length using existing dicevals and 1 roll remaining'''

    if not (4 <= str8len <=5): raise Exception()
    points = 40 if str8len == 5 else 30 
    die_mask, chance = dice_to_roll_for_str8(dicevals,str8len)
    return chance * points 


' SCORING FUNCTIONS '

def score_upperbox(boxnum, dicevals):
    total = 0
    for x in dicevals:
        if x==boxnum: total+=x
    return total

def score_n_of_a_kind(n,dicevals):
    inarow=1; maxinarow=1; lastval=-1; sum=0; 
    for x in sorted(dicevals):
        if x==lastval: inarow = inarow + 1
        else: inarow=1 
        maxinarow = max(inarow,maxinarow)
        lastval = x
        sum+=x
    if maxinarow>=n: 
        return sum 
    else: 
        return 0

def straight_len(dicevals):
    inarow=1; maxinarow=1; lastval=-999
    sortedvals=sorted(dicevals)
    for x in sortedvals:
        if x==lastval+1: inarow = inarow + 1
        else: inarow=1
        maxinarow = max(inarow,maxinarow)
        lastval = x
    return maxinarow 

def score_aces(dicevals):  return score_upperbox(1,dicevals)
def score_twos(dicevals):  return score_upperbox(2,dicevals)
def score_threes(dicevals):return score_upperbox(3,dicevals)
def score_fours(dicevals): return score_upperbox(4,dicevals)
def score_fives(dicevals): return score_upperbox(5,dicevals)
def score_sixes(dicevals): return score_upperbox(6,dicevals)
def score_three_of_a_kind(dicevals): return score_n_of_a_kind(3,dicevals)
def score_four_of_a_kind(dicevals):  return score_n_of_a_kind(4,dicevals)
def score_sm_straight(dicevals): return (30 if straight_len(dicevals) >= 4 else 0)
def score_lg_straight(dicevals): return (40 if straight_len(dicevals) >= 5 else 0)
def score_yahtzee(dicevals): return (50 if score_n_of_a_kind(5,dicevals) > 0 else 0)
def score_fullhouse(dicevals): 
    counts = sorted(list(Counter(dicevals).values() ))
    if (counts[0]==2 and counts[1]==3) or counts[0]==5: return 25
    else: return 0

'============================================================================================'
def main():
    dicevals = [ randint(1,6), randint(1,6), randint(1,6), randint(1,6), randint(1,6) ]
    sameparems=(4,1,[1,1,1,3,4])
    round( sim_ev_n_of_a_kind(*sameparems)  ,1)   
 


#########################################################
if __name__ == "__main__": main()

from dataclasses import dataclass
from collections import Counter
from distutils.command.build import build
# from copyreg import pickle 
from itertools import permutations, product, combinations, combinations_with_replacement, groupby
from more_itertools import powerset, unique_justseen
from functools import cache 
from tqdm import tqdm
from typing import Any
import math #; import xxhash; from pickle import dumps
# import numpy as np

DieVals = tuple[int,int,int,int,int]
Slots = tuple[int,...]

'============================================================================================'
' UTILITY FUNCTIONS '
'============================================================================================'

def fullrange(start_inclusive:int, end_inclusive:int)->range:
    '''returns a range INCUSIVE of the given starting value AND ending value''' 
    return range(start_inclusive, end_inclusive+1) 

# # https://stackoverflow.com/a/48234170/ @Divakar
# def onecold(a):
#     n = len(a)
#     s = a.strides[0]
#     strided = np.lib.stride_tricks.as_strided
#     b = np.concatenate((a,a[:-1]))
#     return strided(b[1:], shape=(n-1,n), strides=(s,s))

# # https://stackoverflow.com/a/48234170/ @Divakar
# def combinations_without_repeat(a):
#     n = len(a)
#     out = np.empty((n,n-1,2),dtype=a.dtype)
#     out[:,:,0] = np.broadcast_to(a[:,None], (n, n-1))
#     out.shape = (n-1,n,2)
#     out[:,:,1] = onecold(a)
#     out.shape = (-1,2)
#     return out


'============================================================================================'
' SCORING FUNCTIONS '
'============================================================================================'

def score_upperbox(boxnum:int, sorted_dievals:DieVals)->int:
    return sum([x for x in sorted_dievals if x==boxnum])

def score_n_of_a_kind(n:int,sorted_dievals:DieVals)->int:
    inarow=1; maxinarow=1; lastval=-1; sum=0; 
    for x in sorted_dievals:
        if x==lastval: inarow = inarow + 1
        else: inarow=1 
        maxinarow = max(inarow,maxinarow)
        lastval = x
        sum+=x
    if maxinarow>=n: return sum 
    else: return 0

# def straight_len(sorted_dievals:DieVals)->int:
#     inarow=1; maxinarow=1; lastval=-999
#     for x in sorted_dievals:
#         if x==lastval+1: inarow = inarow + 1
#         elif x!=lastval: inarow=1
#         maxinarow = max(inarow,maxinarow)
#         lastval = x
#     return maxinarow 

def straight_len(sorted_dievals:DieVals)->int :
    inarow=1; 
    maxinarow=1; 
    lastval=-999; #// stub
    for x in sorted_dievals :
        if x==lastval+1 and x!=0: inarow+=1
        elif x!=lastval: inarow=1
        maxinarow = max(inarow,maxinarow)
        lastval = x
    return maxinarow 
 
# named indexes for the different slot types
ACES=1; TWOS=2; THREES=3; FOURS=4; FIVES=5; SIXES=6
THREE_OF_A_KIND=7; FOUR_OF_A_KIND=8; 
FULL_HOUSE=9; SM_STRAIGHT=10; LG_STRAIGHT=11; YAHTZEE=12; CHANCE=13

def score_aces      (sorted_dievals:DieVals)->int:  return score_upperbox(1,sorted_dievals)
def score_twos      (sorted_dievals:DieVals)->int:  return score_upperbox(2,sorted_dievals)
def score_threes    (sorted_dievals:DieVals)->int:  return score_upperbox(3,sorted_dievals)
def score_fours     (sorted_dievals:DieVals)->int:  return score_upperbox(4,sorted_dievals)
def score_fives     (sorted_dievals:DieVals)->int:  return score_upperbox(5,sorted_dievals)
def score_sixes     (sorted_dievals:DieVals)->int:  return score_upperbox(6,sorted_dievals)

def score_3ofakind  (sorted_dievals:DieVals)->int: return score_n_of_a_kind(3,sorted_dievals)
def score_4ofakind  (sorted_dievals:DieVals)->int: return score_n_of_a_kind(4,sorted_dievals)
def score_sm_str8   (sorted_dievals:DieVals)->int: return 30 if straight_len(sorted_dievals) >= 4 else 0
def score_lg_str8   (sorted_dievals:DieVals)->int: return 40 if straight_len(sorted_dievals) >= 5 else 0

def score_fullhouse(sorted_dievals:DieVals)->int: 
    # The official rule is that a Full House is "three of one number and two of another"
    counts = sorted(list(Counter(sorted_dievals).values() ))
    if len(counts)==2 and (counts[0]==2 and counts[1]==3) : return 25
    else: return 0

def score_chance(sorted_dievals:DieVals)->int: return sum(sorted_dievals) 

@cache
def score_yahtzee(sorted_dievals:DieVals)->int:  
    return 50 if sorted_dievals[0] == sorted_dievals[4] and sorted_dievals[0] != 0 else 0
 
def stub_score(x:DieVals)->int: return 0 

score_fns = [
    stub_score, # stub this out so indices align more intuitively with categories 
    score_aces, score_twos, score_threes, score_fours, score_fives, score_sixes, 
    score_3ofakind, score_4ofakind, score_fullhouse, score_sm_str8, score_lg_str8, score_yahtzee, score_chance, 
]

@cache
def score_slot(slot_index:int , sorted_dievals:DieVals)->int:
    '''reports the score for a set of dice in a given slot w/o regard for exogenous gamestate (bonuses, yahtzee wildcards etc)'''
    return score_fns[slot_index](sorted_dievals)

'============================================================================================'
' TRANSLATED FROM RUST '
'============================================================================================'
@dataclass
class Outcome: 
    __slots__ = ['dievals','mask','arrangements']
    dievals :DieVals 
    mask :DieVals # stores a pre-made mask for blitting this outcome onto a GameState.DieVals.data u16 later
    arrangements :int # how many indistinguisable ways can these dievals be arranged (ie swapping identical dievals)

# INITIALIZERS

FACT = [math.factorial(i) for i in fullrange(0,20)] # cached factorials

''' count of arrangements that can be formed from r selections, chosen from n items, 
    where order DOES or DOESNT matter, and WITH or WITHOUT replacement, as specified'''
def n_take_r(n:int, r:int, order_matters:bool=False, with_replacement:bool=False) -> int:
    if order_matters : # order matters; we're counting "permutations" 
        if with_replacement :
            return n ** r 
        else: # no replacement
            return FACT[n] // FACT[n-r]  # this = FACT[n] when r=n
    else: # we're counting "combinations" where order doesn't matter; there are less of these 
        if with_replacement :
            return FACT[n+r-1] // (FACT[r]*FACT[n-1])
        else: # no replacement
            return FACT[n] // (FACT[r]*FACT[n-r]) 

def sorted_dievals_for_unsorted() -> dict[DieVals, DieVals]:
    out:dict[DieVals,DieVals]={}
    out[(0,0,0,0,0,)] = (0,0,0,0,0,) #first one is the special wildcard 
    for combo in combinations_with_replacement(fullrange(1,6),5) :
        for perm in set(permutations(combo,5)):
            sorted = list(perm)
            sorted.sort()
            out[perm]= tuple(sorted) 
    return out

SORTED_DIEVALS_FOR_UNSORTED=sorted_dievals_for_unsorted() #the sorted version for every 5-dieval-permutation-with-repetition

def indexed_dievals_sorted() -> list[DieVals]: #-> [DieVals; 253] {
    out:list[DieVals]=[] #[DieVals::default(); 253];
    out.append((0,0,0,0,0)) #// first one is the special wildcard 
    for combo in combinations_with_replacement(fullrange(1,6),5) :
        out.append(combo)
    return out

''' the set of all ways to roll different dice, as represented by a collection of index arrays'''
def die_index_combos() -> list[DieVals]: #->[Vec<u8>;32]  { 
    return list(powerset(fullrange(0,4)))

''' this generates the ranges that correspond to the outcomes, within the set of all outcomes, indexed by a given selection '''
def selection_ranges() -> list[slice]: #->[Range<usize>;32]  { 
    sel_ranges:list[slice] = []
    s = 0
    for combo in die_index_combos():
        count = n_take_r(6, len(combo), order_matters=False, with_replacement=True) 
        sel_ranges.append( slice(s,(s+count)) )
        s += count 
    return sel_ranges

SELECTION_RANGES = selection_ranges() 

def distinct_arrangements_for(dievals: DieVals ) -> int:
    key_count = [(key,len(list(group))) for key,group in groupby(dievals)]
    divisor=1
    non_zero_dievals=0
    for key, count in key_count : 
        if key != 0 : 
            divisor *= FACT[count] 
            non_zero_dievals += count
    return FACT[non_zero_dievals ] // divisor 


'''the set of roll outcomes for every possible 5-die selection, where '0' represents an unselected die'''
def all_selection_outcomes() -> list[Outcome]: #->[Outcome;1683]  { 
    out:list[Outcome] = [] #:[Outcome;1683] = [default();1683];
    for combo in die_index_combos():
        for dievals in combinations_with_replacement([1,2,3,4,5,6],len(combo)): 
            mask_list = [0b111,0b111,0b111,0b111,0b111]
            dievals_list = [0] * 5 
            for (j, val ) in enumerate(dievals) : 
                idx = combo[j]  
                dievals_list[idx] = val  
                mask_list[idx] = 0
            outcome = Outcome(
                dievals=tuple(dievals_list),
                mask=tuple(mask_list),
                arrangements=distinct_arrangements_for(dievals),
            )
            out.append(outcome)
    return out

OUTCOMES = all_selection_outcomes() 

''' returns a slice from the precomputed dice roll outcomes that corresponds to the given selection bitfield '''
def outcomes_for_selection(selection:int) ->list[Outcome]: 
    IDX_FOR_SELECTION = [0,1,2,3,4,7,6,16,8,9,10,17,11,13,19,26,5,12,18,20,14,21,22,23,15,25,24,27,28,29,30,31]
    idx = IDX_FOR_SELECTION[selection]
    range = SELECTION_RANGES[idx]
    return OUTCOMES[range]

INDEXED_DIEVALS_SORTED=indexed_dievals_sorted() #//all possible sorted combos of 5 dievals (252 of them)


@dataclass
class GameState:
    __slots__ = ['sorted_dievals','sorted_open_slots','upper_total','rolls_remaining','yahtzee_bonus_avail']
    sorted_dievals:DieVals #=(0,0,0,0,0)# (was) 3bits per die unsorted =15 bits minimally ... 8bits if combo is stored sorted (252 possibilities)
    sorted_open_slots:Slots #=() # " 4 bits for a single slot 
    upper_total:int #=0 # (was) 6 bits " 
    rolls_remaining:int #=0  # (was) 3 bits "
    yahtzee_bonus_avail:bool #= False# (was) 1 bit "

    def __init__(self,sorted_dievals:DieVals=(0,0,0,0,0), sorted_open_slots:Slots=(), upper_total:int=0, rolls_remaining:int=0, yahtzee_bonus_avail:bool=False):
        self.sorted_dievals = sorted_dievals # (was) 3bits per die unsorted =15 bits minimally ... 8bits if combo is stored sorted (252 possibilities)
        self.sorted_open_slots = sorted_open_slots # " 4 bits for a single slot 
        self.upper_total = upper_total # (was) 6 bits " 
        self.rolls_remaining = rolls_remaining  # (was) 3 bits "
        self.yahtzee_bonus_avail = yahtzee_bonus_avail #= False# (was) 1 bit "

    def counts(self) :
        lookups=0; saves=0
        for subset_len in fullrange(1,len(self.sorted_open_slots)): 
            for slots in combinations(self.sorted_open_slots, subset_len):
                joker_rules = YAHTZEE not in slots # yahtzees are wild whenever the yahtzee slot is not open anymore 
                for _upper_bonus_deficit in relevant_upper_totals(slots) :
                    for _yahtzee_bonus_avail in {False,joker_rules}:
                        slot_lookups = subset_len if subset_len==1 else subset_len * 2 * 252 
                        dice_lookups = 848484 # // previoiusly verified by counting up by 1s in the actual loop. however chunking forward is faster 
                        lookups += dice_lookups + slot_lookups
                        saves+=1
        
        return (lookups, saves) 

    def __hash__(self):
        return hash((self.sorted_dievals, self.sorted_open_slots,self.upper_total, self.rolls_remaining, self.yahtzee_bonus_avail,))#return xxhash.xxh3_128_intdigest(dumps((self.sorted_dievals, self.sorted_open_slots,self.upper_total, self.rolls_remaining, self.yahtzee_bonus_avail,))) 

    def __eq__(self, other:Any):
        return (self.sorted_dievals, self.sorted_open_slots,self.upper_total, self.rolls_remaining, self.yahtzee_bonus_avail)  ==  (other.sorted_dievals, other.sorted_open_slots,other.upper_total, other.rolls_remaining, other.yahtzee_bonus_avail)  

    def __ne__(self, other:Any):
        return not(self == other)


    def score_first_slot_in_context(self) :
    
        # /* score slot itself w/o regard to game state */
        slot = self.sorted_open_slots[0]
        assert(slot!=None)
        score = score_slot(slot, self.sorted_dievals)
    
        # /* add upper bonus when needed total is reached */
        if slot<=SIXES and self.upper_total<63 : 
            new_total = min(self.upper_total + score , 63)
            if new_total==63: score += 35 
    
        # /* special handling of "joker rules" */
        just_rolled_yahtzee = score_yahtzee(self.sorted_dievals)==50
        joker_rules_in_play = slot!=YAHTZEE # joker rules in effect when the yahtzee slot is not open 
        if just_rolled_yahtzee and joker_rules_in_play: # standard scoring applies against the yahtzee dice except ... 
            if slot==FULL_HOUSE  : score=25 
            if slot==SM_STRAIGHT : score=30 
            if slot==LG_STRAIGHT : score=40 
    
        # /* special handling of "extra yahtzee" bonus per rules*/
        if just_rolled_yahtzee and self.yahtzee_bonus_avail : 
            score+=100 # extra yahtzee bonus per rules
    
        return score

@dataclass
class ChoiceEV:
    __slots__ = ['choice','ev']
    choice :int 
    ev :float 

    def __init__(self,choice:int = 0 , ev:float = 0.0):
        self.choice = choice
        self.ev= ev 

def previously_used_upper_slots(slots:Slots) : 
    return [x for x in fullrange(1,6) if not x in slots] 

def best_upper_total (slots:Slots) :
    sum=0
    for x in slots : 
        if x>6: break 
        else: sum+=x
    return sum*5


# these are all the possible score entries for each upper slot
UPPER_SCORES = [ 
    [0,0,0,0,0,0],      # STUB
    [0,1,2,3,4,5],      # ACES
    [0,2,4,6,8,10],     # TWOS
    [0,3,6,9,12,15],    # THREES 
    [0,4,8,12,16,20],   # FOURS
    [0,5,10,15,20,25],  # FIVES
    [0,6,12,18,24,30],  # SIXES
]

def relevant_upper_totals(slots:Slots)->list[int]:
    totals:set[int] = set()
    # only upper slots could have contributed to the upper total 
    used_slot_idxs = previously_used_upper_slots(slots)
    used_score_idx_perms = product(fullrange(0,5), repeat=len(used_slot_idxs))
    # for every permutation of entry indexes
    for used_score_idxs in used_score_idx_perms :
        # covert the list of entry indecis to a list of entry -scores-, then total them
        zipped = zip(used_slot_idxs, used_score_idxs)
        tot = sum( map( lambda t: UPPER_SCORES[t[0]][t[1]], zipped ) )
        # add the total to the set of unique totals 
        totals.add(min(tot,63))

    totals.add(0) # 0 is always relevant and must be added here explicitly when there are no used upper slots 

    # filter out the totals that aren't relevant because they can't be reached by the upper slots remaining 
    # this filters out a lot of unneeded state space but means the lookup function must map extraneous deficits to a default 
    best_current_slot_total = best_upper_total(slots)
    return [x for x in totals if x==0 or x + best_current_slot_total >=63]


@dataclass
class App:
    __slots__ = ['bar','ev_cache','game']
    bar:Any
    ev_cache:dict[GameState,ChoiceEV] 
    game:GameState

    ''' return a newly initialized app'''
    def __init__(self, game:GameState) :
        lookups, _saves =  game.counts()
        self.bar:Any = tqdm(total=lookups)
        self.ev_cache:dict[GameState,ChoiceEV] = dict()
        self.game=game 


    ''' rust implementation ported to vanilla single-threaded python for speed comparison'''
    def build_cache(self) :

        all_die_combos = outcomes_for_selection(0b11111)
        placeholder_outcome:Outcome = Outcome((0,0,0,0,0),(0b111,0b111,0b111,0b111,0b111),0)
        # leaf_cache = {}

        # first handle special case of the most leafy leaf calcs -- where there's one slot left and no rolls remaining
        for single_slot in self.game.sorted_open_slots:   
            first_slot = (single_slot,) # set of a single slot 
            joker_rules_in_play = single_slot!=YAHTZEE # joker rules in effect when the yahtzee slot is not open 
            for yahtzee_bonus_available in {False, joker_rules_in_play}: # yahtzee bonus -might- be available when joker rules are in play 
                for upper_total in relevant_upper_totals(first_slot):
                    for outcome in all_die_combos:
                        state = GameState(
                            rolls_remaining = 0,
                            sorted_dievals = outcome.dievals,
                            sorted_open_slots = first_slot,
                            upper_total = upper_total,
                            yahtzee_bonus_avail= yahtzee_bonus_available
                        )
                        score = state.score_first_slot_in_context()
                        choice_ev = ChoiceEV( choice= single_slot, ev= score)
                        self.ev_cache[state] = choice_ev
        
        # for each length 
        for slots_len in fullrange(1, len(self.game.sorted_open_slots)) : 

            # for each slotset (of above length)
            for slots in list(combinations(self.game.sorted_open_slots, slots_len)):

                joker_rules_in_play = YAHTZEE not in slots # joker rules are in effect whenever the yahtzee slot is already filled 

                # for each upper total 
                for upper_total in relevant_upper_totals(slots) :

                    # for each yathzee bonu possibility 
                    for yahtzee_bonus_available in {False,joker_rules_in_play} : #bonus always unavailable unless yahtzees are wild first

                        self.bar.update(848484) #// advance the progress bar by the number of cache reads coming up for dice selection 
                        self.bar.update(252 * slots_len * 1 if slots_len==1 else 2); # advance for slot selection cache reads

                        # for each rolls remaining
                        for rolls_remaining in fullrange(0,3) : 

                            die_combos = [placeholder_outcome] if rolls_remaining==3 else all_die_combos 
                            
                            for die_combo in die_combos: #let built_from_threads = die_combos.into_par_iter().fold(YahtCache::default, |mut built_this_thread, die_combo|{  

                                if rolls_remaining==0 : 

                                    #HANDLE SLOT SELECTION

                                    slot_choice_ev = ChoiceEV(0,0.0)

                                    for first_slot in slots :

                                        # joker rules say extra yahtzees must be played in their matching upper slot if it's available
                                        first_dieval = die_combo.dievals[0]
                                        joker_rules_matter = joker_rules_in_play and score_yahtzee(die_combo.dievals)>0 and first_dieval in slots
                                        head_slot = first_dieval if joker_rules_matter else first_slot 
                                        head = (head_slot,)

                                        yahtzee_bonus_avail_now = yahtzee_bonus_available
                                        upper_total_now:int = upper_total
                                        dievals_or_wildcard:DieVals = die_combo.dievals 
                                        tail = tuple([x for x in slots if x!=head_slot]) if slots_len > 1 else head  
                                        head_plus_tail_ev = 0.0
        
                                        # find the collective ev for the all the slots with this iteration's slot being first 
                                        # do this by summing the ev for the first (head) slot with the ev value that we look up for the remaining (tail) slots
                                        rolls_remaining_now:int = 0
                                        for slots_piece in unique_justseen([head,tail]): #tricky: loops only once when tail==head per condition above. (converting to a set to get uniqe values isn't suitable because order is important and sets are unordered)
                                            state = GameState(
                                                rolls_remaining=rolls_remaining_now, 
                                                sorted_dievals=dievals_or_wildcard,
                                                sorted_open_slots= slots_piece, 
                                                upper_total= upper_total_now if upper_total_now+best_upper_total(slots_piece)>=63 else 0, #only relevant totals are cached 
                                                yahtzee_bonus_avail= yahtzee_bonus_avail_now
                                            )
                                            # cache = leaf_cache if slots_piece==head else self.ev_cache
                                            choice_ev = self.ev_cache[state]
                                            if slots_piece==head : # on the first pass only.. 
                                                #going into tail slots next, we may need to adjust the state based on the head choice
                                                if choice_ev.choice <=SIXES : #adjust upper total for the next pass 
                                                    added = int(choice_ev.ev % 100) # the modulo 100 here removes any yathzee bonus from ev since that doesnt' count toward upper bonus total
                                                    upper_total_now = min(63, upper_total_now + added)
                                                elif choice_ev.choice==YAHTZEE and choice_ev.ev>0.0: #scored _something_ other than 0 in yahtzee
                                                    yahtzee_bonus_avail_now=True # adjust yahtzee related state for the next pass
                                                rolls_remaining_now=3 #for upcoming tail lookup, we always want the ev for 3 rolls remaining
                                                dievals_or_wildcard = placeholder_outcome.dievals # for the 3 rolls remaining, use "wildcard" representative dievals since dice don't matter when rolling all of them
                                            head_plus_tail_ev += choice_ev.ev

                                        if head_plus_tail_ev >= slot_choice_ev.ev: 
                                            slot_choice_ev = ChoiceEV(choice=first_slot, ev=head_plus_tail_ev)
                                        
                                        if joker_rules_matter: break # if joker-rules-matter we were forced to choose one slot, so we can skip trying the rest  
                                    
                                    state = GameState (
                                        sorted_dievals= die_combo.dievals, 
                                        sorted_open_slots= slots,
                                        rolls_remaining= 0, 
                                        upper_total=upper_total, 
                                        yahtzee_bonus_avail= yahtzee_bonus_available 
                                    )
                                    self.ev_cache[state] = slot_choice_ev

                                else: #(if rolls_remaining > 0)  

                                    # HANDLE DICE SELECTION 

                                    next_roll = rolls_remaining-1 
                                    best_dice_choice_ev = ChoiceEV(0,0.0)
                                    # selections are bitfields where '1' means roll and '0' means don't roll # always select all dice on the initial roll, otherwise try all selections 
                                    selections = fullrange(0b11111,0b11111) if rolls_remaining ==3 else fullrange(0b00000,0b11111) 

                                    for selection in selections : # we'll try each selection against this starting dice combo  
                                        total_ev_for_selection = 0.0 
                                        outcomes_count = 0 
                                        for roll_outcome in outcomes_for_selection(selection) :
                                            newvals:DieVals = (
                                                (die_combo.dievals[0] & roll_outcome.mask[0]) | roll_outcome.dievals[0], 
                                                (die_combo.dievals[1] & roll_outcome.mask[1]) | roll_outcome.dievals[1], 
                                                (die_combo.dievals[2] & roll_outcome.mask[2]) | roll_outcome.dievals[2], 
                                                (die_combo.dievals[3] & roll_outcome.mask[3]) | roll_outcome.dievals[3], 
                                                (die_combo.dievals[4] & roll_outcome.mask[4]) | roll_outcome.dievals[4], 
                                            )
                                            newvals = SORTED_DIEVALS_FOR_UNSORTED[newvals]
                                            state = GameState(
                                                sorted_dievals= newvals,
                                                sorted_open_slots= slots, 
                                                upper_total= upper_total, 
                                                yahtzee_bonus_avail= yahtzee_bonus_available, 
                                                rolls_remaining= next_roll, # we'll average all the 'next roll' possibilities (which we'd calclated last) to get ev for 'this roll' 
                                            )
                                            choice_ev = self.ev_cache[state] 
                                            ev_for_this_selection_outcome = choice_ev.ev
                                            total_ev_for_selection += ev_for_this_selection_outcome * roll_outcome.arrangements # bake into upcoming average
                                            outcomes_count += roll_outcome.arrangements # we loop through die "combos" but we'll average all "perumtations"

                                        avg_ev_for_selection = total_ev_for_selection / outcomes_count
                                        if avg_ev_for_selection > best_dice_choice_ev.ev:
                                            best_dice_choice_ev = ChoiceEV(choice=selection, ev=avg_ev_for_selection)

                                    state = GameState(
                                        sorted_dievals= die_combo.dievals,  
                                        sorted_open_slots= slots, 
                                        upper_total=upper_total, 
                                        yahtzee_bonus_avail= yahtzee_bonus_available, 
                                        rolls_remaining=rolls_remaining, 
                                    ) 
                                    self.ev_cache[state] = best_dice_choice_ev
    
    #                             built_this_thread

    #                         }).reduce(YahtCache::default, |mut a,built_from_thread|{
    #                             a.extend(&built_from_thread); a 
    #                         }); // end die_combos.par_into_iter() 

    #                         self.ev_cache.extend(&built_from_threads);

    #                     } // end for each rolls_remaining
    #                 } //end for each yahtzee_is_wild
    #             } //end for each upper total 
    #         } // end for each slot_set 
    #     } // end for each length
    # } // end fn build_cache


'============================================================================================'
def main(): 
    #ad hoc testing code here for now

    game = GameState(   
        sorted_dievals= (0,0,0,0,0) ,
        rolls_remaining= 3, 
        sorted_open_slots= (1,2,3,4,5,6,7,8,9,10,11,12,13),
        upper_total= 0, 
        yahtzee_bonus_avail= False, 
    )
    app = App(game)
    app.build_cache()
    result = app.ev_cache[game]
    print(result)


#########################################################
if __name__ == "__main__": main()
#########################################################


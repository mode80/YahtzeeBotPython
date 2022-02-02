from yahtzeebot import *
import math

card = ScoreCard()

def test_count_of_n_choose_x_items():
    assert n_take_r(6,3,ordered=True,with_replacement=True)== 216 
    assert n_take_r(6,3,ordered=True,with_replacement=False)==120
    assert n_take_r(6,3,ordered=False,with_replacement=True)==56
    assert n_take_r(6,3,ordered=False,with_replacement=False)== 20
    assert n_take_r(15,6) == math.comb(15,6) 

def test_score_aces():  
    assert card.score_aces((2,1,2,1,5,)) == 2
    assert card.score_aces((2,3,2,6,5,)) == 0 

def test_score_upper_box():
    assert score_upperbox(4,(1,2,3,4,5,)) == 4
    assert score_upperbox(4,(4,4,4,4,4,)) == 20
    assert score_upperbox(4,(1,2,3,6,5,)) == 0 

def test_score_three_of_a_kind():
    assert card.score_3ofakind(tuple(sorted([5,1,2,5,5])))==18
    assert card.score_3ofakind(tuple(sorted([3,2,2,3,1])))==0
    assert card.score_3ofakind(tuple(sorted([6,6,1,6,6])))==25

def test_score_four_of_a_kind():
    assert card.score_4ofakind(tuple(sorted([3,2,3,3,3])))==14
    assert card.score_4ofakind(tuple(sorted([3,2,2,3,3])))==0
    assert card.score_4ofakind(tuple(sorted([3,3,3,3,3])))==15

def test_score_fullhouse():
    assert card.score_fullhouse((2,2,3,3,3,)) == 25
    assert card.score_fullhouse((2,2,3,3,2,)) == 25
    assert card.score_fullhouse((2,2,1,3,3,)) == 0 
    assert card.score_fullhouse((2,3,3,3,3,)) == 0 
    assert card.score_fullhouse((1,2,3,4,5,)) == 0 
    assert card.score_fullhouse((3,3,3,3,3,)) == 25 

def test_score_sm_straight():
    assert card.score_sm_str8(tuple(sorted((1,3,2,4,6)))) == 30
    assert card.score_sm_str8(tuple(sorted((1,3,2,4,5,)))) == 30
    assert card.score_sm_str8(tuple(sorted((1,3,2,6,5)))) == 0 

    assert card.score_sm_str8(tuple(sorted((5,5,5,5,5)))) == 0 

def test_score_lg_straight():
    assert card.score_lg_str8(tuple(sorted([1,3,2,4,6]))) == 0
    assert card.score_lg_str8(tuple(sorted([1,3,2,4,5]))) == 40
    assert card.score_lg_str8(tuple(sorted([1,3,2,6,5]))) == 0 
    assert card.score_lg_str8(tuple(sorted([5,5,5,5,5]))) == 0 

def test_score_yahtzee():
    assert card.score_yahtzee(tuple(sorted([2,2,2,2,2]))) == 50 
    assert( card.score_yahtzee(tuple(sorted([2,2,6,2,2]))) ) == 0 

def test_odds_of_x_hits_with_n_dice():
    assert chance_of_exactly_x_hits(1,1) == 1/6
    assert round( chance_of_exactly_x_hits(2,7,12), 5) ==  0.09439

def test_straight_len():
    assert straight_len(tuple(sorted([1,2,0,5,3]))) == 4

def test_sim_ev():
    EV1DIEROLL = 3.5 # 1/6 * 1 + 1/6 * 2 + 1/6 * 3 + 1/6 * 4 + 1/6 * 5 + 1/6 * 6

    assert card.ev_for_slot(card.CHANCE,tuple(sorted([1,1,1,1,1])))[0] == EV1DIEROLL*5

    assert round(card.ev_for_slot(card.CHANCE,tuple(sorted([1,6,6,6,6])))[0] ) == round(4*6 + EV1DIEROLL )# AI should try for higher score with the 1 even though 4 of a kind exists 

    assert card.ev_for_slot(card.YAHTZEE, tuple(sorted([2,2,2,2,2])))[0] == 50 
    assert card.ev_for_slot(card.YAHTZEE, tuple(sorted([2,2,6,2,2])))[0] == 50 * 1/6 

    assert round( card.ev_for_slot(card.ACES, tuple(sorted([1,1,1,1,1])))[0] ,1) == 5.0 
    assert round( card.ev_for_slot(card.ACES, tuple(sorted([1,1,1,1,1])))[0] ,1) == 5.0 
    assert round( card.ev_for_slot(card.ACES, tuple(sorted([1,1,1,1,2])))[0] ,1) == round(4 + (1/6) ,1) 
    assert round( card.ev_for_slot(card.ACES, tuple(sorted([1,1,1,2,2])))[0] ,1) == round(3 + 2*(1/6) ,1)
    assert card.ev_for_slot(card.ACES, tuple(sorted([1,1,1,1,1])))[0] == 5 
    assert card.ev_for_slot(card.ACES, tuple(sorted([1,1,1,1,2])))[0] == 4 + 1/6 


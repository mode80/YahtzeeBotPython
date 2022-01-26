from yahtzeebot import *
import math

def test_count_of_n_choose_x_items():
    assert n_take_r(6,3,ordered=True,with_repetition=True)== 216 
    assert n_take_r(6,3,ordered=True,with_repetition=False)==120
    assert n_take_r(6,3,ordered=False,with_repetition=True)==56
    assert n_take_r(6,3,ordered=False,with_repetition=False)== 20
    assert n_take_r(15,6) == math.comb(15,6) 

def test_score_aces():  
    assert score_aces([2,1,2,1,5]) == 2
    assert score_aces([2,3,2,6,5]) == 0 

def test_score_upper_box():
    assert score_upperbox(4,[1,2,3,4,5]) == 4
    assert score_upperbox(4,[4,4,4,4,4]) == 20
    assert score_upperbox(4,[1,2,3,6,5]) == 0 

def test_score_three_of_a_kind():
    assert score_3ofakind([5,1,2,5,5])==18
    assert score_3ofakind([3,2,2,3,1])==0
    assert score_3ofakind([6,6,1,6,6])==25

def test_score_four_of_a_kind():
    assert score_4ofakind([3,2,3,3,3])==14
    assert score_4ofakind([3,2,2,3,3])==0
    assert score_4ofakind([3,3,3,3,3])==15

def test_score_fullhouse():
    assert score_fullhouse([2,2,3,3,3]) == 25
    assert score_fullhouse([2,2,3,3,2]) == 25
    assert score_fullhouse([2,2,1,3,3]) == 0 
    assert score_fullhouse([2,3,3,3,3]) == 0 
    assert score_fullhouse([1,2,3,4,5]) == 0 
    assert score_fullhouse([3,3,3,3,3]) == 25 

def test_score_sm_straight():
    assert score_sm_str8([1,3,2,4,6]) == 30
    assert score_sm_str8([1,3,2,4,5]) == 30
    assert score_sm_str8([1,3,2,6,5]) == 0 

    assert score_sm_str8([5,5,5,5,5]) == 0 

def test_score_lg_straight():
    assert score_lg_str8([1,3,2,4,6]) == 0
    assert score_lg_str8([1,3,2,4,5]) == 40
    assert score_lg_str8([1,3,2,6,5]) == 0 
    assert score_lg_str8([5,5,5,5,5]) == 0 

def test_score_yahtzee():
    assert score_yahtzee([2,2,2,2,2]) == 50 
    assert( score_yahtzee([2,2,6,2,2]) ) == 0 

def test_odds_of_x_hits_with_n_dice():
    assert chance_of_exactly_x_hits(1,1) == 1/6
    assert round( chance_of_exactly_x_hits(2,7,12), 5) ==  0.09439

def test_straight_len():
    assert straight_len([1,2,0,5,3]) == 4

def test_sim_ev():
    EV1DIEROLL = 3.5 # 1/6 * 1 + 1/6 * 2 + 1/6 * 3 + 1/6 * 4 + 1/6 * 5 + 1/6 * 6

    assert sim_ev([1,1,1,1,1],score_chance) == EV1DIEROLL*5

    assert round(sim_ev([1,6,6,6,6],score_4ofakind) ) == round(4*6 + EV1DIEROLL )# AI should try for higher score with the 1 even though 4 of a kind exists 

    assert sim_ev([2,2,2,2,2],score_yahtzee) == 50 
    assert sim_ev([2,2,6,2,2],score_yahtzee) == 50 * 1/6 

    assert round( sim_ev([1,1,1,1,1], score_aces) ,1) == 5.0 
    assert round( sim_ev([1,1,1,1,1], score_aces) ,1) == 5.0 
    assert round( sim_ev([1,1,1,1,2], score_aces) ,1) == round(4 + (1/6) ,1) 
    assert round( sim_ev([1,1,1,2,2], score_aces) ,1) == round(3 + 2*(1/6) ,1)
    assert sim_ev([1,1,1,1,1], score_aces) == 5 
    assert sim_ev([1,1,1,1,2], score_aces) == 4 + 1/6 


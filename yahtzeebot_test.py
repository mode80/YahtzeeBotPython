from yahtzeebot import *

def test_count_of_n_choose_x_combos():
    parems=(15,6)
    assert count_of_n_choose_x_combos(*parems) == math.comb(*parems) 

def test_score_aces():  
    assert score_aces([2,1,2,1,5]) == 2
    assert score_aces([2,3,2,6,5]) == 0 

def test_score_upper_box():
    assert score_upperbox(4,[1,2,3,4,5]) == 4
    assert score_upperbox(4,[4,4,4,4,4]) == 20
    assert score_upperbox(4,[1,2,3,6,5]) == 0 

def test_score_three_of_a_kind():
    assert score_three_of_a_kind([5,1,2,5,5])==18
    assert score_three_of_a_kind([3,2,2,3,1])==0
    assert score_three_of_a_kind([6,6,1,6,6])==25

def test_score_four_of_a_kind():
    assert score_four_of_a_kind([3,2,3,3,3])==14
    assert score_four_of_a_kind([3,2,2,3,3])==0
    assert score_four_of_a_kind([3,3,3,3,3])==15

def test_score_fullhouse():
    assert score_fullhouse([2,2,3,3,3]) == 25
    assert score_fullhouse([2,2,3,3,2]) == 25
    assert score_fullhouse([2,2,1,3,3]) == 0 
    assert score_fullhouse([2,3,3,3,3]) == 0 
    assert score_fullhouse([1,2,3,4,5]) == 0 
    assert score_fullhouse([3,3,3,3,3]) == 25 

def test_score_sm_straight():
    assert score_sm_straight([1,3,2,4,6]) == 30
    assert score_sm_straight([1,3,2,4,5]) == 30
    assert score_sm_straight([1,3,2,6,5]) == 0 

    assert score_sm_straight([5,5,5,5,5]) == 0 

def test_score_lg_straight():
    assert score_lg_straight([1,3,2,4,6]) == 0
    assert score_lg_straight([1,3,2,4,5]) == 40
    assert score_lg_straight([1,3,2,6,5]) == 0 
    assert score_lg_straight([5,5,5,5,5]) == 0 

def test_score_yahtzee():
    assert score_yahtzee([2,2,2,2,2]) == 50 
    assert( score_yahtzee([2,2,6,2,2]) ) == 0 

def test_odds_of_x_hits_with_n_dice():
    assert chance_of_exactly_x_hits(1,1) == 1/6
    assert round( chance_of_exactly_x_hits(2,7,12), 5) ==  0.09439

def test_ev_upperbox():
    assert round( sim_ev_upperbox(n=1, dicevals=[1,1,1,1,1], rolls=1) ,2) == 5.00 
    assert round( sim_ev_upperbox(n=1, dicevals=[1,1,1,1,1], rolls=2) ,2) == 5.00 
    assert round( sim_ev_upperbox(n=1, dicevals=[1,1,1,1,2], rolls=1) ,2) == round(4 + (1/6) ,2) 
    assert round( sim_ev_upperbox(n=1, dicevals=[1,1,1,2,2], rolls=1) ,2) == round(3 + 2*(1/6) ,2)
    assert ev_upperbox(1,[1,1,1,1,1],2) == 5 
    assert ev_upperbox(1,[1,1,1,1,2],1) == 4 + 1/6 
    assert round( ev_upperbox(1,[1,1,1,2,2],3), 2) ==  round( sim_ev_upperbox(1,[1,1,1,2,2],3), 2)

def test_ev_n_of_a_kind():
    paremslist=[
        (4,1,[1,1,1,1,4]),
        (4,1,[1,2,3,4,5]),
        (3,1,[1,2,3,4,5]),
        (3,1,[1,1,1,1,1]),
        (4,1,[1,1,2,3,4]),
        (4,1,[5,2,3,4,1])
    ]
    for parems in paremslist:
        assert                                          \
            round( sim_ev_n_of_a_kind(*parems)  ,1)==   \
            round( ev_n_of_a_kind(*parems)      ,1)

def test_ev_full_house():
    paremslist=[
         ([2,3,3,3,2]),
         ([4,4,4,4,1]),
         ([2,2,3,3,6]),
         ([5,5,5,5,5]),
         ([1,1,1,4,6]),
         ([5,2,3,4,1])
    ]
    for parems in paremslist:
        assert                                        \
            round( sim_ev_fullhouse(parems)  ,1)==   \
            round( ev_fullhouse(parems)      ,1)

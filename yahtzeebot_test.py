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

def test_ev_upperbox():
    assert round( sim_ev_upperbox(n=1, dievals=[1,1,1,1,1], rolls=1) ,1) == 5.0 
    assert round( sim_ev_upperbox(n=1, dievals=[1,1,1,1,1], rolls=2) ,1) == 5.0 
    assert round( sim_ev_upperbox(n=1, dievals=[1,1,1,1,2], rolls=1) ,1) == round(4 + (1/6) ,1) 
    assert round( sim_ev_upperbox(n=1, dievals=[1,1,1,2,2], rolls=1) ,1) == round(3 + 2*(1/6) ,1)
    assert ev_upperbox(1,[1,1,1,1,1],2) == 5 
    assert ev_upperbox(1,[1,1,1,1,2],1) == 4 + 1/6 
    assert round( ev_upperbox(1,[1,1,1,2,2],3), 1) ==  round( sim_ev_upperbox(1,[1,1,1,2,2],3), 1)

def test_ev_n_of_a_kind():
    EV1DIEROLL = 3.5 # 1/6 * 1 + 1/6 * 2 + 1/6 * 3 + 1/6 * 4 + 1/6 * 5 + 1/6 * 6
    assert round(sim_ev_n_of_a_kind(4, [1,6,6,6,6]) ) == round(4*6 + EV1DIEROLL )# AI should try for higher score with the 1 even though 4 of a kind exists 
    # assert round(sim_ev_n_of_a_kind(3, [1,1,1,6,6]) ,1) == 6+6+3*EV1DIEROLL # AI should try for 6s even though 1s are a sure thing
    # assert ev_n_of_a_kind(3, [1,1,1,6,6]) == 36 # AI should try for 6s even though 1s are a sure thing
    # paremslist=[
    #     (4,[1,1,1,1,4],1),
    #     (4,[1,2,3,4,5],1),
    #     (3,[1,2,3,4,5],1),
    #     (3,[1,1,1,1,1],1),
    #     (4,[1,1,2,3,4],1),
    #     (4,[5,2,3,4,1],1)
    # ]
    # for parems in paremslist:
    #     assert                                          \
    #         round( sim_ev_n_of_a_kind(*parems)  ,1)==   \
    #         round( ev_n_of_a_kind(*parems)      ,1)

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
        assert round( sim_ev_fullhouse(parems)) == round( ev_fullhouse(parems)) 

def test_straight_len():
    assert straight_len([1,2,0,5,3]) == 4

def test_dice_to_roll_for_str8():
    assert dice_to_roll_for_str8([1,2,3,4,5])==("00000",1)
    assert dice_to_roll_for_str8([1,2,1,4,5])==("00100",1/6)
    assert dice_to_roll_for_str8([1,2,1,1,5])==("00110",2*1/6*1/6)
    assert dice_to_roll_for_str8([1,2,1,1,6])[0]=="10111"
    assert dice_to_roll_for_str8([1,1,3,1,5])[0]=="01010"
    assert dice_to_roll_for_str8([1,2,3,4,5],4)==("00000",1)
    assert dice_to_roll_for_str8([1,2,1,4,5],4)[0]=="00101"
    assert dice_to_roll_for_str8([5,2,1,1,5],4)[0]=="00111"
    assert dice_to_roll_for_str8([1,2,1,1,6],4)[0]=="11111" # equal odds of rolling "10111".. one of these may be better for other box fallbacks :/
    assert dice_to_roll_for_str8([1,1,3,1,5],4)[0]=="11010"

def test_ev_straight():
    assert round(ev_straight([2,3,4,5,5],5) ,1) == round(2/6*40, 1) # outside shot 
    assert round(ev_straight([1,2,2,4,5],5) ,1) == round(1/6*40, 1) # gutshot 
    assert round(ev_straight([2,3,4,5,5],5) ,1) == round( sim_ev([2,3,4,5,5], score_lg_str8) ,1)
    assert round(ev_straight([1,2,2,4,5],5) ,1) == round( sim_ev([1,2,2,4,5], score_lg_str8) ,1)
     # assert round(sim_ev_straight([1,2,0,4,5],5) ,1) == round(1/6*40, 1) # gap1
    # assert round(sim_ev_straight([1,2,0,0,5],5) ,1) == round(fact(2) * (1/6)**2 * 40, 1) #gap2
    # assert round(sim_ev_straight([1,2,0,5,6],5) ,1) == round(fact(3) * (1/6)**2 * 40, 1) #gap3
    # assert round(sim_ev_straight([1,0,3,0,5],5) ,1) == round(fact(3) * (1/6)**2 * 40, 1) #gap1 2x
    # paremslist=[
    #      ([1,2,3,4,5]),
    #      ([1,2,4,5,1]),
    #      ([1,2,5,1,1]),
    #      ([1,2,5,6,1]),
    #      ([2,3,2,2,6]),
    #      ([1,3,5,6,6]),
    #      ([1,2,4,5,5])
    # ]
    # for parems in paremslist:
    #     assert                                        \
    #         round( ev_straight(parems)      ,1)==   \
    #         round( sim_ev_straight(parems)  ,1)   

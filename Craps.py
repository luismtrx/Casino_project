import random 
import tkinter as tk


def printbets():
    betcount = [0]
    betmax = [0, '1', '2', '3', '4']
    keepbet = 'y'
    print("If you wanna bet on the come out role you need to have betted on the pass or no pass")
    while keepbet == 'y':
        if betcount == betmax:
            print ("You have betted on all 4 bets lets start the game already")
            break
        print ("What would you like to Bet on?")
        count = 0
        betlist = ['1. Pass/No Pass', '2. Field Bet', '3. Proposition Bet', '4. Odds Bet']
        while count < 4:
            print (betlist[count])
            count += 1
        bet = input("Bet number: ")
        while int(bet) <= 0 or int(bet) > 4:
            bet = input("Please pick a valid option ")
        while bet in betcount:
            bet = input("Sorry you already betted on this please pick another bet: ")
            while int(bet) <= 0 or int(bet) > 4:
                bet = input("Please pick a valid option ")
            if bet not in betcount:
                break
        betcount.append(bet)
        keepbet = input("Do you want to bet on anything else y or n: ")
        if keepbet == 'n':
            break
    return betcount 

def rolldice():
    dice1_int = random.randint(1,6)
    dice2_int = random.randint(1,6)
    print(f"Dice 1: {dice1_int}")
    print(f"Dice 2: {dice2_int}")
    sum = dice1_int + dice2_int
    print(f"total:",sum)
    details = {
        "dice1" : dice1_int,
        "dice2" : dice2_int,
        "sum" : sum
    }
    return details

def game(bet, bet1, bet2, bet3, bet4, cheat):
    print (bet)
    craps = [2,3,12]
    total = 0
    betp = 1
    confirmobet = 'y'
    print(f"Roll you dices")
    string = input("press enter to roll: ")
    dice = rolldice()
    if cheat == 1:
        print("the dice are loded and still rolling what numbers do you want them to be")
        Fdice1 = input("Dice1: ")
        Fdice2 = input("Dice2: ")
        Ftotal = int(Fdice1) + int(Fdice2)
        dice['sum'] = int(Ftotal)
        dice['dice1'] = int(Fdice1)
        dice['dice2'] = int(Fdice2)

        
    if '1' in bet:
        winnum = (4, 5, 6, 8, 9, 10)
        if dice['sum'] == 7 or dice['sum'] == 11:
            print (f"Congratulations you won here is your pay out")
            betp=2
            total = int(bet1) + int(bet1)
        elif dice['sum'] in winnum:
            print(f"Congrats you passed the first check now you need to roll a ",dice['sum'], " again but if you roll a 7 you lose")
            if '4' in bet:
                print ("are you sure you want to stand on your odd bet y or n")
                confirmobet = input()
            string = input("press enter to roll: ")
            dice2 = rolldice()
            while dice2['sum'] != dice['sum']:
                if dice2['sum'] == 7:
                    print("better luck next time")
                    betp = 0
                    break
                string = input("press enter to roll: ")
                dice2 = rolldice()
            if dice2['sum'] == dice['sum']:
                    print("congrats you won")
                    total = int(bet1) + int(bet1)
                    betp = 1
        else:
            print(f"better luck next time")
            betp = 0
    print("Your total with 1st bet:",total)
    if '2' in bet:
        feildwin = (2, 3, 4, 9, 10, 11, 12)
        if dice['sum'] in feildwin:
            if dice['sum'] == 2 or dice['sum']==12:
                bet2 = int(bet2) * 3
                total = int(total) + int(bet2)
            else:
                bet2 = int(bet2) + int(bet2)
                total = int(total) + int(bet2)
        else:
            print("you lost your feild bet sorry")
    print("Your total with 2nd bet ",total)
    if '3' in bet:
        if bet3[0] > 0:
            if dice['sum'] == 7:
                bet3[0] = bet3[0] * 6
            else:
                bet3[0] = 0
        if bet3[1] > 0:
            if dice['dice1'] == 3 and dice['dice2'] == 3:
                bet3[1] = bet3[1] * 11
            else:
                bet3[1] = 0
        if bet3[2] > 0:
            if dice['dice1'] == 5 and dice['dice2'] == 5:
                bet3[2] = bet3[2] * 9
            else:
                bet3[2] = 0
        if bet3[3] > 0:
            if dice['dice1'] == 4 and dice['dice2'] == 4:
                bet3[3] = bet3[3] * 11
            else:
                bet3[3] = 0
        if bet3[4] > 0:
            if dice['dice1'] == 2 and dice['dice2'] == 2:
                bet3[4] = bet3[4] * 9
            else:
                bet3[4] = 0
        if bet3[5] > 0:
            if (dice['dice1'] == 1 and dice['dice2'] == 2) or (dice['dice1'] == 2 and dice['dice2'] == 1):
                bet3[5] = bet3[5] * 17
            else:
                bet3[5] = 0
        if bet3[6] > 0:
            if dice['dice1'] == 1 and dice['dice2'] == 1:
                bet3[6] = bet3[6] * 32
            else:
                bet3[6] = 0
        if bet3[7] > 0:
            if dice['dice1'] == 6 and dice['dice2'] == 6:
                bet3[7] = bet3[7] * 32
            else:
                bet3[7] = 0
        if bet3[8] > 0:
            if (dice['dice1'] == 6 and dice['dice2'] == 5) or (dice['dice1'] == 5 and dice['dice2'] == 6):
                bet3[8] = bet3[8] * 17
            else:
                bet3[8] = 0
        if bet3[9] > 0:
            if dice['sum'] in craps:
                bet3[9] = bet3[9] * 9
            else:
                bet3[9] = 0
        print(bet3)
        Tbet = sum(bet3)
        total = int(total) + int(Tbet)
    print("Your total for 3rd bet: ",total)
    if '4' in bet:
        if '1' in bet:
            if confirmobet == 'y':
                if betp == 1:
                    if dice2['sum'] == 4 or dice2['sum'] == 10:
                        bet4 = int(bet4)*2
                    elif dice2['sum'] == 5 or dice2['sum'] == 9:
                        holdbet = int(bet4) / 2
                        bet4 = int(bet4) + holdbet
                    elif dice2['sum'] == 6 or dice2['sum'] == 8:
                        holdbet = int(bet4)/5
                        bet4 = int(bet4) + holdbet
                    else:
                        bet4 = 0
                if betp == 0:
                    print("better luck next time on the odds bet")
                    bet4 = 0
                if betp == 2:
                    print("you won instantly so no odds bet needed")
            elif confirmobet == 'n':
                print("we wont do the odds bet since you said no")
        else:
            print("Sorry you didnt bet on the pass no pass")
        total = int(total) + int(bet4)
    print("Your total with 4th bet: ",total)
    return total

                

    
    
def probet(money):
    keepbet = 'y'
    procount = [0,0,0,0,0,0,0,0,0,0]
    betmax = [0]
    betcheck = [0,'1','2','3','4','5','6','7','8','9','10']
    while keepbet == 'y':
        if betcheck == betmax:
            print("You have betted on all the bets lets play the game now")
            break
        betlist= ['1. next roll 7','2. roll 3 3', '3. roll 5 5', '4. roll 4 4', '5. roll 2 2', '6. roll 1 3', '7. roll 1 1', '8. roll 6 6', '9. roll 6 5', '10. roll any craps']
        count = 0
        while count < 10:
            print(betlist[count])
            count += 1
        bet = input("Bet number: ")
        while int(bet) <= 0 or int(bet) > 10:
            bet = input("Please pick a valid option ")
        while bet in betmax:
            bet = input("Sorry you already betted on this please pick another bet: ")
            while int(bet) <= 0 or int(bet) > 10:
                bet = input("Please pick a valid option ")
            if bet not in betmax:
                break
        betmax.append(bet)
        newbet = input ("How much money would you like to bet: ")
        while int(newbet) < 0 or int(newbet) > int(money):
            newbet = input("You dont have enough money for that bet: ")
        procount[int(bet)-1] = int(newbet)
        money = int(money) - procount[int(bet)-1]
        keepbet = input("Do you want to bet on anything else y or n: ")
        if keepbet == 'n':
            break
    return procount, money

    
play = 'y'
cheat = 0
cheatIA = 0
lost = 0
money = input("How much money are you putting on the table: ")
while int(money) <= 0:
    money = input("Please Friend don't waste everyones time: ")
else:
    print("Perfect here are your chips")
while play == 'y':       
    betnum = printbets()
    
    betm1 = 0 
    betm2 = 0 
    betm3 = [] 
    betm4 = 0
    if '1' in betnum:
        betm1 = input("How much would you like to bet for 1: ")
        while int(betm1) < 0 or int(betm1) > int(money):
            betm1 = input("You dont have enough to make that kind of bet try again: ")
        else:
            money = int(money) - int(betm1)
        print(money, " 1")
    if '2' in betnum:
        bet2 = 0
        betm2 = input("How much would you like to bet for 2: ")
        while int(betm2) < 0 or int(betm2) > money:
            betm2 = input("You dont have enough to make that kind of bet try again: ")
        else:
            money = int(money) - int(betm2)
        print(money, " 2")
    if '3' in betnum:
        betm3,money = probet(int(money))
        print(money, " 3")
    if '4' in betnum:
        betm4 = input("How much would you like to bet for 4: ")
        while int(betm4) < 0 or int(betm4) > money:
            betm4 = input("You dont have enough to make that kind of bet try again: ")
        else:
            money = int(money) - int(betm4)
        print(money, " 4")
    
    betmoney = game(betnum, betm1, betm2, betm3, betm4, cheatIA)
    print(betmoney)
    print(money)
    if int(cheat) == 3:
        print("Havent you been lucky im going to have to ask you to leave")
        break
    cheatIA = 0
    if int(betmoney) == 0:
        lost = int(lost) + 1
    if int(lost) >= 3:
        print("someone approches you, It appers that you have lost 3 or more times you want a little help with that?")
        confirm = input("y or n: ")
        if confirm == 'y':
            cheat = int(cheat) + 1
            lost = 0
            cheatIA = 1
    
    money = int(money) + int(betmoney)
    
    print("Your money: ", money)
    play = input("Do you want to play again y or n: ")
    if play == 'n':
        break
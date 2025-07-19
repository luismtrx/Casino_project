import tkinter as tk
from tkinter import messagebox
import random

from Casino_APC import CasinoStats

def play_craps(gambler, parent, bal):
    win = tk.Toplevel(parent)
    win.title("Craps Game")
    win.geometry("400x350")
    loss_streak = [0]

    # Labels
    balance_label = tk.Label(win, text=f"Balance: ${gambler.balance:.2f}", font=("Arial", 14))
    balance_label.pack(pady=5)
    status_label = tk.Label(win, text="Place your bet and press 'Roll Dice'", font=("Arial", 12))
    status_label.pack(pady=5)

    # Bet entry
    bet_frame = tk.Frame(win)
    bet_frame.pack(pady=5)
    tk.Label(bet_frame, text="Bet Amount: $", font=("Arial", 12)).pack(side="left")
    bet_entry = tk.Entry(bet_frame, width=10, font=("Arial", 12))
    bet_entry.pack(side="left")

    # Dice display
    dice_frame = tk.Frame(win)
    dice_frame.pack(pady=10)
    dice_label_1 = tk.Label(dice_frame, text="?", font=("Arial", 48))
    dice_label_1.pack(side="left", padx=15)
    dice_label_2 = tk.Label(dice_frame, text="?", font=("Arial", 48))
    dice_label_2.pack(side="left", padx=15)

    # Game state variables
    point = [None]  # The "point" number in phase 2
    phase = ['come_out']  # 'come_out' or 'point'

    cheat_var = tk.IntVar(value=0)  # checkbox for cheat option, enabled after 3 losses

    def update_balance_label():
        balance_label.config(text=f"Balance: ${gambler.balance:.2f}")
        bal.set(f"Balance: ${gambler.balance:.2f}")

    def reset_game():
        point[0] = None
        phase[0] = 'come_out'
        status_label.config(text="Place your bet and press 'Roll Dice'")
        dice_label_1.config(text="?")
        dice_label_2.config(text="?")
        cheat_var.set(0)
        cheat_checkbox.config(state='disabled')
        roll_button.config(state='normal')

    def roll_dice():
        if gambler.is_banned:
            messagebox.showerror("Cheater", "You are banned for cheating. Manager must restore your access.")
            win.destroy()
            return

        try:
            bet = float(bet_entry.get())
            if bet <= 0 or bet > gambler.balance:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Bet", f"Enter a valid bet between 1 and {int(gambler.balance)}")
            return

        gambler.balance -= bet
        update_balance_label()

        cheat_now = False
        if cheat_var.get() == 1:
            cheat_now = True
            gambler.add_cheat()
            messagebox.showinfo("Cheat", "You CHEATED! Dice set to win conditions.")

        # Roll dice
        if cheat_now:
            # cheat logic: make dice sum a winning number depending on phase
            if phase[0] == 'come_out':
                # force 7 or 11 to win on come out roll
                winning_sum = random.choice([7, 11])
            else:
                # force hitting the point to win
                winning_sum = point[0]
            # create dice combination matching winning_sum (1-6 each)
            possible_rolls = [(d1,d2) for d1 in range(1,7) for d2 in range(1,7) if d1 + d2 == winning_sum]
            roll1, roll2 = random.choice(possible_rolls)
        else:
            roll1, roll2 = random.randint(1,6), random.randint(1,6)

        dice_label_1.config(text=str(roll1))
        dice_label_2.config(text=str(roll2))

        dice_sum = roll1 + roll2
        win_amt = 0
        won = False

        # Evaluate game logic
        if phase[0] == 'come_out':
            if dice_sum in [7, 11]:
                # immediate win
                win_amt = bet * 2
                status_label.config(text=f"You rolled {dice_sum}. You WIN! Payout: ${win_amt}")
                phase[0] = 'come_out'  # reset phase just for clarity
                won = True
                loss_streak[0] = 0
            elif dice_sum in [2, 3, 12]:
                # immediate loss
                status_label.config(text=f"You rolled {dice_sum}. You LOSE!")
                phase[0] = 'come_out'
                won = False
                loss_streak[0] += 1
            else:
                # establish point
                point[0] = dice_sum
                phase[0] = 'point'
                status_label.config(text=f"Point is set to {point[0]}. Roll again to hit point before 7!")
                won = None  # game continues
        else:  # point phase
            if dice_sum == point[0]:
                # player wins, hits point
                win_amt = bet * 2
                status_label.config(text=f"You hit your POINT ({point[0]}). You WIN! Payout: ${win_amt}")
                phase[0] = 'come_out'
                point[0] = None
                won = True
                loss_streak[0] = 0
            elif dice_sum == 7:
                # player loses
                status_label.config(text=f"You rolled a 7 before hitting point. You LOSE!")
                phase[0] = 'come_out'
                point[0] = None
                won = False
                loss_streak[0] += 1
            else:
                # roll again, no win/loss
                status_label.config(text=f"You rolled {dice_sum}. Keep rolling for {point[0]}!")
                won = None

        # Update gambler balance and records only if round ended (win or lose)
        if won is not None:
            gambler.balance += win_amt
            update_balance_label()
            gambler.record_game(won, bet, win_amt, "Craps", cheat_now)
            CasinoStats().add_bet(bet, win_amt)
            CasinoStats().add_game()

            # Reset cheat checkbox if loss streak < 3
            if loss_streak[0] >= 3:
                cheat_btn.config(state='normal')
            else:
                cheat_btn.config(state='disabled')

            if gambler.cheat_count >= 3:
                gambler.save()
                messagebox.showerror("Banned", "You cheated 3 times. Manager must restore your access.")
                win.destroy()
                return

            if gambler.balance <= 0:
                messagebox.showinfo("Game Over", "You're out of money! Deposit to play again.")
                win.destroy()
                return

        bet_entry.delete(0, tk.END)

    roll_button = tk.Button(win, text="Roll Dice", font=("Arial", 14), width=12, command=roll_dice)
    roll_button.pack(pady=10)

    cheat_btn = tk.Button(win, text="Cheat (Win!)", command = lambda: roll_dice(True))
    cheat_btn.pack(pady=5)

    reset_button = tk.Button(win, text="Reset Game", command=reset_game)
    reset_button.pack(pady=5)

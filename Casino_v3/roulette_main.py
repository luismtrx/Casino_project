import tkinter as tk
from tkinter import messagebox
import random

from Casino_APC import CasinoStats

RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMBERS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
CHIP_VALUES = [1, 5, 10, 25, 100]
CHIP_COLORS = {1: 'white', 5: 'red', 10: 'blue', 25: 'green', 100: 'black'}





def play_roulette(gambler, parent, bal):
    win = tk.Toplevel(parent)
    win.title("Roulette Game")
    win.geometry("900x440")
    bets = {}
    history = []
    loss_streak = [0]
    cheat_count = [gambler.cheat_count]

  
    balance_label = tk.Label(win, text=f"Balance: ${gambler.balance:.2f}", font=("Arial", 14))
    balance_label.grid(row=0, column=0, sticky='w')
    result_label = tk.Label(win, text="", font=("Arial", 14))
    result_label.grid(row=0, column=1)
    history_frame = tk.Frame(win)
    history_frame.grid(row=1, column=2, sticky='n')
    history_title = tk.Label(history_frame, text="History:")
    history_title.pack(anchor='n')
    history_list = tk.Listbox(history_frame, height=6)
    history_list.pack()
    bets_frame = tk.Frame(win)
    bets_frame.grid(row=2, column=2, sticky='n')
    bets_title = tk.Label(bets_frame, text="Bets:")
    bets_title.pack(anchor='n')
    bets_list = tk.Listbox(bets_frame, height=10)
    bets_list.pack()
    selected_chip = tk.IntVar(value=1)
    board_frame = tk.Frame(win)
    board_frame.grid(row=1, column=0)
    def get_color(num):
        if num in RED_NUMBERS: return 'red'
        elif num in BLACK_NUMBERS: return 'black'
        return 'green'
    def update_balance():
        balance_label.config(text=f"Balance: ${gambler.balance:.2f}")
        bal.set(f"Balance: ${gambler.balance:.2f}")
    def update_bets_label():
        bets_list.delete(0, tk.END)
        if not bets:
            bets_list.insert(tk.END, "None")
        else:
            for k, v in bets.items():
                bets_list.insert(tk.END, f"{k}: ${v}")
    def update_history_label():
        history_list.delete(0, tk.END)
        for num, color in history[-5:]:
            history_list.insert(tk.END, f"{num} ({color[0].upper()})")
    def place_bet(position):
        chip_value = selected_chip.get()
        if chip_value > gambler.balance:
            messagebox.showwarning("Insufficient Funds", "Not enough balance to place this chip.")
            return
        gambler.balance -= chip_value
        update_balance()
        if position not in bets: bets[position] = 0
        bets[position] += chip_value
        update_bets_label()
    def clear_bets():
        total_bet = sum(bets.values())
        gambler.balance += total_bet
        bets.clear()
        update_balance()
        update_bets_label()
    def get_payout(bet):
        if isinstance(bet, int) or bet in ['0', '00']: return 35
        elif bet in ['RED', 'BLACK', 'ODD', 'EVEN', '1 to 18', '19 to 36']: return 1
        elif bet in ['1st 12', '2nd 12', '3rd 12']: return 2
        return 0
    def is_winning_bet(bet, result):
        if bet == result: return True
        elif bet == 'RED' and result in RED_NUMBERS: return True
        elif bet == 'BLACK' and result in BLACK_NUMBERS: return True
        elif bet == 'ODD' and isinstance(result, int) and result % 2 == 1: return True
        elif bet == 'EVEN' and isinstance(result, int) and result % 2 == 0: return True
        elif bet == '1 to 18' and isinstance(result, int) and 1 <= result <= 18: return True
        elif bet == '19 to 36' and isinstance(result, int) and 19 <= result <= 36: return True
        elif bet == '1st 12' and isinstance(result, int) and 1 <= result <= 12: return True
        elif bet == '2nd 12' and isinstance(result, int) and 13 <= result <= 24: return True
        elif bet == '3rd 12' and isinstance(result, int) and 25 <= result <= 36: return True
        return False
    def evaluate_bets(result, cheated):
        winnings = 0
        win = False
        for bet, amount in bets.items():
            if is_winning_bet(bet, result):
                payout = get_payout(bet)
                winnings += amount * (payout + 1)
                win = True
        gambler.balance += winnings
        update_balance()
        CasinoStats().add_bet(sum(bets.values()), winnings)
        CasinoStats().add_game()
        gambler.record_game(win, sum(bets.values()), winnings, "Roulette", cheated)
        messagebox.showinfo("Results", f"Winning number: {result}\nColor: {get_color(result).upper()}\nWinnings: ${winnings}")
        return win
    def spin(cheat_mode=False):
        if gambler.is_banned:
            win.destroy()
            messagebox.showerror("Cheater", "You are banned for cheating. Manager must restore your access.")
            return
        if not bets:
            messagebox.showinfo("No Bets", "Please place at least one bet before spinning.")
            return
        cheated = 0
        if cheat_mode:
            
            for bet in bets:
                if isinstance(bet, int) or bet in ['0', '00']:
                    result = bet
                    break
                elif bet == 'RED':
                    result = random.choice(list(RED_NUMBERS)); break
                elif bet == 'BLACK':
                    result = random.choice(list(BLACK_NUMBERS)); break
                elif bet == 'ODD':
                    result = random.choice([n for n in range(1, 37) if n % 2 == 1]); break
                elif bet == 'EVEN':
                    result = random.choice([n for n in range(1, 37) if n % 2 == 0]); break
                elif bet == '1 to 18':
                    result = random.randint(1, 18); break
                elif bet == '19 to 36':
                    result = random.randint(19, 36); break
                elif bet == '1st 12':
                    result = random.randint(1, 12); break
                elif bet == '2nd 12':
                    result = random.randint(13, 24); break
                elif bet == '3rd 12':
                    result = random.randint(25, 36); break
            else:
                result = random.choice(list(range(1, 37)) + [0, '00'])
            gambler.add_cheat()
            cheated = 1
            messagebox.showinfo("Cheat", "You CHEATED! Automatic win.")
        else:
            result = random.choice(list(range(1, 37)) + [0, '00'])
        color = get_color(result) if isinstance(result, int) else 'green'
        result_label.config(text=f"Result: {result} ({color.upper()})")
        history.append((result, color))
        update_history_label()
        win = evaluate_bets(result, cheated)
        bets.clear()
        update_bets_label()
        if win:
            loss_streak[0] = 0
        else:
            loss_streak[0] += 1
        if gambler.cheat_count >= 3:
            gambler.save()
            win.destroy()
            messagebox.showerror("Banned", "You cheated 3 times. Manager must restore your access.")
            return
        if gambler.balance <= 0:
            messagebox.showinfo("Game Over", "You're out of money! Deposit to play again.")
            win.destroy()

    chip_frame = tk.Frame(win)
    chip_frame.grid(row=2, column=0, sticky='w')
    for value in CHIP_VALUES:
        fg_color = 'white' if value in [10, 100] else 'black'
        tk.Radiobutton(
            chip_frame, text=f"${value}", variable=selected_chip,
            value=value, indicatoron=0, bg=CHIP_COLORS[value], fg=fg_color, width=5
        ).pack(side='left')
    clear_btn = tk.Button(chip_frame, text="Clear Bets", command=clear_bets)
    clear_btn.pack(side='left', padx=10)
    
    cheat_btn = tk.Button(win, text="💀 Cheat (Win!)", command=lambda: spin(True), width=12)
    cheat_btn.grid(row=2, column=1, sticky="e", padx=85)

    spin_btn = tk.Button(win, text="Spin ", command=lambda: spin(False), width=12, bg="red", fg="white")
    spin_btn.grid(row=3, column=1, sticky="e", padx=85)
  
    def draw_board():
        for widget in board_frame.winfo_children():
            widget.destroy()
        tk.Button(board_frame, text="0", bg="green", fg="white", width=4, height=2,
            command=lambda: place_bet('0')).grid(row=0, column=0, rowspan=2)
        tk.Button(board_frame, text="00", bg="green", fg="white", width=4, height=2,
            command=lambda: place_bet('00')).grid(row=2, column=0, rowspan=2)
        number = 1
        for col in range(1, 13):
            for row in range(3):
                bg_color = get_color(number)
                fg_color = 'white' if bg_color == 'black' else 'black'
                tk.Button(board_frame, text=str(number), width=4, height=2,
                    bg=bg_color, fg=fg_color, command=lambda n=number: place_bet(n)).grid(row=row, column=col)
                number += 1
        outside_bets = [
            ('1st 12', 3, 1), ('2nd 12', 3, 5), ('3rd 12', 3, 9),
            ('1 to 18', 4, 1), ('EVEN', 4, 3), ('RED', 4, 5),
            ('BLACK', 4, 7), ('ODD', 4, 9), ('19 to 36', 4, 11)
        ]
        for label, row_, col in outside_bets:
            bg = 'red' if label == 'RED' else 'black' if label == 'BLACK' else 'SystemButtonFace'
            fg = 'white' if label == 'BLACK' else 'black'
            tk.Button(board_frame, text=label, width=10, bg=bg, fg=fg, command=lambda l=label: place_bet(l)).grid(row=row_, column=col, columnspan=2)
    draw_board()

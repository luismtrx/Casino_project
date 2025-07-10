import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import datetime
import sys

DB = "casino5.db"
database = sqlite3.connect(DB)
cursor = database.cursor()

#gambler table in sqlite
cursor.execute(""" CREATE TABLE IF NOT EXISTS GAMBLER (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    FIRST_NAME TEXT NOT NULL,
    LAST_NAME TEXT NOT NULL,
    BIRTHYEAR INTEGER NOT NULL,
    EMAIL TEXT NOT NULL,
    BALANCE REAL NOT NULL,
    CHEAT_COUNT INTEGER NOT NULL DEFAULT 0,
    IS_BANNED INTEGER NOT NULL DEFAULT 0,
    MONEY_WON REAL NOT NULL DEFAULT 0,
    MONEY_LOST REAL NOT NULL DEFAULT 0,
    GAMES_PLAYED INTEGER NOT NULL DEFAULT 0,
    WINS INTEGER NOT NULL DEFAULT 0,
    LOSSES INTEGER NOT NULL DEFAULT 0
);
""")

#manager table 
cursor.execute(""" CREATE TABLE IF NOT EXISTS MANAGER (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    USERNAME TEXT NOT NULL,
    PASSWORD TEXT NOT NULL
);
""")
if cursor.execute("SELECT COUNT(*) FROM MANAGER").fetchone()[0] == 0:
    cursor.executemany("INSERT INTO MANAGER (USERNAME, PASSWORD) VALUES (?,?)",
        [("admin", "adminpass"), ("manager1", "RT1"), ("manager2", "RT2")])
    database.commit()

#casino stats table
cursor.execute("""CREATE TABLE IF NOT EXISTS CASINO_STATS (
    ID INTEGER PRIMARY KEY,
    TOTAL_MADE REAL NOT NULL,
    TOTAL_PAYOUT REAL NOT NULL,
    NUM_BETS_MADE INTEGER NOT NULL,
    NUM_GAMBLERS INTEGER NOT NULL,
    CHEATERS_KICKED INTEGER NOT NULL
)
""")
if cursor.execute("SELECT COUNT(*) FROM CASINO_STATS").fetchone()[0] == 0:
    cursor.execute("INSERT INTO CASINO_STATS VALUES (1, 0, 0, 0, 0, 0)")
    database.commit()

#cheater table 
cursor.execute("""CREATE TABLE IF NOT EXISTS CHEATERS (
    GAMBLER_ID INTEGER,
    CHEAT_COUNT INTEGER,
    KICKED_COUNT INTEGER,
    PRIMARY KEY(GAMBLER_ID)
)
""")

#game history table 
cursor.execute("""CREATE TABLE IF NOT EXISTS GAME_HISTORY (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    GAMBLER_ID INTEGER,
    GAME TEXT,
    WON INTEGER,
    AMOUNT_BET REAL,
    AMOUNT_WON REAL,
    CHEATED INTEGER,
    TIMESTAMP TEXT
)
""")
database.commit()


class Gambler:
    def __init__(self, gambler_id):
        row = cursor.execute("SELECT * FROM GAMBLER WHERE ID=?", (gambler_id,)).fetchone()
        if not row:
            raise Exception("Gambler not found.")
        self.id = row[0]
        self.first_name = row[1]
        self.last_name = row[2]
        self.birthyear = row[3]
        self.email = row[4]
        self.balance = row[5]
        self.cheat_count = row[6]
        self.is_banned = bool(row[7])
        self.money_won = row[8]
        self.money_lost = row[9]
        self.games_played = row[10]
        self.wins = row[11]
        self.losses = row[12]
    def save(self):
        cursor.execute("""UPDATE GAMBLER SET BALANCE=?, CHEAT_COUNT=?, IS_BANNED=?,
                        MONEY_WON=?, MONEY_LOST=?, GAMES_PLAYED=?, WINS=?, LOSSES=?
                        WHERE ID=?""", (self.balance, self.cheat_count, int(self.is_banned),
                        self.money_won, self.money_lost, self.games_played,
                        self.wins, self.losses, self.id))
        database.commit()
    def add_cheat(self):
        self.cheat_count += 1
        if self.cheat_count >= 3:
            self.is_banned = True
            CasinoStats().kick_cheater()
            row = cursor.execute("SELECT * FROM CHEATERS WHERE GAMBLER_ID=?", (self.id,)).fetchone()
            if row:
                cursor.execute("UPDATE CHEATERS SET CHEAT_COUNT=?, KICKED_COUNT=KICKED_COUNT+1 WHERE GAMBLER_ID=?",
                               (self.cheat_count, self.id))
            else:
                cursor.execute("INSERT INTO CHEATERS VALUES (?, ?, 1)", (self.id, self.cheat_count))
            database.commit()
        self.save()
    def restore(self):
        self.is_banned = False
        self.cheat_count = 0
        self.save()
    def record_game(self, win, bet, payout, game, cheated):
        self.games_played += 1
        if win:
            self.wins += 1
            self.money_won += payout
        else:
            self.losses += 1
            self.money_lost += bet
        self.save()
        cursor.execute("""
            INSERT INTO GAME_HISTORY (GAMBLER_ID, GAME, WON, AMOUNT_BET, AMOUNT_WON, CHEATED, TIMESTAMP)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.id, game, int(win), bet, payout, int(cheated), datetime.datetime.now().isoformat()))
        database.commit()

class CasinoStats:
    def __init__(self):
        row = cursor.execute("SELECT * FROM CASINO_STATS WHERE ID=1").fetchone()
        self.id = row[0]
        self.total_made = row[1]
        self.total_payout = row[2]
        self.num_bets_made = row[3]
        self.num_gamblers = row[4]
        self.num_games = row[5]
        self.cheaters_kicked = row[6]
    def add_bet(self, bet, payout):
        self.total_made += bet
        self.total_payout += payout
        self.num_bets_made += 1
        self._save()
    def add_gambler(self):
        self.num_gamblers += 1
        self._save()
    def add_game(self):
        self.num_games += 1
        self._save()
    def kick_cheater(self):
        self.cheaters_kicked += 1
        self._save()
    def _save(self):
        cursor.execute("""UPDATE CASINO_STATS SET
            TOTAL_MADE=?, TOTAL_PAYOUT=?, NUM_BETS_MADE=?,
            NUM_GAMBLERS=?, NUM_GAMES=?, CHEATERS_KICKED=?
            WHERE ID=1
        """, (self.total_made, self.total_payout, self.num_bets_made,
              self.num_gamblers, self.num_games, self.cheaters_kicked))
        database.commit()


# --- MENUS ---

def main_menu():

    root = tk.Tk()
    root.title("Wentworth Casino")
    root.geometry("420x410")

    tk.Label(root, text="Welcome to Wentworth Casino", font=("Arial", 20, "bold")).pack(pady=14)
    tk.Button(root, text="Register as Gambler", width=30, height=2, command=lambda: register_gambler(root)).pack(pady=7)
    tk.Button(root, text="Login as Gambler", width=30, height=2, command=lambda: gambler_login(root)).pack(pady=7)
    tk.Button(root, text="Manager Login", width=30, height=2, command=lambda: manager_login(root)).pack(pady=7)
    tk.Button(root, text="Exit", width=30, height=2, command=root.destroy).pack(pady=7)

    root.mainloop()

def register_gambler(parent):
    win = tk.Toplevel(parent)
    win.title("Register Gambler")
    win.geometry("350x370")
    tk.Label(win, text="First Name:").pack()
    first = tk.Entry(win); first.pack()
    tk.Label(win, text="Last Name:").pack()
    last = tk.Entry(win); last.pack()
    tk.Label(win, text="Birth Year (YYYY):").pack()
    birth = tk.Entry(win); birth.pack()
    tk.Label(win, text="Email:").pack()
    email = tk.Entry(win); email.pack()
    tk.Label(win, text="Initial Deposit ($):").pack()
    dep = tk.Entry(win); dep.pack()
    def submit():
        if not (first.get() and last.get() and birth.get() and email.get() and dep.get()):
            messagebox.showerror("Error", "All fields required!"); return
        try:
            byear = int(birth.get())
            age = datetime.datetime.now().year - byear
            if age < 21:
                messagebox.showerror("Error", "You must be at least 21.")
                return
            deposit = float(dep.get())
            if deposit < 1:
                messagebox.showerror("Error", "Deposit at least $1.")
                return
        except Exception:
            messagebox.showerror("Error", "Check your inputs.")
            return
        cursor.execute("INSERT INTO GAMBLER (FIRST_NAME, LAST_NAME, BIRTHYEAR, EMAIL, BALANCE, CHEAT_COUNT, IS_BANNED) VALUES (?,?,?,?,?,?,?)",
                       (first.get(), last.get(), byear, email.get(), deposit, 0, 0))
        database.commit()
        CasinoStats().add_gambler()
        messagebox.showinfo("Success", "Registered successfully! You can now log in.")
        win.destroy()
    tk.Button(win, text="Register", command=submit, width=18, height=2).pack(pady=18)

def gambler_login(parent):
    win = tk.Toplevel(parent)
    win.title("Gambler Login")
    win.geometry("350x230")
    tk.Label(win, text="Enter Gambler ID:").pack()
    gid = tk.Entry(win); gid.pack()
    def login():
        try:
            g = Gambler(int(gid.get()))
            if g.is_banned:
                messagebox.showerror("Banned", "You are currently banned for cheating. Manager must restore your access.")
                win.destroy(); return
            gambler_menu(g, parent)
            win.destroy()
        except Exception:
            messagebox.showerror("Error", "Invalid Gambler ID.")
    tk.Button(win, text="Login", width=16, height=2, command=login).pack(pady=18)

def manager_login(parent):
    win = tk.Toplevel(parent)
    win.title("Manager Login")
    win.geometry("330x200")
    tk.Label(win, text="Username:").pack()
    un = tk.Entry(win); un.pack()
    tk.Label(win, text="Password:").pack()
    pw = tk.Entry(win, show="*"); pw.pack()
    def login():
        row = cursor.execute("SELECT * FROM MANAGER WHERE USERNAME=? AND PASSWORD=?", (un.get(), pw.get())).fetchone()
        if not row:
            messagebox.showerror("Error", "Invalid login.")
        else:
            win.destroy()
            open_manager_menu(un.get(), parent)
    tk.Button(win, text="Login", command=login, width=16, height=2).pack(pady=16)

#gambler menu and game 

def gambler_menu(gambler, parent):
    win = tk.Toplevel(parent)
    win.title(f"Gambler: {gambler.first_name} {gambler.last_name}")
    win.geometry("420x470")
    bal = tk.StringVar()
    def update_bal():
        bal.set(f"Balance: ${gambler.balance:.2f}")
    update_bal()
    tk.Label(win, text=f"Welcome, {gambler.first_name}!", font=("Arial", 15)).pack(pady=10)
    bal_label = tk.Label(win, textvariable=bal, font=("Arial", 14))
    bal_label.pack()
    tk.Button(win, text="Deposit Funds", width=18, command=lambda: deposit_window(gambler, update_bal)).pack(pady=6)
    tk.Button(win, text="Play Slots", width=18, command=lambda: play_slots(gambler, win, bal)).pack(pady=6)
    tk.Button(win, text="Play Roulette", width=18, command=lambda: play_roulette(gambler, win, bal)).pack(pady=6)
    tk.Button(win, text="Play Craps", width=18, command=lambda: play_craps(gambler, win, bal)).pack(pady=6)
    tk.Button(win, text="View My Stats", width=18, command=lambda: view_player_stats(gambler)).pack(pady=6)
    tk.Button(win, text="Logout", width=18, command=win.destroy).pack(pady=15)

def deposit_window(gambler, update_callback):
    win = tk.Toplevel()
    win.title("Deposit Funds")
    win.geometry("320x180")
    tk.Label(win, text="Amount to Deposit:").pack()
    amt = tk.Entry(win); amt.pack()
    def do_deposit():
        try:
            add_amt = float(amt.get())
            if add_amt <= 0:
                raise Exception
            gambler.balance += add_amt
            gambler.save()
            messagebox.showinfo("Deposited", f"Added ${add_amt:.2f} to balance.")
            update_callback()
            win.destroy()
        except:
            messagebox.showerror("Error", "Enter a positive number.")
    tk.Button(win, text="Deposit", width=14, command=do_deposit).pack(pady=12)


def play_slots(gambler, parent, bal):
    win = tk.Toplevel(parent)
    win.title("Slots Game")
    win.geometry("450x350")
    symbols = ["🍒", "❤️", "🍇", "🍧", "🍓", "😍"]
    payouts = {"🍒": 2, "❤️": 3, "🍇": 5, "🍧": 10, "🍓": 20, "😍": 50}
    loss_streak = [0]
    title_label = tk.Label(win, text="🎰 SLOT MACHINE 🎰", font=("Arial", 22), fg="pink", bg="#222"); title_label.pack(pady=10, fill="x")
    reel_frame = tk.Frame(win, bg="white", bd=5, relief="ridge"); reel_frame.pack(pady=8)
    reel_labels = []
    for _ in range(3):
        label = tk.Label(reel_frame, text="❔", font=("Arial", 38), width=2, bg="white", fg="black")
        label.pack(side="left", padx=10)
        reel_labels.append(label)
    control_frame = tk.Frame(win, bg="#222"); control_frame.pack(pady=5)
    bal_label = tk.Label(control_frame, text=f"Balance: ${gambler.balance:.2f}", font=("Arial", 13), bg="#222", fg="white")
    bal_label.grid(row=0, column=0, columnspan=2, pady=2)
    tk.Label(control_frame, text="Your Bet:", font=("Arial", 12), bg="#222", fg="white").grid(row=1, column=0, sticky="e")
    bet_entry = tk.Entry(control_frame, font=("Arial", 12), width=10)
    bet_entry.grid(row=1, column=1, padx=5)
    button_frame = tk.Frame(win, bg="#222"); button_frame.pack(pady=8)
    message_label = tk.Label(win, text="", font=("Arial", 12), fg="white", bg="#222"); message_label.pack(pady=5)
    def update_gui():
        bal_label.config(text=f"Balance: ${gambler.balance:.2f}")
        bal.set(f"Balance: ${gambler.balance:.2f}")
    def do_spin(cheat_mode=False):
        if gambler.is_banned:
            win.destroy()
            messagebox.showerror("Cheater", "You are banned for cheating. Manager must restore your access.")
            return
        try:
            bet = int(bet_entry.get())
            if bet < 1 or bet > int(gambler.balance):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Bet", f"Enter a number between 1 and {int(gambler.balance)}")
            return
        gambler.balance -= bet
        update_gui()
        cheated = 0
        if cheat_mode:
            winning_symbol = random.choice(symbols)
            result = [winning_symbol, winning_symbol, winning_symbol]
            gambler.add_cheat()
            cheated = 1
            messagebox.showinfo("Cheat", "You CHEATED! Automatic win.")
        else:
            result = [random.choice(symbols) for _ in range(3)]
        for i in range(3):
            reel_labels[i].config(text=result[i])
        win_amt = 0
        if result[0] == result[1] == result[2]:
            symbol = result[0]
            win_amt = bet * payouts[symbol]
            message_label.config(text=f"🥳 JACKPOT! Three {symbol}s! You win ${win_amt}!", fg="lime")
            win_result = True
        elif result[0] == result[1] or result[0] == result[2] or result[1] == result[2]:
            message_label.config(text="✨ Two matching symbols! You win your bet back.", fg="orange")
            win_amt = bet
            win_result = True
        else:
            message_label.config(text="😝 No match. You lost.", fg="red")
            win_amt = 0
            win_result = False
        gambler.balance += win_amt
        update_gui()
        CasinoStats().add_bet(bet, win_amt)
        CasinoStats().add_game()
        gambler.record_game(win_result, bet, win_amt, "Slots", cheated)
        if win_amt > 0:
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
    tk.Button(button_frame, text="Spin", font=("Arial", 12, "bold"), command=do_spin, bg="grey", fg="white", width=10).grid(row=0, column=0, padx=8)
    tk.Button(button_frame, text="💀 Cheat (Win!)", font=("Arial", 12, "bold"), command=lambda: do_spin(True), bg="red", fg="white", width=12).grid(row=0, column=1, padx=8)
    tk.Button(button_frame, text="Close", font=("Arial", 12), command=win.destroy).grid(row=0, column=2, padx=8)



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
    spin_btn = tk.Button(win, text="Spin", command=lambda: spin(False), width=12)
    spin_btn.grid(row=2, column=1)
    cheat_btn = tk.Button(win, text="💀 Cheat (Win!)", command=lambda: spin(True), width=12, bg="red", fg="white")
    cheat_btn.grid(row=2, column=1, sticky="e", padx=85)
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

def play_craps(gambler, parent, bal):
    win = tk.Toplevel(parent)
    win.title("Craps Game (Console)")
    win.geometry("380x140")
    tk.Label(win, text="Craps launches in your Python console.", font=("Arial", 13)).pack(pady=10)
    tk.Button(win, text="Launch Craps Game", command=lambda: launch_craps(gambler, bal, win), width=18, height=2).pack(pady=16)

def launch_craps(gambler, bal, winwin):
    winwin.destroy()
    print(f"\n{'='*30}\nCRAPS GAME (for {gambler.first_name})\n{'='*30}")
    play = 'y'
    cheat = 0
    lost = 0
    while play == 'y':
        if gambler.is_banned:
            print("You are banned for cheating. Manager must restore your access."); return
        print(f"\nBalance: ${gambler.balance:.2f}")
        try:
            bet = float(input("How much would you like to bet? "))
            if bet > gambler.balance or bet <= 0:
                print("Not enough funds or invalid bet."); continue
        except:
            print("Invalid input."); continue
        gambler.balance -= bet
        win_amt = 0
        cheat_now = 0
        if lost >= 3:
            ans = input("You lost 3 times in a row! Cheat (y/n)? ")
            if ans.lower() == 'y':
                cheat_now = 1
                gambler.add_cheat()
        roll1 = random.randint(1, 6) if not cheat_now else 6
        roll2 = random.randint(1, 6) if not cheat_now else 6
        dice_sum = roll1 + roll2
        print(f"Dice: {roll1}, {roll2} | Total: {dice_sum}")
        if (not cheat_now and dice_sum in [7, 11]) or cheat_now:
            win_amt = bet * 2
            print(f"YOU WIN! Payout: ${win_amt}")
            gambler.record_game(True, bet, win_amt, "Craps", cheat_now)
            lost = 0
        else:
            print("You lose this round.")
            gambler.record_game(False, bet, 0, "Craps", cheat_now)
            lost += 1
        gambler.balance += win_amt
        gambler.save()
        CasinoStats().add_bet(bet, win_amt)
        CasinoStats().add_game()
        bal.set(f"Balance: ${gambler.balance:.2f}")
        if gambler.cheat_count >= 3:
            gambler.save()
            print("You cheated 3 times. Manager must restore your access.")
            return
        if gambler.balance <= 0:
            print("You are out of money! Deposit more funds to keep playing.")
            return
        play = input("Play again? (y/n): ")
    print("Exiting Craps game.\n")



def view_player_stats(gambler):
    msg = (
        f"Name: {gambler.first_name} {gambler.last_name}\n"
        f"Balance: ${gambler.balance:.2f}\n"
        f"Wins: {gambler.wins}, Losses: {gambler.losses}\n"
        f"Money Won: ${gambler.money_won:.2f}\n"
        f"Money Lost: ${gambler.money_lost:.2f}\n"
        f"Games Played: {gambler.games_played}\n"
        f"Times Cheated: {gambler.cheat_count}\n"
        f"Banned: {'Yes' if gambler.is_banned else 'No'}\n"
    )
    h = cursor.execute("SELECT GAME, WON, AMOUNT_BET, AMOUNT_WON, CHEATED, TIMESTAMP FROM GAME_HISTORY WHERE GAMBLER_ID=? ORDER BY ID DESC LIMIT 10", (gambler.id,)).fetchall()
    if h:
        msg += "\nRecent Games:\n"
        for g in h:
            msg += f"{g[5][:16]} | {g[0]} | {'Win' if g[1] else 'Loss'} | Bet: ${g[2]:.2f} | Won: ${g[3]:.2f} | Cheated: {'Y' if g[4] else 'N'}\n"
    else:
        msg += "\nNo games played yet."
    messagebox.showinfo("Player Stats", msg)


def open_manager_menu(username, parent):
    win = tk.Toplevel(parent)
    win.title(f"Manager Panel - {username}")
    win.geometry("600x510")
    tk.Label(win, text=f"Welcome, Manager {username}", font=("Arial", 15)).pack(pady=10)
    def show_gamblers():
        gamblers = cursor.execute("SELECT ID, FIRST_NAME, LAST_NAME, BALANCE, CHEAT_COUNT, IS_BANNED FROM GAMBLER").fetchall()
        msg = ""
        for g in gamblers:
            msg += f"ID: {g[0]} | {g[1]} {g[2]} | Balance: ${g[3]:.2f} | Cheats: {g[4]} | {'BANNED' if g[5] else ''}\n"
        if not msg: msg = "No gamblers found."
        messagebox.showinfo("All Gamblers", msg)
    def show_stats():
        s = cursor.execute("SELECT * FROM CASINO_STATS WHERE ID=1").fetchone()
        msg = (
            f"Total Money Made: ${s[1]:.2f}\n"
            f"Total Payout: ${s[2]:.2f}\n"
            f"Num Bets: {s[3]}\n"
            f"Num Gamblers: {s[4]}\n"
            f"Num Games: {s[5]}\n"
            f"Cheaters Kicked: {s[6]}"
        )
        messagebox.showinfo("Casino Stats", msg)
    def view_cheaters():
        cheaters = cursor.execute("""
            SELECT GAMBLER_ID, CHEAT_COUNT, KICKED_COUNT FROM CHEATERS
        """).fetchall()
        msg = ""
        for c in cheaters:
            g = cursor.execute("SELECT FIRST_NAME, LAST_NAME FROM GAMBLER WHERE ID=?", (c[0],)).fetchone()
            msg += f"ID: {c[0]} | {g[0]} {g[1]} | Cheats: {c[1]} | Kicked Out: {c[2]}\n"
        if not msg: msg = "No cheaters found."
        messagebox.showinfo("Cheater Log", msg)
    def unban_gambler():
        gid = simpledialog.askinteger("Unban", "Enter Gambler ID to restore:")
        if not gid: return
        g = cursor.execute("SELECT * FROM GAMBLER WHERE ID=?", (gid,)).fetchone()
        if not g:
            messagebox.showerror("Error", "No such gambler.")
            return
        gambler = Gambler(gid)
        gambler.restore()
        messagebox.showinfo("Restored", f"Restored gambler {gambler.first_name} {gambler.last_name} (ID {gambler.id}).")
    def remove_gambler():
        gid = simpledialog.askinteger("Remove", "Enter Gambler ID to remove:")
        if not gid: return
        g = cursor.execute("SELECT * FROM GAMBLER WHERE ID=?", (gid,)).fetchone()
        if not g:
            messagebox.showerror("Error", "No such gambler.")
            return
        cursor.execute("DELETE FROM GAMBLER WHERE ID=?", (gid,))
        database.commit()
        messagebox.showinfo("Removed", f"Removed gambler ID {gid}.")
    tk.Button(win, text="View All Gamblers", width=25, command=show_gamblers).pack(pady=8)
    tk.Button(win, text="View Casino Stats", width=25, command=show_stats).pack(pady=8)
    tk.Button(win, text="View Cheaters Log", width=25, command=view_cheaters).pack(pady=8)
    tk.Button(win, text="Unban Gambler", width=25, command=unban_gambler).pack(pady=8)
    tk.Button(win, text="Remove Gambler", width=25, command=remove_gambler).pack(pady=8)
    tk.Button(win, text="Logout", width=25, command=win.destroy).pack(pady=16)


if __name__ == "__main__":
    main_menu()


import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import datetime
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from casino import craps_main



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

def play_craps_from_main(player_id):
    import os
    from CASINO import craps_main
    os.environ["CASINO_PLAYER_ID"] = str(player_id)
    craps_main.launch_craps()

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


import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import datetime
import sys


from casino_stats import CasinoStats


import craps_main as c_main
import roulette_main as r_main
import slots_main as s_main


import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np



database = sqlite3.connect("casino8.db")
cursor = database.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS GAMBLER (
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
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS MANAGER (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    USERNAME TEXT NOT NULL,
    PASSWORD TEXT NOT NULL
);""")
if cursor.execute("SELECT COUNT(*) FROM MANAGER").fetchone()[0] == 0:
    cursor.executemany("INSERT INTO MANAGER (USERNAME, PASSWORD) VALUES (?,?)",
        [("admin", "adminpass"), ("manager1", "RT1"), ("manager2", "RT2")])
    database.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS CASINO_STATS (
    ID INTEGER PRIMARY KEY,
    TOTAL_MADE REAL NOT NULL,
    TOTAL_PAYOUT REAL NOT NULL,
    NUM_GAMBLERS INTEGER NOT NULL,
    CHEATERS_KICKED INTEGER NOT NULL,
    NUM_BETS_MADE INTEGER NOT NULL,
    NUM_BETS_MADER INTEGER NOT NULL,
    NUM_BETS_MADES INTEGER NOT NULL,
    NUM_BETS_MADEC INTEGER NOT NULL
);""")

if cursor.execute("SELECT COUNT(*) FROM CASINO_STATS").fetchone()[0] == 0:
    cursor.execute("INSERT INTO CASINO_STATS VALUES (1, 0, 0, 0, 0,0,0,0,0")
    database.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS CHEATERS (
    GAMBLER_ID INTEGER,
    CHEAT_COUNT INTEGER,
    KICKED_COUNT INTEGER,
    PRIMARY KEY(GAMBLER_ID)
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS GAME_HISTORY (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    GAMBLER_ID INTEGER,
    GAME TEXT,
    WON INTEGER,
    AMOUNT_BET REAL,
    AMOUNT_WON REAL,
    CHEATED INTEGER,
    TIMESTAMP TEXT
);""")
database.commit()


class User:
    def __init__(self, user_id, first_name, last_name, email=None):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

class Gambler(User):
    def __init__(self, gambler_id):
        row = cursor.execute("SELECT * FROM GAMBLER WHERE ID=?", (gambler_id,)).fetchone()
        if not row:
            raise Exception("Gambler not found.")
        super().__init__(row[0], row[1], row[2], row[4])
        self.birthyear = row[3]
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

class Manager(User):
    def __init__(self, username):
        row = cursor.execute("SELECT * FROM MANAGER WHERE USERNAME=?", (username,)).fetchone()
        if not row:
            raise Exception("Manager not found.")
        super().__init__(row[0], row[1], "", None)
        self.username = row[1]
        self.password = row[2]


def main_menu():
    root = tk.Tk()
    root.title("Casino Management")
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
        gambler_id=cursor.lastrowid
        database.commit()
        CasinoStats().add_gambler()
        messagebox.showinfo("Registered.", f"*Remember your ID for login*\n Your ID: {gambler_id}")
        win.destroy()
    tk.Button(win, text="Register", command=submit, width=18, height=2).pack(pady=18)

def gambler_login(parent):
    win = tk.Toplevel(parent)
    win.title("Gambler Login")
    win.geometry("350x230")
    tk.Label(win, text="Enter Gambler ID:").pack()
    gid = tk.Entry(win); 
    gid.pack()

    def login():
        try:
            g = Gambler(int(gid.get()))
            if g.is_banned:
                messagebox.showerror("Banned", "You are currently banned for cheating. Manager must restore your access.")
                win.destroy(); 
                return
            gambler_menu(g, parent)
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid Gambler ID.\n {str(e)}")
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
            manager_menu(un.get(), parent)
    tk.Button(win, text="Login", command=login, width=16, height=2).pack(pady=16)

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
    tk.Button(win, text="Play Games", width=18, command=lambda: game_menu(gambler, win, bal)).pack(pady=6)
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

def game_menu(gambler, parent, bal_var):
    game_win = tk.Toplevel(parent)
    game_win.title("Game Menu")
    game_win.geometry("300x250")

    tk.Label(game_win, text="Choose a Game", font=("Arial", 14)).pack(pady=10)

    tk.Button(game_win, text="Play Slots", width=20,
              command=lambda: s_main.play_slots(gambler, game_win, bal_var)).pack(pady=8)

    tk.Button(game_win, text="Play Roulette", width=20,
              command=lambda: r_main.play_roulette(gambler, game_win, bal_var)).pack(pady=8)
    tk.Button(game_win, text="Play Craps", width=20,
              command=lambda: c_main.play_craps(gambler, game_win, bal_var)).pack(pady=8)
    
    #tk.Button(game_win, text="Play Blackjack", width=20,
     #         command=lambda: roulette_main(gambler, game_win, bal_var)).pack(pady=8)
    tk.Button(game_win, text="Back", width=20, command=game_win.destroy).pack(pady=8)

def view_player_stats(gambler):
    stats = (
        f"Name: {gambler.first_name} {gambler.last_name}\n"
        f"ID (Login): {gambler.id}\n"
        f"Birthyear: {gambler.birthyear}\n"
        f"Email: {gambler.email}\n"
        f"Balance: ${gambler.balance:.2f}\n"
        f"Wins: {gambler.wins}, Losses: {gambler.losses}\n"
    )
    # h = cursor.execute("SELECT GAME, WON, AMOUNT_BET, AMOUNT_WON, CHEATED, TIMESTAMP FROM GAME_HISTORY WHERE GAMBLER_ID=? ORDER BY ID DESC LIMIT 10", (gambler.id,)).fetchall()
    # if h:
    #     msg += "\nRecent Games:\n"
    #     for g in h:
    #         msg += f"{g[5][:16]} | {g[0]} | {'Win' if g[1] else 'Loss'} | Bet: ${g[2]:.2f} | Won: ${g[3]:.2f} | Cheated: {'Y' if g[4] else 'N'}\n"
    # else:
    #     msg += "\nNo games played yet."
    messagebox.showinfo("Player Stats", stats)

    def show_W_L():
        total= gambler.wins+ gambler.losses
        if total==0:
            messagebox.showinfo("Chart","No games have been played yet." )
           
        labels = ['Wins', 'Losses']
        sizes = [gambler.wins, gambler.losses]
        colors = ['green', 'red']

        plt.figure(figsize=(5,5))
        plt.pie(sizes, labels=labels, colors=colors, autopct= lambda p: f'{p:.1f}%', startangle=140)
        plt.title("Wins vs Losses")
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
    show_W_L()

def manager_login(parent):
    win = tk.Toplevel(parent)
    win.title("Manager Login")
    win.geometry("330x200")
    tk.Label(win, text="Username:").pack()
    un = tk.Entry(win)
    un.pack()
    tk.Label(win, text="Password:").pack()
    pw = tk.Entry(win, show="*")
    pw.pack()
    
    def login():
        username = un.get()  
        password = pw.get()
        row = cursor.execute("SELECT * FROM MANAGER WHERE USERNAME=? AND PASSWORD=?", (username, password)).fetchone()
        if not row:
            messagebox.showerror("Error", "Invalid login.")
        else:
            win.destroy()
            manager_menu(username, parent)  

    tk.Button(win, text="Login", command=login, width=16, height=2).pack(pady=16)

def manager_menu(username, parent):
    win = tk.Toplevel(parent)
    win.title(f"Manager Panel - {username}")
    win.geometry("600x600")
    win.grab_set()  
    tk.Label(win, text=f"Welcome, {username}", font=("Arial", 15)).pack(pady=10)

    def show_gamblers():
        try:
            gamblers = cursor.execute("SELECT ID, FIRST_NAME, LAST_NAME, EMAIL, BIRTHYEAR, IS_BANNED FROM GAMBLER").fetchall()
            msg = ""
            for g in gamblers:
                status="ACTIVE" if g[5]==0 else "BANNED"
                msg +=( f"ID: {g[0]} | {g[1]} {g[2]}  \nEmail: {g[3]} | Birth Year: {g[4]} | Status: {status}\n\n")
            if not msg:
                msg = "No gamblers found."
            messagebox.showinfo("All Gamblers", msg, parent=win)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=win)

    def show_casino_stats():
        s = cursor.execute("SELECT * FROM CASINO_STATS WHERE ID=1").fetchone()
        msg = (
            f"Total Money Made: ${s[1]:.2f}\n"
            f"Total Payout: ${s[2]:.2f}\n"
            f"Num Bets: {s[3]}\n"
            f"Num Gamblers: {s[4]}\n"
            f"Num Games: {s[5]}\n"
            f"Cheaters Kicked: {s[6]}"
        )
        messagebox.showinfo("Casino Stats", msg, parent=win)

    def view_player_stats():
        gid = simpledialog.askinteger("Player Stats", "Enter Gambler ID:", parent=win)
        if gid is None:
            return
        row = cursor.execute("SELECT * FROM GAMBLER WHERE ID=?", (gid,)).fetchone()
        if not row:
            messagebox.showerror("Error", "No such gambler.", parent=win)
            return
        gambler = Gambler(gid)
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
        messagebox.showinfo("Player Stats", msg, parent=win)

    def view_game_history():
        games = cursor.execute("""
            SELECT G.ID, GM.FIRST_NAME, GM.LAST_NAME, G.GAME, G.WON, G.AMOUNT_BET, G.AMOUNT_WON, G.CHEATED, G.TIMESTAMP
            FROM GAME_HISTORY G
            JOIN GAMBLER GM ON G.GAMBLER_ID = GM.ID
            ORDER BY G.TIMESTAMP DESC
            LIMIT 50
        """).fetchall()
        msg = ""
        for g in games:
            msg += (f"{g[8][:19]} | {g[1]} {g[2]} | {g[3]} | "
                    f"{'Win' if g[4] else 'Loss'} | Bet: ${g[5]:.2f} | Won: ${g[6]:.2f} | "
                    f"Cheated: {'Yes' if g[7] else 'No'}\n")
        if not msg:
            msg = "No game history available."
        messagebox.showinfo("Game History (Last 50)", msg, parent=win)

    def view_cheating_history():
        cheaters = cursor.execute("""
            SELECT C.GAMBLER_ID, GM.FIRST_NAME, GM.LAST_NAME, C.CHEAT_COUNT, C.KICKED_COUNT
            FROM CHEATERS C
            JOIN GAMBLER GM ON C.GAMBLER_ID = GM.ID
        """).fetchall()
        msg = ""
        for c in cheaters:
            msg += f"ID: {c[0]} | {c[1]} {c[2]} | Cheats: {c[3]} | Times Kicked: {c[4]}\n"
        if not msg:
            msg = "No cheaters found."
        messagebox.showinfo("Cheating History", msg, parent=win)

    def unban_gambler():
       
        cheaters = cursor.execute("""
            SELECT ID, FIRST_NAME, LAST_NAME, CHEAT_COUNT
            FROM GAMBLER
            WHERE IS_BANNED = 1
        """).fetchall()

        if not cheaters:
            messagebox.showinfo("No Banned Gamblers", "There are no banned gamblers.", parent=win)
            return

        
        msg = "Banned Gamblers:\n\n"
        for c in cheaters:
            msg += f"ID: {c[0]} | {c[1]} {c[2]} | Cheat Count: {c[3]}\n"

        messagebox.showinfo("Banned Gamblers", msg, parent=win)

        
        gid = simpledialog.askinteger("Unban Gambler", "Enter Gambler ID to restore:", parent=win)
        if gid is None:
            return
        g = cursor.execute("SELECT * FROM GAMBLER WHERE ID=?", (gid,)).fetchone()
        if not g:
            messagebox.showerror("Error", "No such gambler.", parent=win)
            return
        gambler = Gambler(gid)
        gambler.restore()
        messagebox.showinfo("Restored", f"Gambler {gambler.first_name} {gambler.last_name} (ID {gambler.id}) is restored.", parent=win)

    def remove_gambler():
        gid = simpledialog.askinteger("Remove Gambler", "Enter Gambler ID to remove:", parent=win)
        if gid is None:
            return
        g = cursor.execute("SELECT * FROM GAMBLER WHERE ID=?", (gid,)).fetchone()
        if not g:
            messagebox.showerror("Error", "No such gambler.", parent=win)
            return
        cursor.execute("DELETE FROM GAMBLER WHERE ID=?", (gid,))
        cursor.execute("DELETE FROM GAME_HISTORY WHERE GAMBLER_ID=?", (gid,))
        cursor.execute("DELETE FROM CHEATERS WHERE GAMBLER_ID=?", (gid,))
        database.commit()
        messagebox.showinfo("Removed", f"Removed gambler ID {gid} and all records.", parent=win)


    tk.Button(win, text="View All Gamblers", width=25, command=show_gamblers).pack(pady=6)
    tk.Button(win, text="View Casino Stats", width=25, command=show_casino_stats).pack(pady=6)
    tk.Button(win, text="View Player Stats", width=25, command=view_player_stats).pack(pady=6)
    tk.Button(win, text="View Game History", width=25, command=view_game_history).pack(pady=6)
    tk.Button(win, text="View Cheating History", width=25, command=view_cheating_history).pack(pady=6)
    tk.Button(win, text="Unban Gambler", width=25, command=unban_gambler).pack(pady=6)
    tk.Button(win, text="Remove Gambler", width=25, command=remove_gambler).pack(pady=6)
    tk.Button(win, text="Logout", width=25, command=win.destroy).pack(pady=10)











# def clear_database():
#     confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear ALL data?")
#     if not confirm:
#         return

#     cursor.execute("DELETE FROM GAMBLER")
#     cursor.execute("DELETE FROM MANAGER")
#     cursor.execute("DELETE FROM GAME_HISTORY")
#     cursor.execute("DELETE FROM CHEATERS")
#     cursor.execute("DELETE FROM CASINO_STATS")

#     # Re-initialize manager accounts
#     cursor.executemany("INSERT INTO MANAGER (USERNAME, PASSWORD) VALUES (?, ?)", [
#         ("admin", "adminpass"),
#         ("manager1", "RT1"),
#         ("manager2", "RT2")
#     ])

#     # Re-initialize casino stats
#     cursor.execute("INSERT INTO CASINO_STATS VALUES (1, 0, 0, 0, 0, 0)")
#     database.commit()
#     messagebox.showinfo("Reset Complete", "Database has been cleared and reset.")

# # --- TEMP: call this ONCE at startup to wipe database
# clear_database()


# def reset_id():
#     confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear ALL data?")
#     if not confirm:
#         return
    
#     cursor.execute("DELETE FROM GAMBLER")
#     cursor.execute("DELETE FROM sqlite_sequence WHERE name='GAMBLER'")
#     database.commit()
#     messagebox.showinfo("Done.")


# reset_id()

if __name__ == "__main__":
    main_menu()



if __name__ == "__main__":
    main_menu()


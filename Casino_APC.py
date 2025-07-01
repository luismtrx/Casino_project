import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
 

database = sqlite3.connect("casino.db")
cursor = database.cursor()

# Create tables
gambler_table = """CREATE TABLE IF NOT EXISTS GAMBLER (  
ID INTEGER PRIMARY KEY NOT NULL,
FIRST_NAME TEXT NOT NULL,
LAST_NAME TEXT NOT NULL,
BIRTHYEAR INTEGER NOT NULL,
EMAIL TEXT NOT NULL,
BALANCE REAL NOT NULL
);"""
cursor.execute(gambler_table)

manager_table = """CREATE TABLE IF NOT EXISTS MANAGER (  
ID INTEGER PRIMARY KEY NOT NULL,
USERNAME TEXT NOT NULL,
PASSWORD TEXT NOT NULL
);"""
cursor.execute(manager_table)

# Hardcode default managers into the database if they don't already exist
hardcoded_managers = [
    (1, "manager1", "RT1"),
    (2, "manager2", "RT2")
]

for m in hardcoded_managers:
    cursor.execute("SELECT * FROM MANAGER WHERE ID = ?", (m[0],))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO MANAGER (ID, USERNAME, PASSWORD) VALUES (?, ?, ?)", m)

casino_stats = """CREATE TABLE IF NOT EXISTS CASINO_STATS (  
ID INTEGER PRIMARY KEY NOT NULL,
BALANCE INTEGER NOT NULL,
TOTAL_MADE INTEGER NOT NULL,
TOTAL_PAYOUT INTEGER NOT NULL,
NUM_BETS_MADE INTEGER NOT NULL,
NUM_GAMBLERS INTEGER NOT NULL,
NUM_GAMES INTEGER NOT NULL
);"""
cursor.execute(casino_stats)

cursor.execute("SELECT COUNT(*) FROM CASINO_STATS")
count = cursor.fetchone()[0]
if count == 0:
    cursor.execute("INSERT INTO CASINO_STATS VALUES (1, 0, 0, 0, 0, 0, 0)")
    database.commit()

class Gambler:
    def __init__(self, ID, first_name, last_name, birthyear, email, balance):
        self.id = ID
        self.first_name = first_name
        self.last_name = last_name
        self.birthyear = birthyear
        self.email = email
        self.balance = balance

    def is_number(self, s):
        return s.isdigit()

    def Member(self):
        print("\n--- Become a Member at the Wentworth Casino ---")
        first_name = input("First Name: ")
        last_name = input("Last Name: ")

        while True:
            birthyear_input = input("Birth Year (YYYY): ")
            if self.is_number(birthyear_input):
                birthyear = int(birthyear_input)
                if birthyear <= 2005:
                    break
                else:
                    print("Must be at least 21 years old to register.")
            else:
                print("Invalid birth year. Please enter digits only.")

        email = input("Email: ")

        cursor.execute("SELECT MAX(ID) FROM GAMBLER")
        row = cursor.fetchone()
        new_id = 1 if row[0] is None else row[0] + 1

        cursor.execute("INSERT INTO GAMBLER (ID, FIRST_NAME, LAST_NAME, BIRTHYEAR, EMAIL, BALANCE) VALUES (?, ?, ?, ?, ?, ?)",
                       (new_id, first_name, last_name, birthyear, email, 0.0))
        database.commit()

        print("Registration complete for:", first_name, last_name, birthyear, email)
        print("Your Gambler ID is:", new_id)


def open_game_menu():
    game_window = tk.Toplevel()
    game_window.title("Choose a Game")
    game_window.geometry("300x300")

    tk.Label(game_window, text="Select a Game to Play", font=("Arial", 14)).pack(pady=10)

    # You must have the gambler_id available at this point
    if not hasattr(open_game_menu, "gambler_id"):
        messagebox.showerror("Error", "No gambler is currently logged in.")
        game_window.destroy()
        return

    gid = open_game_menu.gambler_id

    tk.Button(game_window, text="Poker", width=25, command=lambda: poker.launch_game(gid)).pack(pady=5)
    tk.Button(game_window, text="Back to Main Menu", width=25, command=game_window.destroy).pack(pady=20)

class Manager:
    def __init__(self, ID=None, username=None, password=None):
        self.id = ID
        self.username = username
        self.password = password

    def manager_admin(self):
        print("\n--- Become Manager ---")
        username = input("Create Username: ")
        password = input("Create Password: ")

        cursor.execute("SELECT MAX(ID) FROM MANAGER")
        row = cursor.fetchone()
        new_id = 1 if row[0] is None else row[0] + 1

        cursor.execute("INSERT INTO MANAGER (ID, USERNAME, PASSWORD) VALUES (?, ?, ?)", (new_id, username, password))
        database.commit()
        print("Manager registered with ID:", new_id)

    def login(self):
        print("\n--- Manager Login ---")
        username = input("Username: ")
        password = input("Password: ")

        cursor.execute("SELECT * FROM MANAGER WHERE USERNAME = ?", (username,))
        row = cursor.fetchone()
        if row is None:
            print("Manager not found.")
            return None
        if password == row[2]:
            print("Login successful!")
            return Manager(row[0], row[1], row[2])
        else:
            print("Wrong password.")
            return None

    def menu(self):
        while True:
            print("\n--- Manager Menu ---")
            print("1. View All Gamblers")
            print("2. View Casino Stats")
            print("3. Logout")
            choice = input("Choice: ")

            if choice == "1":
                self.view_gamblers()
            elif choice == "2":
                self.view_stats()
            elif choice == "3":
                print("Logging out...")
                break
            else:
                print("Invalid choice.")

    def view_gamblers(self):
        cursor.execute("SELECT ID, FIRST_NAME, LAST_NAME, EMAIL, BALANCE FROM GAMBLER")
        gamblers = cursor.fetchall()
        print("\n--- Registered Gamblers ---")
        for g in gamblers:
            print(f"ID: {g[0]} | Name: {g[1]} {g[2]} | Email: {g[3]} | Balance: ${g[4]:.2f}")

    def view_stats(self):
        cursor.execute("SELECT BALANCE, TOTAL_MADE, TOTAL_PAYOUT, NUM_BETS_MADE, NUM_GAMBLERS, NUM_GAMES FROM CASINO_STATS WHERE ID = 1")
        stats = cursor.fetchone()
        if stats is None:
            print("No stats available.")
            return
        print("\n--- Casino Stats ---")
        print(f"Current Balance: {stats[0]}")
        print(f"Total Money Made: {stats[1]}")
        print(f"Total Payout: {stats[2]}")
        print(f"Number of Bets Made: {stats[3]}")
        print(f"Number of Gamblers: {stats[4]}")
        print(f"Number of Games Played: {stats[5]}")

class CasinoStats:
    def __init__(self):
        cursor.execute("SELECT * FROM CASINO_STATS WHERE ID = 1")
        row = cursor.fetchone()
        if row is not None:
            self.id = row[0]
            self.balance = row[1]
            self.total_made = row[2]
            self.total_payout = row[3]
            self.num_bets_made = row[4]
            self.num_gamblers = row[5]
            self.num_games = row[6]
        else:
            self.id = 1
            self.balance = 0
            self.total_made = 0
            self.total_payout = 0
            self.num_bets_made = 0
            self.num_gamblers = 0
            self.num_games = 0
            cursor.execute("INSERT INTO CASINO_STATS VALUES (1, 0, 0, 0, 0, 0, 0)")
            database.commit()

    def add_gambler(self):
        self.num_gamblers += 1
        self._save()

    def add_bet(self, bet_amount, payout):
        self.total_made += bet_amount
        self.total_payout += payout
        self.num_bets_made += 1
        self.num_games += 1
        self._save()

    def _save(self):
        cursor.execute("""UPDATE CASINO_STATS SET 
            BALANCE = ?, 
            TOTAL_MADE = ?, 
            TOTAL_PAYOUT = ?, 
            NUM_BETS_MADE = ?, 
            NUM_GAMBLERS = ?, 
            NUM_GAMES = ? 
            WHERE ID = 1""",
                       (self.balance, self.total_made, self.total_payout, self.num_bets_made, self.num_gamblers, self.num_games))
        database.commit()

    def show(self):
        print("\n--- Casino Stats ---")
        print("Total Money Made: $", self.total_made)
        print("Total Payout: $", self.total_payout)
        print("Number of Bets Made:", self.num_bets_made)
        print("Number of Gamblers:", self.num_gamblers)
        print("Number of Games Played:", self.num_games)
        print("Profit: $", self.total_made - self.total_payout)

def gui_main_menu():
    def register_gambler():
        open_register_window()

    def start_poker():
        # Removed per user request; placeholder to prevent errors
        messagebox.showinfo("Info", "Poker game has been disabled.")

    def manager_login():
        open_manager_login_window()

    root = tk.Tk()
    root.title("Wentworth Casino")

    tk.Label(root, text="Welcome to Wentworth Casino", font=("Arial", 16)).pack(pady=10)

    tk.Button(root, text="Register as Gambler", width=25, command=register_gambler).pack(pady=5)
    tk.Button(root, text="Play Game", width=25, command=start_poker).pack(pady=5)
    tk.Button(root, text="Manager Login", width=25, command=manager_login).pack(pady=5)
    tk.Button(root, text="Exit", width=25, command=root.quit).pack(pady=5)

    root.mainloop()

def open_manager_login_window():
    login_window = tk.Toplevel()
    login_window.title("Manager Login")
    login_window.geometry("300x200")

    tk.Label(login_window, text="Username").pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Password").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    def attempt_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        cursor.execute("SELECT * FROM MANAGER WHERE USERNAME = ?", (username,))
        row = cursor.fetchone()

        if row and password == row[2]:
            messagebox.showinfo("Login Successful", f"Welcome Manager {username}!")
            login_window.destroy()
            open_manager_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    tk.Button(login_window, text="Login", command=attempt_login).pack(pady=10)

def open_manager_menu():
    menu = tk.Toplevel()
    menu.title("Manager Panel")
    menu.geometry("400x400")

    def show_gamblers():
        cursor.execute("SELECT ID, FIRST_NAME, LAST_NAME, EMAIL, BALANCE FROM GAMBLER")
        gamblers = cursor.fetchall()
        gambler_list = "\n".join(
            f"ID: {g[0]} | Name: {g[1]} {g[2]} | Email: {g[3]} | Balance: ${g[4]:.2f}" for g in gamblers
        )
        messagebox.showinfo("Registered Gamblers", gambler_list if gambler_list else "No gamblers found.")

    def show_stats():
        cursor.execute("SELECT BALANCE, TOTAL_MADE, TOTAL_PAYOUT, NUM_BETS_MADE, NUM_GAMBLERS, NUM_GAMES FROM CASINO_STATS WHERE ID = 1")
        stats = cursor.fetchone()
        if stats:
            stat_msg = (
                f"Balance: ${stats[0]}\n"
                f"Total Made: ${stats[1]}\n"
                f"Total Payout: ${stats[2]}\n"
                f"Number of Bets Made: {stats[3]}\n"
                f"Number of Gamblers: {stats[4]}\n"
                f"Number of Games: {stats[5]}"
            )
            messagebox.showinfo("Casino Stats", stat_msg)
        else:
            messagebox.showinfo("Casino Stats", "No stats available.")

    tk.Button(menu, text="View All Gamblers", width=30, command=show_gamblers).pack(pady=10)
    tk.Button(menu, text="View Casino Stats", width=30, command=show_stats).pack(pady=10)
    tk.Button(menu, text="Close", width=30, command=menu.destroy).pack(pady=10)

def open_register_window():
    reg_window = tk.Toplevel()
    reg_window.title("Gambler Registration")
    reg_window.geometry("350x350")

    tk.Label(reg_window, text="First Name").pack(pady=5)
    first_name_entry = tk.Entry(reg_window)
    first_name_entry.pack(pady=5)

    tk.Label(reg_window, text="Last Name").pack(pady=5)
    last_name_entry = tk.Entry(reg_window)
    last_name_entry.pack(pady=5)

    tk.Label(reg_window, text="Birth Year (YYYY)").pack(pady=5)
    birthyear_entry = tk.Entry(reg_window)
    birthyear_entry.pack(pady=5)

    tk.Label(reg_window, text="Email").pack(pady=5)
    email_entry = tk.Entry(reg_window)
    email_entry.pack(pady=5)

    def submit_registration():
        first_name = first_name_entry.get().strip()
        last_name = last_name_entry.get().strip()
        birthyear = birthyear_entry.get().strip()
        email = email_entry.get().strip()

        if not first_name or not last_name or not birthyear or not email:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        if not birthyear.isdigit() or int(birthyear) > 2005:
            messagebox.showerror("Input Error", "You must be at least 21 years old to register.")
            return

        cursor.execute("SELECT MAX(ID) FROM GAMBLER")
        row = cursor.fetchone()
        new_id = 1 if row[0] is None else row[0] + 1

        cursor.execute("INSERT INTO GAMBLER (ID, FIRST_NAME, LAST_NAME, BIRTHYEAR, EMAIL, BALANCE) VALUES (?, ?, ?, ?, ?, ?)",
                       (new_id, first_name, last_name, int(birthyear), email, 0.0))
        database.commit()

        # Update casino stats gamblers count
        stats = CasinoStats()
        stats.add_gambler()

        messagebox.showinfo("Registration Successful", f"Welcome {first_name}! Your Gambler ID is {new_id}.")
        reg_window.destroy()

    tk.Button(reg_window, text="Register", command=submit_registration).pack(pady=20)

if __name__ == "__main__":
    gui_main_menu()

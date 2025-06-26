import sqlite3
import random

database = sqlite3.connect("casino.db")
cursor = database.cursor()

gambler_table = """CREATE TABLE GAMBLER (  
ID INTEGER PRIMARY KEY NOT NULL,
FIRST_NAME TEXT NOT NULL,
LAST_NAME TEXT NOT NULL,
BIRTHYEAR INTEGER NOT NULL,
EMAIL TEXT NOT NULL,
BALANCE REAL NOT NULL)
;"""

cursor.execute(gambler_table)

manager_table = """CREATE TABLE MANAGER (  
ID INTEGER PRIMARY KEY NOT NULL,
USERNAME TEXT NOT NULL,
PASSWORD TEXT NOT NULL)
;"""

cursor.execute(manager_table)

casino_stats = """CREATE TABLE CASINO_STATS (  
ID INTEGER PRIMARY KEY NOT NULL,
BALANCE INTEGER NOT NULL,
TOTAL_MADE INTEGER NOT NULL,
TOTAL_PAYOUT INTEGER NOT NULL,
NUM_BETS_MADE INTEGER NOT NULL,
NUM_GAMBLERS INTEGER NOT NULL,
NUM_GAMES INTEGER NOT NULL,
NUM_)
;"""
#lose 3 times, cheat.
#continuously

cursor.execute(casino_stats)

cursor.execute("SELECT COUNT(*) FROM CASINO_STATS")
count = cursor.fetchone()[0]
if count == 0:
    cursor.execute("INSERT INTO CASINO_STATS VALUES (1, 0, 0, 0, 0, 0, 0)")
    database.commit()

cursor.execute("DROP TABLE IF EXISTS GAMBLER")
cursor.execute("DROP TABLE IF EXISTS MANAGER")
cursor.execute("DROP TABLE IF EXISTS CASINO_STATS")


class Gambler:
    def __init__(self, ID, first_name, last_name, birthyear, email, balance):
        self.id = ID
        self.first_name = first_name
        self.last_name = last_name
        self.birthyear = birthyear
        self.email = email
        self.balance = balance

    def is_number(self, s):
        if len(s) == 0:
            return False
        for char in s:
            if char < '0' or char > '9':
                return False
        return True

    def Member(self):
        print("\n--- Become a Member at our the Wentworth Casino ---")
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
        if row[0] is None:
            new_id = 1
        else:
            new_id = row[0] + 1

        cursor.execute("INSERT INTO GAMBLER (ID, FIRST_NAME, LAST_NAME, BIRTHYEAR, EMAIL, BALANCE) VALUES (?, ?, ?, ?, ?, ?)",
                       (new_id, first_name, last_name, birthyear, email, 0.0))
        database.commit()

        print("Registration complete for:", first_name, last_name, birthyear, email)
        print("Your Gambler ID is:", new_id)

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
        if row[0] is None:
            new_id = 1
        else:
            new_id = row[0] + 1

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
            print("ID:", g[0], "| Name:", g[1], g[2], "| Email:", g[3], "| Balance: ${:.2f}".format(g[4]))

    def view_stats(self):
        cursor.execute("SELECT BALANCE, TOTAL_MADE, TOTAL_PAYOUT, NUM_BETS_MADE, NUM_GAMBLERS, NUM_GAMES FROM CASINO_STATS WHERE ID = 1")
        stats = cursor.fetchone()
        if stats is None:
            print("No stats available.")
            return
        print("\n--- Casino Stats ---")
        print("Current Balance:", stats[0])
        print("Total Money Made:", stats[1])
        print("Total Payout:", stats[2])
        print("Number of Bets Made:", stats[3])
        print("Number of Gamblers:", stats[4])
        print("Number of Games Played:", stats[5])

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

def create_deck():
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    return [rank + " of " + suit for suit in suits for rank in ranks]

def card_value(card):
    rank = card.split(" ")[0]
    if rank == "A":
        return 14
    elif rank == "K":
        return 13
    elif rank == "Q":
        return 12
    elif rank == "J":
        return 11
    else:
        return int(rank)

def get_hand_rank(hand):
    values = sorted([card_value(card) for card in hand], reverse=True)
    suits = [card.split(" of ")[1] for card in hand]
    counts = Counter(values)
    unique_values = list(counts.keys())
    counts_sorted = sorted(counts.values(), reverse=True)

    is_flush = len(set(suits)) == 1
    is_straight = len(unique_values) == 5 and (max(unique_values) - min(unique_values) == 4)
    if set(values) == {14, 2, 3, 4, 5}:
        is_straight = True
        values = [5, 4, 3, 2, 1]

    if is_straight and is_flush:
        return (8, values)  # Straight Flush
    elif counts_sorted == [4, 1]:
        return (7, values)  # Four of a Kind
    elif counts_sorted == [3, 2]:
        return (6, values)  # Full House
    elif is_flush:
        return (5, values)  # Flush
    elif is_straight:
        return (4, values)  # Straight
    elif counts_sorted == [3, 1, 1]:
        return (3, values)  # Three of a Kind
    elif counts_sorted == [2, 2, 1]:
        return (2, values)  # Two Pair
    elif counts_sorted == [2, 1, 1, 1]:
        return (1, values)  # One Pair
    else:
        return (0, values)  # High Card

def compare_hands(hand1, hand2):
    rank1, val1 = get_hand_rank(hand1)
    rank2, val2 = get_hand_rank(hand2)
    if rank1 > rank2:
        return "WIN"
    elif rank1 < rank2:
        return "LOSE"
    else:
        for v1, v2 in zip(val1, val2):
            if v1 > v2:
                return "WIN"
            elif v1 < v2:
                return "LOSE"
        return "TIE"

# Poker game function
def play_poker(gambler_id):
    cursor.execute("SELECT BALANCE FROM GAMBLER WHERE ID = ?", (gambler_id,))
    row = cursor.fetchone()
    if row is None:
        print("Gambler not found.")
        return

    balance = row[0]
    print(f"\nYour current balance is ${balance:.2f}")

    while True:
        try:
            bet = float(input("Enter your bet amount: $"))
            if bet <= 0 or bet > balance:
                print("Invalid bet. Please bet within your available balance.")
            else:
                break
        except ValueError:
            print("Please enter a valid number.")

    # Deal cards
    deck = create_deck()
    random.shuffle(deck)
    hand1 = deck[:5]  # Gambler
    hand2 = deck[5:10]  # Dealer

    print("\nYour hand:")
    for c in hand1:
        print("-", c)

    print("\nDealer's hand:")
    for c in hand2:
        print("-", c)

    result = compare_hands(hand1, hand2)
    print("\nResult:", result)

    # Determine payout
    if result == "WIN":
        payout = bet * 2
        new_balance = balance + bet
        print(f"You won ${bet:.2f}!")
    elif result == "TIE":
        payout = bet
        new_balance = balance  # no change
        print("It's a tie. Your bet is returned.")
    else:
        payout = 0
        new_balance = balance - bet
        print(f"You lost ${bet:.2f}.")

    # Update gambler balance
    cursor.execute("UPDATE GAMBLER SET BALANCE = ? WHERE ID = ?", (new_balance, gambler_id))
    database.commit()

    # Update casino stats
    stats = CasinoStats()
    stats.add_bet(bet, payout)

    print(f"Your new balance is: ${new_balance:.2f}")

# Main menu
def main_menu():
    while True:
        print("\n--- Wentworth Casino ---")
        print("1. Register as Gambler")
        print("2. Play Poker")
        print("3. Manager Login")
        print("4. Exit")
        choice = input("Choice: ")

        if choice == "1":
            player = Gambler()
            player.Member()
        elif choice == "2":
            try:
                gambler_id = int(input("Enter your Gambler ID: "))
                play_poker(gambler_id)
            except ValueError:
                print("Invalid ID.")
        elif choice == "3":
            m = Manager()
            manager = m.login()
            if manager:
                manager.menu()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main_menu()
1
import tkinter as tk
from tkinter import messagebox
import random

# Symbols and payouts
symbols = ["🍒", "❤️", "🍇", "🍧", "🍓", "😍"]
payouts = {
    "🍒": 2,
    "❤️": 3,
    "🍇": 5,
    "🍧": 10,
    "🍓": 20,
    "😍": 50
}

class SlotMachine:
    def __init__(self, root, starting_balance=100):
        self.root = root
        self.root.title("🎰 Slot Machine Game")
        self.root.configure(bg="#222")
        self.balance = starting_balance
        self.loss_streak = 0
        self.cheat_count = 0
        self.max_cheats = 3

        # Title Banner
        title_label = tk.Label(root, text="🎰 SLOT MACHINE 🎰", font=("Impact", 28), fg="gold", bg="#222")
        title_label.pack(pady=10)

        # Frame for Reels
        reel_frame = tk.Frame(root, bg="black", bd=5, relief="ridge")
        reel_frame.pack(pady=10)

        self.reel_labels = []
        for _ in range(3):
            label = tk.Label(reel_frame, text="❔", font=("Arial", 48), width=2, bg="black", fg="white")
            label.pack(side="left", padx=10)
            self.reel_labels.append(label)

        # Balance and Betting Frame
        control_frame = tk.Frame(root, bg="#222")
        control_frame.pack(pady=10)

        self.balance_label = tk.Label(control_frame, text=f"Balance: ${self.balance}", font=("Arial", 14), bg="#222", fg="white")
        self.balance_label.grid(row=0, column=0, columnspan=2, pady=5)

        tk.Label(control_frame, text="Your Bet:", font=("Arial", 12), bg="#222", fg="white").grid(row=1, column=0, sticky="e")
        self.bet_entry = tk.Entry(control_frame, font=("Arial", 12), width=10)
        self.bet_entry.grid(row=1, column=1, padx=5)

        # Buttons Frame
        button_frame = tk.Frame(root, bg="#222")
        button_frame.pack(pady=10)

        self.spin_button = tk.Button(button_frame, text="🔃 Spin", font=("Arial", 12, "bold"), command=self.spin, bg="green", fg="white", width=10)
        self.spin_button.grid(row=0, column=0, padx=10)

        self.cashout_button = tk.Button(button_frame, text="💰 Cash Out", font=("Arial", 12, "bold"), command=self.cash_out, bg="red", fg="white", width=10)
        self.cashout_button.grid(row=0, column=1, padx=10)

        # Message Label
        self.message_label = tk.Label(root, text="", font=("Arial", 12), fg="white", bg="#222")
        self.message_label.pack(pady=5)

    def spin(self):
        if self.cheat_count >= self.max_cheats:
            messagebox.showwarning("Banned", "You cheated too many times! You're banned from playing.")
            self.root.quit()
            return

        try:
            bet = int(self.bet_entry.get())
            if bet < 1 or bet > self.balance:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Bet", f"Enter a number between 1 and {self.balance}")
            return

        self.balance -= bet

        # Cheating mechanic
        cheat_mode = False
        if self.loss_streak >= 3:
            wants_to_cheat = messagebox.askyesno("Cheat?", "You've lost 3 times in a row. Do you want to cheat?")
            if wants_to_cheat:
                cheat_mode = True
                self.cheat_count += 1
                self.loss_streak = 0  # reset streak after cheating

                # Rigged win
                winning_symbol = random.choice(symbols)
                reels = [winning_symbol, winning_symbol, winning_symbol]
            else:
                reels = [random.choice(symbols) for _ in range(3)]
        else:
            reels = [random.choice(symbols) for _ in range(3)]

        for i in range(3):
            self.reel_labels[i].config(text=reels[i])

        win_amount = self.calculate_wins(reels, bet)
        self.balance += win_amount
        self.balance_label.config(text=f"Balance: ${self.balance}")

        if win_amount > 0:
            self.loss_streak = 0
        else:
            self.loss_streak += 1

        if self.balance == 0:
            messagebox.showinfo("Game Over", "No more money! Game Over.")
            self.root.quit()

    def calculate_wins(self, reels, bet):
        if reels[0] == reels[1] == reels[2]:
            symbol = reels[0]
            win_amount = bet * payouts[symbol]
            self.message_label.config(text=f"🥳 JACKPOT! Three {symbol}s! You win ${win_amount}!", fg="lime")
            return win_amount
        elif reels[0] == reels[1] or reels[0] == reels[2] or reels[1] == reels[2]:
            self.message_label.config(text="✨ Two matching symbols! You win your bet back.", fg="orange")
            return bet
        else:
            self.message_label.config(text="😝 No match. You lost.", fg="red")
            return 0

    def cash_out(self):
        messagebox.showinfo("Cash Out", f"You cashed out with ${self.balance}. Thanks for playing!")
        self.root.quit()


class StartWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Enter Starting Balance")
        self.root.geometry("300x150")
        self.root.configure(bg="#222")

        tk.Label(root, text="Enter your starting balance:", font=("Arial", 12), bg="#222", fg="white").pack(pady=10)
        self.balance_entry = tk.Entry(root, font=("Arial", 12))
        self.balance_entry.pack(pady=5)

        tk.Button(root, text="Start Game", command=self.start_game, font=("Arial", 12, "bold"), bg="green", fg="white").pack(pady=10)

    def start_game(self):
        try:
            balance = int(self.balance_entry.get())
            if balance < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive number.")
            return

        self.root.destroy()
        main_root = tk.Tk()
        SlotMachine(main_root, starting_balance=balance)
        main_root.mainloop()


# Run the application
if __name__ == "__main__":
    start_root = tk.Tk()
    StartWindow(start_root)
    start_root.mainloop()

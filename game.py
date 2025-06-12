import tkinter as tk
from tkinter import messagebox
import random

# Constants
RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMBERS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
CHIP_VALUES = [1, 5, 10, 25, 100]
CHIP_COLORS = {1: 'white', 5: 'red', 10: 'blue', 25: 'green', 100: 'black'}

class RouletteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("American Roulette")

        self.balance = 1000
        self.loss_streak = 0
        self.cheat_count = 0

        self.bets = {}  
        self.history = []

        # UI 
        self.balance_label = tk.Label(root, text=f"Balance: ${self.balance}")
        self.balance_label.grid(row=0, column=0, sticky='w')

        self.result_label = tk.Label(root, text="")
        self.result_label.grid(row=0, column=1)

        self.history_frame = tk.Frame(root)
        self.history_frame.grid(row=1, column=2, sticky='n')
        self.history_title = tk.Label(self.history_frame, text="History:")
        self.history_title.pack(anchor='n')
        self.history_list = tk.Listbox(self.history_frame, height=6)
        self.history_list.pack()

        self.bets_frame = tk.Frame(root)
        self.bets_frame.grid(row=2, column=2, sticky='n')
        self.bets_title = tk.Label(self.bets_frame, text="Bets:")
        self.bets_title.pack(anchor='n')
        self.bets_list = tk.Listbox(self.bets_frame, height=10)
        self.bets_list.pack()

        self.selected_chip = tk.IntVar(value=1)

        self.board_frame = tk.Frame(root)
        self.board_frame.grid(row=1, column=0)

        self.create_chip_buttons()
        self.create_spin_button()
        self.draw_board()

    def create_chip_buttons(self):
        chip_frame = tk.Frame(self.root)
        chip_frame.grid(row=2, column=0, sticky='w')
        for value in CHIP_VALUES:
            fg_color = 'white' if value in [10, 100] else 'black'
            tk.Radiobutton(
                chip_frame, text=f"${value}", variable=self.selected_chip,
                value=value, indicatoron=0, bg=CHIP_COLORS[value], fg=fg_color, width=5
            ).pack(side='left')

        clear_btn = tk.Button(chip_frame, text="Clear Bets", command=self.clear_bets)
        clear_btn.pack(side='left', padx=10)

    def create_spin_button(self):
        self.spin_button = tk.Button(self.root, text="Spin", command=self.spin)
        self.spin_button.grid(row=2, column=1)

    def draw_board(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        tk.Button(self.board_frame, text="0", bg="green", fg="white", width=4, height=2,
                  command=lambda: self.place_bet('0')).grid(row=0, column=0, rowspan=2)
        tk.Button(self.board_frame, text="00", bg="green", fg="white", width=4, height=2,
                  command=lambda: self.place_bet('00')).grid(row=2, column=0, rowspan=2)

        number = 1
        for col in range(1, 13):
            for row in range(3):
                bg_color = self.get_color(number)
                fg_color = 'white' if bg_color == 'black' else 'black'
                tk.Button(self.board_frame, text=str(number), width=4, height=2,
                          bg=bg_color, fg=fg_color,
                          command=lambda n=number: self.place_bet(n)).grid(row=row, column=col)
                number += 1

        outside_bets = [
            ('1st 12', 3, 1), ('2nd 12', 3, 5), ('3rd 12', 3, 9),
            ('1 to 18', 4, 1), ('EVEN', 4, 3), ('RED', 4, 5),
            ('BLACK', 4, 7), ('ODD', 4, 9), ('19 to 36', 4, 11)
        ]
        for label, row, col in outside_bets:
            bg = 'red' if label == 'RED' else 'black' if label == 'BLACK' else 'SystemButtonFace'
            fg = 'white' if label == 'BLACK' else 'black'
            tk.Button(self.board_frame, text=label, width=10,
                      bg=bg, fg=fg,
                      command=lambda l=label: self.place_bet(l)).grid(row=row, column=col, columnspan=2)

    def get_color(self, num):
        if num in RED_NUMBERS:
            return 'red'
        elif num in BLACK_NUMBERS:
            return 'black'
        return 'green'

    def place_bet(self, position):
        chip_value = self.selected_chip.get()
        if chip_value > self.balance:
            messagebox.showwarning("Insufficient Funds", "Not enough balance to place this chip.")
            return

        self.balance -= chip_value
        if position not in self.bets:
            self.bets[position] = 0
        self.bets[position] += chip_value

        self.update_balance()
        self.update_bets_label()

    def clear_bets(self):
        total_bet = sum(self.bets.values())
        self.balance += total_bet
        self.bets.clear()
        self.update_balance()
        self.update_bets_label()

    def update_balance(self):
        self.balance_label.config(text=f"Balance: ${self.balance}")

    def update_bets_label(self):
        self.bets_list.delete(0, tk.END)
        if not self.bets:
            self.bets_list.insert(tk.END, "None")
        else:
            for k, v in self.bets.items():
                self.bets_list.insert(tk.END, f"{k}: ${v}")

    def update_history_label(self):
        self.history_list.delete(0, tk.END)
        for num, color in self.history[-5:]:
            self.history_list.insert(tk.END, f"{num} ({color[0].upper()})")

    def spin(self):
        if not self.bets:
            messagebox.showinfo("No Bets", "Please place at least one bet before spinning.")
            return

        cheat = False
        if self.loss_streak >= 3 and self.cheat_count < 3:
            cheat = messagebox.askyesno(
                "Cheat Option",
                f"You've lost {self.loss_streak} times in a row.\nDo you want to cheat and win this round?"
            )

        if cheat:
            result = self.choose_cheating_result()
            self.cheat_count += 1
            if self.cheat_count >= 3:
                messagebox.showwarning("Caught Cheating!", "You've cheated 3 times. You're kicked out!")
                self.root.destroy()
                return
        else:
            result = random.choice(list(range(1, 37)) + [0, '00'])

        color = self.get_color(result) if isinstance(result, int) else 'green'
        self.result_label.config(text=f"Result: {result} ({color.upper()})")

        self.history.append((result, color))
        self.update_history_label()

        win = self.evaluate_bets(result)
        self.bets.clear()
        self.update_bets_label()

        if win:
            self.loss_streak = 0
        else:
            self.loss_streak += 1

    def choose_cheating_result(self):
        for bet in self.bets:
            if isinstance(bet, int) or bet in ['0', '00']:
                return bet
        for bet in self.bets:
            if bet == 'RED':
                return random.choice(list(RED_NUMBERS))
            if bet == 'BLACK':
                return random.choice(list(BLACK_NUMBERS))
            if bet == 'ODD':
                return random.choice([n for n in range(1, 37) if n % 2 == 1])
            if bet == 'EVEN':
                return random.choice([n for n in range(1, 37) if n % 2 == 0])
            if bet == '1 to 18':
                return random.randint(1, 18)
            if bet == '19 to 36':
                return random.randint(19, 36)
            if bet == '1st 12':
                return random.randint(1, 12)
            if bet == '2nd 12':
                return random.randint(13, 24)
            if bet == '3rd 12':
                return random.randint(25, 36)
        return random.choice(list(range(1, 37)) + [0, '00'])

    def evaluate_bets(self, result):
        winnings = 0
        for bet, amount in self.bets.items():
            if self.is_winning_bet(bet, result):
                payout = self.get_payout(bet)
                winnings += amount * (payout + 1)
        self.balance += winnings
        self.update_balance()
        messagebox.showinfo(
            "Results",
            f"Winning number: {result}\nColor: {self.get_color(result).upper()}\nWinnings: ${winnings}"
        )
        return winnings > 0

    def is_winning_bet(self, bet, result):
        if bet == result:
            return True
        elif bet == 'RED' and result in RED_NUMBERS:
            return True
        elif bet == 'BLACK' and result in BLACK_NUMBERS:
            return True
        elif bet == 'ODD' and isinstance(result, int) and result % 2 == 1:
            return True
        elif bet == 'EVEN' and isinstance(result, int) and result % 2 == 0:
            return True
        elif bet == '1 to 18' and isinstance(result, int) and 1 <= result <= 18:
            return True
        elif bet == '19 to 36' and isinstance(result, int) and 19 <= result <= 36:
            return True
        elif bet == '1st 12' and isinstance(result, int) and 1 <= result <= 12:
            return True
        elif bet == '2nd 12' and isinstance(result, int) and 13 <= result <= 24:
            return True
        elif bet == '3rd 12' and isinstance(result, int) and 25 <= result <= 36:
            return True
        return False

    def get_payout(self, bet):
        if isinstance(bet, int) or bet in ['0', '00']:
            return 35
        elif bet in ['RED', 'BLACK', 'ODD', 'EVEN', '1 to 18', '19 to 36']:
            return 1
        elif bet in ['1st 12', '2nd 12', '3rd 12']:
            return 2
        return 0

if __name__ == '__main__':
    root = tk.Tk()
    app = RouletteGUI(root)
    root.mainloop()
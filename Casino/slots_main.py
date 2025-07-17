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



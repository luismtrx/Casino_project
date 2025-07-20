import random
import tkinter as tk
from tkinter import messagebox, simpledialog
from casino_stats import CasinoStats


class Cards:
    def __init__(self, num_decks=1):
        self.deck = self.create_deck(num_decks)
        self.shuffle_deck()
        self.current_card = 0

    def create_deck(self, num_decks=1):
        suits = ['s', 'c', 'd', 'h']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [s + r for s in suits for r in ranks] * num_decks
        return deck

    def shuffle_deck(self):
        random.shuffle(self.deck)
        self.current_card = 0

    def deal_card(self):
        if self.current_card >= len(self.deck):
            print("Deck is empty, reshuffling...")
            self.shuffle_deck()
        card = self.deck[self.current_card]
        self.current_card += 1
        return card

    def deal_initial_hand(self):
        player_hand = [self.deal_card(), self.deal_card()]
        dealer_hand = [self.deal_card(), self.deal_card()]
        return player_hand, dealer_hand

    def card_value(self, card):
        rank = card[1:]
        if rank in ['J', 'Q', 'K']:
            return 10
        elif rank == 'A':
            return 11  # initially treat as 11, adjust later
        else:
            return int(rank)

    def card_pretty(self, card):
        suit_map = {'s': '♠', 'c': '♣', 'd': '♦', 'h': '♥'}
        return f"{suit_map[card[0]]}{card[1:]}"


class CheatTool:
    def __init__(self, cards_instance):
        self.cards = cards_instance

    def peek_dealer_card(self, dealer_hand):
        return dealer_hand[0]  # Return the hidden card

    def force_next_card(self, forced_card):
        if forced_card in self.cards.deck[self.cards.current_card:]:
            self.cards.deck.remove(forced_card)
            self.cards.deck.insert(self.cards.current_card, forced_card)
            print(f"[Cheat] Forced next card to be: {forced_card}")
        else:
            print("[Cheat] Card not found in remaining deck.")


class CasinoBlackjackGUI:
    def __init__(self, root, gambler, parent_window, balance_var):
        self.root = root
        self.gambler = gambler  # Casino gambler object
        self.parent_window = parent_window
        self.balance_var = balance_var
        self.casino_stats = CasinoStats()

        self.root.title("Blackjack Game")
        self.root.geometry("900x700")
        self.root.configure(bg='green')
        self.root.grab_set()  # Make window modal

        self.cards = Cards(num_decks=6)  # Use 6 decks like real casinos
        self.cheat_tool = CheatTool(self.cards)

        self.player_hands = []  # Can have multiple hands if split
        self.dealer_hand = []
        self.game_active = False
        self.current_bet = 0
        self.current_hand_index = 0  # Which hand is currently being played
        self.hand_bets = []  # Bet for each hand
        self.hand_status = []  # Status of each hand ('playing', 'stood', 'bust', 'blackjack')
        self.doubled_down = []  # Track which hands have doubled down
        self.cheated_in_game = False  # Track if player cheated in current game

        self.setup_gui()

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.root.grab_release()
        self.root.destroy()

    def setup_gui(self):
        # Title
        title_label = tk.Label(self.root, text="BLACKJACK",
                               font=("Arial", 24, "bold"),
                               fg="gold", bg='green')
        title_label.pack(pady=10)

        # Balance info
        self.balance_label = tk.Label(self.root, text=f"Balance: ${self.gambler.balance:.2f}",
                                      font=("Arial", 16),
                                      fg="white", bg='green')
        self.balance_label.pack(pady=5)

        # Bet info
        self.bet_label = tk.Label(self.root, text="No bet placed",
                                  font=("Arial", 14),
                                  fg="yellow", bg='green')
        self.bet_label.pack(pady=5)

        # Dealer section
        dealer_frame = tk.Frame(self.root, bg='green')
        dealer_frame.pack(pady=20)

        tk.Label(dealer_frame, text="DEALER", font=("Arial", 16, "bold"),
                 fg="white", bg='green').pack()

        self.dealer_cards_frame = tk.Frame(dealer_frame, bg='green')
        self.dealer_cards_frame.pack(pady=10)

        self.dealer_score_label = tk.Label(dealer_frame, text="",
                                           font=("Arial", 12),
                                           fg="lightblue", bg='green')
        self.dealer_score_label.pack()

        # Player section
        player_frame = tk.Frame(self.root, bg='green')
        player_frame.pack(pady=20)

        tk.Label(player_frame, text="PLAYER", font=("Arial", 16, "bold"),
                 fg="white", bg='green').pack()

        # Container for multiple hands
        self.player_hands_container = tk.Frame(player_frame, bg='green')
        self.player_hands_container.pack(pady=10)

        # Will be populated with hand frames dynamically
        self.player_hand_frames = []
        self.player_score_labels = []

        # Current hand indicator
        self.current_hand_label = tk.Label(player_frame, text="",
                                           font=("Arial", 12, "bold"),
                                           fg="yellow", bg='green')
        self.current_hand_label.pack()

        # Status
        self.status_label = tk.Label(self.root, text="Place a bet to start!",
                                     font=("Arial", 14),
                                     fg="orange", bg='green')
        self.status_label.pack(pady=10)

        # Buttons frame
        button_frame = tk.Frame(self.root, bg='green')
        button_frame.pack(pady=20)

        # Game buttons
        tk.Button(button_frame, text="Place Bet", command=self.place_bet,
                  font=("Arial", 12), bg="darkgreen", fg="white", width=12).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Hit", command=self.hit,
                  font=("Arial", 12), bg="blue", fg="white", width=12).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Stand", command=self.stand,
                  font=("Arial", 12), bg="red", fg="white", width=12).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="New Game", command=self.new_game,
                  font=("Arial", 12), bg="purple", fg="white", width=12).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Double Down", command=self.double_down,
                  font=("Arial", 12), bg="darkred", fg="white", width=12).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(button_frame, text="Split", command=self.split,
                  font=("Arial", 12), bg="darkorange", fg="white", width=12).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(button_frame, text="Exit", command=self.on_closing,
                  font=("Arial", 12), bg="darkblue", fg="white", width=12).grid(row=1, column=3, padx=5, pady=5)
        cheat_frame = tk.Frame(self.root, bg='green')
        cheat_frame.pack(pady=10)

        tk.Label(cheat_frame, text="Cheating:", font=("Arial", 10, "bold"),
                 fg="red", bg='green').grid(row=0, column=0, columnspan=2)
        tk.Button(cheat_frame, text="Peek Dealer", command=self.peek_card,
                  font=("Arial", 10), bg="orange", fg="black", width=15).grid(row=1, column=0, padx=5)
        tk.Button(cheat_frame, text="Force Ace", command=self.force_ace,
                  font=("Arial", 10), bg="orange", fg="black", width=15).grid(row=1, column=1, padx=5)

    def update_balance_display(self):
        self.balance_label.config(text=f"Balance: ${self.gambler.balance:.2f}")
        if self.balance_var:
            self.balance_var.set(f"Balance: ${self.gambler.balance:.2f}")

    def place_bet(self):
        if self.game_active:
            messagebox.showwarning("Warning", "Game in progress! Finish current round first.")
            return

        if self.gambler.balance <= 0:
            messagebox.showerror("Error", "Insufficient funds! Please deposit money.")
            return

        try:
            max_bet = self.gambler.balance
            amount = float(simpledialog.askstring("Place Bet",
                                                  f"Enter your bet amount (Max: ${max_bet:.2f}):"))

            if amount <= 0:
                raise ValueError("Bet must be positive")

            if amount > self.gambler.balance:
                raise ValueError("Insufficient funds")

            # Deduct bet from gambler's balance
            self.gambler.balance -= amount
            self.gambler.save()  # Save to database

            self.current_bet = amount
            self.bet_label.config(text=f"Current Bet: ${self.current_bet:.2f}")
            self.update_balance_display()

            # Reset cheat tracking for new game
            self.cheated_in_game = False

            # Start new round
            self.start_new_round()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Invalid bet amount: {str(e)}")

    def start_new_round(self):
        player_hand, dealer_hand = self.cards.deal_initial_hand()

        # Initialize single hand
        self.player_hands = [player_hand]
        self.dealer_hand = dealer_hand
        self.hand_bets = [self.current_bet]
        self.hand_status = ['playing']
        self.doubled_down = [False]
        self.current_hand_index = 0

        self.game_active = True
        self.status_label.config(text="Game started! Hit, Stand, Double Down, or Split?")
        self.update_labels()

        # Check for blackjack
        if self.calculate_score(self.player_hands[0]) == 21:
            self.status_label.config(text="BLACKJACK! You win!")
            self.end_game(blackjack=True)

    def create_card_widget(self, parent, card, hidden=False):
        if hidden:
            # Create hidden card
            card_frame = tk.Frame(parent, bg='navy', relief='raised', bd=3, width=70, height=100)
            card_frame.pack_propagate(False)

            # Card back pattern
            back_label = tk.Label(card_frame, text="🂠", font=("Arial", 30),
                                  fg="white", bg='navy')
            back_label.pack(expand=True)

        else:
            # Create visible card
            suit_colors = {'♠': 'black', '♣': 'black', '♦': 'red', '♥': 'red'}
            pretty_card = self.cards.card_pretty(card)
            suit = pretty_card[0]
            rank = pretty_card[1:]

            card_frame = tk.Frame(parent, bg='white', relief='raised', bd=3, width=70, height=100)
            card_frame.pack_propagate(False)

            inner_frame = tk.Frame(card_frame, bg='white')
            inner_frame.pack(fill='both', expand=True, padx=2, pady=2)

            # Top rank and suit
            top_label = tk.Label(inner_frame, text=f"{rank}\n{suit}",
                                 font=("Arial", 8, "bold"),
                                 fg=suit_colors[suit], bg='white',
                                 justify='center')
            top_label.pack(side='top', anchor='nw')

            # Center suit symbol
            center_label = tk.Label(inner_frame, text=suit,
                                    font=("Arial", 24),
                                    fg=suit_colors[suit], bg='white')
            center_label.pack(expand=True)

            # Bottom rank and suit
            bottom_label = tk.Label(inner_frame, text=f"{suit}\n{rank}",
                                    font=("Arial", 8, "bold"),
                                    fg=suit_colors[suit], bg='white',
                                    justify='center')
            bottom_label.pack(side='bottom', anchor='se')

        return card_frame

    def clear_cards(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def create_hand_frames(self):
        # Clear existing frames
        for frame in self.player_hand_frames:
            frame.destroy()

        self.player_hand_frames = []
        self.player_score_labels = []

        # Create frame for each hand
        for i in range(len(self.player_hands)):
            hand_container = tk.Frame(self.player_hands_container, bg='green')
            hand_container.pack(side='left', padx=20)

            # Hand label
            hand_label = tk.Label(hand_container, text=f"Hand {i + 1}",
                                  font=("Arial", 12, "bold"),
                                  fg="white", bg='green')
            hand_label.pack()

            # Cards frame
            cards_frame = tk.Frame(hand_container, bg='green')
            cards_frame.pack(pady=5)

            # Score label
            score_label = tk.Label(hand_container, text="",
                                   font=("Arial", 10),
                                   fg="lightgreen", bg='green')
            score_label.pack()

            # Status label
            status_label = tk.Label(hand_container, text="",
                                    font=("Arial", 10),
                                    fg="yellow", bg='green')
            status_label.pack()

            self.player_hand_frames.append({
                'container': hand_container,
                'cards': cards_frame,
                'score': score_label,
                'status': status_label
            })

    def update_labels(self):
        if len(self.player_hand_frames) != len(self.player_hands):
            self.create_hand_frames()

        # Clear existing dealer cards
        self.clear_cards(self.dealer_cards_frame)

        # Update dealer cards
        if self.dealer_hand:
            for i, card in enumerate(self.dealer_hand):
                if i == 0 and self.game_active:
                    # First card is hidden during game
                    card_widget = self.create_card_widget(self.dealer_cards_frame, card, hidden=True)
                else:
                    card_widget = self.create_card_widget(self.dealer_cards_frame, card)
                card_widget.pack(side='left', padx=5, pady=5)

        # Update dealer score
        if self.dealer_hand:
            if self.game_active:
                self.dealer_score_label.config(text="Score: ?")
            else:
                dealer_score = self.calculate_score(self.dealer_hand)
                self.dealer_score_label.config(text=f"Score: {dealer_score}")
        else:
            self.dealer_score_label.config(text="")

        # Update player hands
        for i, hand in enumerate(self.player_hands):
            frame = self.player_hand_frames[i]

            # Clear and update cards
            self.clear_cards(frame['cards'])
            for card in hand:
                card_widget = self.create_card_widget(frame['cards'], card)
                card_widget.pack(side='left', padx=2)

            # Update score
            score = self.calculate_score(hand)
            bet_text = f"Bet: ${self.hand_bets[i]:.2f}"
            if self.doubled_down[i]:
                bet_text += " (Doubled)"
            frame['score'].config(text=f"Score: {score}\n{bet_text}")

            # Update status
            status = self.hand_status[i]
            if i == self.current_hand_index and self.game_active:
                frame['status'].config(text="👈 PLAYING", fg="yellow")
            elif status == 'bust':
                frame['status'].config(text="💥 BUST", fg="red")
            elif status == 'blackjack':
                frame['status'].config(text="🎯 BLACKJACK", fg="gold")
            elif status == 'stood':
                frame['status'].config(text="✋ STOOD", fg="lightblue")
            else:
                frame['status'].config(text="", fg="yellow")

        # Update current hand indicator
        if self.game_active and len(self.player_hands) > 1:
            self.current_hand_label.config(
                text=f"Playing Hand {self.current_hand_index + 1} of {len(self.player_hands)}")
        else:
            self.current_hand_label.config(text="")

    def calculate_score(self, hand):
        score = 0
        aces = 0
        for card in hand:
            val = self.cards.card_value(card)
            score += val
            if card[1:] == 'A':
                aces += 1

        # Adjust for aces
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1
        return score

    def hit(self):
        if not self.game_active:
            messagebox.showwarning("Warning", "Place a bet first!")
            return

        if self.current_hand_index >= len(self.player_hands):
            messagebox.showwarning("Warning", "No active hand to hit!")
            return

        current_hand = self.player_hands[self.current_hand_index]

        # Check if hand is already finished
        if self.hand_status[self.current_hand_index] != 'playing':
            messagebox.showwarning("Warning", "This hand is already finished!")
            return

        # Deal card to current hand
        card = self.cards.deal_card()
        current_hand.append(card)
        self.update_labels()

        # Check for bust
        current_score = self.calculate_score(current_hand)
        if current_score > 21:
            self.hand_status[self.current_hand_index] = 'bust'
            self.status_label.config(text=f"Hand {self.current_hand_index + 1} BUST!")
            self.move_to_next_hand()
        elif current_score == 21:
            self.hand_status[self.current_hand_index] = 'stood'
            self.status_label.config(text=f"Hand {self.current_hand_index + 1} got 21! Auto-standing...")
            self.move_to_next_hand()

    def move_to_next_hand(self):
        self.current_hand_index += 1

        if self.current_hand_index >= len(self.player_hands):
            # All hands finished, dealer plays
            self.dealer_play()
        else:
            # Move to next hand
            self.update_labels()
            self.status_label.config(text=f"Playing Hand {self.current_hand_index + 1}")

    def stand(self):
        if not self.game_active:
            messagebox.showwarning("Warning", "Place a bet first!")
            return

        if self.current_hand_index >= len(self.player_hands):
            return

        # Mark current hand as stood
        self.hand_status[self.current_hand_index] = 'stood'
        self.status_label.config(text=f"Hand {self.current_hand_index + 1} stood!")

        # Move to next hand
        self.move_to_next_hand()

    def dealer_play(self):

        # Dealer hits on 16 and stands on 17
        while self.calculate_score(self.dealer_hand) < 17:
            self.dealer_hand.append(self.cards.deal_card())

        self.update_labels()

        # Evaluate all hands
        self.evaluate_all_hands()

    def evaluate_all_hands(self):
        dealer_score = self.calculate_score(self.dealer_hand)
        dealer_bust = dealer_score > 21

        total_winnings = 0
        results = []

        for i, hand in enumerate(self.player_hands):
            player_score = self.calculate_score(hand)
            bet = self.hand_bets[i]

            if self.hand_status[i] == 'bust':
                # Player busted - lose bet
                result = "BUST"
                winnings = 0
            elif self.hand_status[i] == 'blackjack':
                # Blackjack pays 3:2
                result = "BLACKJACK"
                winnings = bet * 2.5
            elif dealer_bust:
                # Dealer busted - player wins
                result = "WIN (Dealer Bust)"
                winnings = bet * 2
            elif player_score > dealer_score:
                # Player wins
                result = "WIN"
                winnings = bet * 2
            elif player_score < dealer_score:
                # Dealer wins
                result = "LOSE"
                winnings = 0
            else:
                # Push (tie)
                result = "PUSH"
                winnings = bet  # Return bet

            total_winnings += winnings
            results.append(f"Hand {i + 1}: {result} (${winnings:.2f})")

        # Update gambler balance and stats
        self.gambler.balance += total_winnings
        self.gambler.save()

        # Record game results in database
        total_bet = sum(self.hand_bets)
        won = total_winnings > total_bet
        self.gambler.record_game(won, total_bet, total_winnings, "Blackjack", self.cheated_in_game)

        # Update casino stats
        payout = total_winnings - total_bet  # Net payout (negative means casino profit)
        self.casino_stats.add_bet(total_bet, max(0, payout))  # Only count positive payouts

        # Handle cheating
        if self.cheated_in_game:
            self.gambler.add_cheat()
            if self.gambler.is_banned:
                messagebox.showwarning("BANNED",
                                       "You have been banned for excessive cheating! Contact a manager to restore access.")

        # Display results
        result_text = "\n".join(results)
        result_text += f"\n\nTotal Winnings: ${total_winnings:.2f}"
        result_text += f"\nDealer: {dealer_score}"

        messagebox.showinfo("Game Results", result_text)

        # Update displays
        self.update_balance_display()

        # Reset game
        self.game_active = False
        self.current_bet = 0
        self.bet_label.config(text="No bet placed")
        self.status_label.config(text="Place a bet to start!")

    def double_down(self):
        """Double the bet and take exactly one more card"""
        if not self.game_active:
            messagebox.showwarning("Warning", "Place a bet first!")
            return

        if self.current_hand_index >= len(self.player_hands):
            return

        current_hand = self.player_hands[self.current_hand_index]

        # Can only double down with exactly 2 cards
        if len(current_hand) != 2:
            messagebox.showwarning("Warning", "Can only double down with 2 cards!")
            return

        # Check if already doubled down
        if self.doubled_down[self.current_hand_index]:
            messagebox.showwarning("Warning", "Already doubled down on this hand!")
            return

        # Check if player has enough money
        current_bet = self.hand_bets[self.current_hand_index]
        if current_bet > self.gambler.balance:
            messagebox.showwarning("Warning", "Insufficient funds to double down!")
            return

        # Double the bet
        self.gambler.balance -= current_bet
        self.gambler.save()
        self.hand_bets[self.current_hand_index] *= 2
        self.doubled_down[self.current_hand_index] = True

        # Deal exactly one card
        card = self.cards.deal_card()
        current_hand.append(card)

        # Check for bust
        current_score = self.calculate_score(current_hand)
        if current_score > 21:
            self.hand_status[self.current_hand_index] = 'bust'
            self.status_label.config(text=f"Hand {self.current_hand_index + 1} DOUBLED DOWN and BUST!")
        else:
            self.hand_status[self.current_hand_index] = 'stood'
            self.status_label.config(text=f"Hand {self.current_hand_index + 1} DOUBLED DOWN!")

        self.update_labels()
        self.update_balance_display()

        # Move to next hand
        self.move_to_next_hand()

    def split(self):

        if not self.game_active:
            messagebox.showwarning("Warning", "Place a bet first!")
            return

        if self.current_hand_index >= len(self.player_hands):
            return

        current_hand = self.player_hands[self.current_hand_index]

        # Can only split with exactly 2 cards
        if len(current_hand) != 2:
            messagebox.showwarning("Warning", "Can only split with 2 cards!")
            return

        # Check if cards have same rank
        card1_rank = current_hand[0][1:]  # Remove suit
        card2_rank = current_hand[1][1:]  # Remove suit

        if card1_rank != card2_rank:
            messagebox.showwarning("Warning", "Can only split pairs!")
            return

        # Check if player has enough money for second bet
        current_bet = self.hand_bets[self.current_hand_index]
        if current_bet > self.gambler.balance:
            messagebox.showwarning("Warning", "Insufficient funds to split!")
            return

        # Place bet for second hand
        self.gambler.balance -= current_bet
        self.gambler.save()

        # Split the cards
        card1 = current_hand[0]
        card2 = current_hand[1]

        # Create two new hands
        hand1 = [card1, self.cards.deal_card()]
        hand2 = [card2, self.cards.deal_card()]

        # Replace current hand with first split hand
        self.player_hands[self.current_hand_index] = hand1

        # Insert second hand after current hand
        self.player_hands.insert(self.current_hand_index + 1, hand2)
        self.hand_bets.insert(self.current_hand_index + 1, current_bet)
        self.hand_status.insert(self.current_hand_index + 1, 'playing')
        self.doubled_down.insert(self.current_hand_index + 1, False)

        self.update_labels()
        self.update_balance_display()
        self.status_label.config(text=f"Split! Playing Hand {self.current_hand_index + 1}")

        # Check for blackjack on current hand
        if self.calculate_score(hand1) == 21:
            self.hand_status[self.current_hand_index] = 'blackjack'
            self.move_to_next_hand()


    def peek_card(self):
        """Cheat tool: peek at dealer's hidden card"""
        if not self.dealer_hand:
            messagebox.showinfo("Peek", "No dealer hand to peek at!")
            return

        # Mark as cheating
        self.cheated_in_game = True

        hidden_card = self.cheat_tool.peek_dealer_card(self.dealer_hand)
        messagebox.showinfo("Peek", f"Dealer's hidden card: {self.cards.card_pretty(hidden_card)}")

    def force_ace(self):
        """Cheat tool: force next card to be an ace"""
        self.cheated_in_game = True
        self.cheat_tool.force_next_card("sA")  # Force spade ace
        messagebox.showinfo("Cheat", "Next card forced to be Ace of Spades!")

    def new_game(self):
        if self.game_active:
            response = messagebox.askyesno("New Game", "Game in progress. Start new game anyway?")
            if not response:
                return

        self.cards = Cards(num_decks=6)
        self.cheat_tool = CheatTool(self.cards)
        self.player_hands = []
        self.dealer_hand = []
        self.game_active = False
        self.current_bet = 0
        self.cheated_in_game = False

        self.status_label.config(text="Place a bet to start!")
        self.bet_label.config(text="No bet placed")
        self.dealer_score_label.config(text="")

        # Clear card displays
        self.clear_cards(self.dealer_cards_frame)

        # Clear hand frames
        for frame in self.player_hand_frames:
            frame['container'].destroy()
        self.player_hand_frames = []

        self.update_balance_display()


def blackjackGUI(gambler, parent_window, balance_var):

    blackjack_window = tk.Toplevel(parent_window)
    game = CasinoBlackjackGUI(blackjack_window, gambler, parent_window, balance_var)
    return game


# For testing standalone
def test_standalone():


    class MockGambler:
        def __init__(self):
            self.id = 1
            self.first_name = "Test"
            self.last_name = "Player"
            self.balance = 1000.0
            self.cheat_count = 0
            self.is_banned = False
            self.wins = 0
            self.losses = 0
            self.money_won = 0
            self.money_lost = 0
            self.games_played = 0

        def save(self):
            pass

        def record_game(self, won, bet, payout, game, cheated):
            pass

        def add_cheat(self):
            self.cheat_count += 1
            if self.cheat_count >= 3:
                self.is_banned = True

    root = tk.Tk()
    root.withdraw()

    mock_gambler = MockGambler()
    game = blackjackGUI(mock_gambler, root, None)

    root.mainloop()


if __name__ == "__main__":
    test_standalone()
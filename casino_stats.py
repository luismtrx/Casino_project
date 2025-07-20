import sqlite3

database = sqlite3.connect("casino8.db", check_same_thread = False)
cursor = database.cursor()


class CasinoStats:
    def __init__(self):
        row = cursor.execute("SELECT * FROM CASINO_STATS WHERE ID=1").fetchone()
        self.id = row[0]
        self.total_made = row[1]
        self.total_payout = row[2]
        self.num_gamblers = row[3]
        self.cheaters_kicked = row[4]
        self.num_bets_made = row[5]
        self.num_betsr = row[6]
        self.num_betss = row[7]
        self.num_betsc = row[8]
        

    def add_bet(self, bet, payout):
        self.total_made += bet
        self.total_payout += payout
        self.num_bets_made += 1
        self._save()

    def add_gambler(self):
        self.num_gamblers += 1
        self._save()

    def kick_cheater(self):
        self.cheaters_kicked += 1
        self._save()

    def add_game(self, game_name):
        self.num_bets_made = self.num_bets_made +1

        if game_name.lower() == "roulette":
            self.num_betsr = self.num_betsr  +1
        elif game_name.lower() == "slots":
            self.num_betss = self.num_betss  +1
        elif game_name.lower() == "craps":
            self.num_betsc = self.num_betsc  +1
       
        self._save()

    def add_bet(self, bet, payout):
        self.total_made = self.total_made + bet
        self.total_payout = self.total_payout + payout
        self.num_bets_made = self.num_bets_made +1
        self._save()
    

    def _save(self):
        cursor.execute("""UPDATE CASINO_STATS SET
                TOTAL_MADE=?, 
                TOTAL_PAYOUT=?, 
                NUM_GAMBLERS=?, 
                CHEATERS_KICKED=?,
                NUM_BETS_MADE=?,
                       NUM_BETS_MADER=?,
                       NUM_BETS_MADES=?,
                       NUM_BETS_MADEC=?,
            WHERE ID=1""", (self.total_made, self.total_payout,self.num_gamblers, self.cheaters_kicked, 
                            self.num_bets_made, self.num_betsr, self.num_betss, self.num_betsc))
        database.commit()

    
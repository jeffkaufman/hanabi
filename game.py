import random

COLORS = ["R",
          "G",
          "W",
          "Y",
          "B"]

MEANING = {"R": 0,
           "G": 1,
           "W": 2,
           "Y": 3,
           "B": 4,
           1: 4,
           2: 3,
           3: 2,
           4: 1,
           5: 0}

class Card(object):
  def __init__(self, color, number):
    self.color = color
    self.number = number

  def __repr__(self):
    return "%s%s" % (self.number, self.color)

class Hand(object):
  def __init__(self, deck):
    self.cards = [deck.draw() for i in range(5)]

  def __repr__(self):
    return "Hand<%s>" % (",".join(str(x) for x in self.cards))

  def play(self, index, deck):
    card = self.cards.pop(index)
    self.cards.append(deck.draw())
    return card

class Deck(object):
  def __init__(self):
    self.cards = []
    for number in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]:
      for color in COLORS:
        self.cards.append(Card(color, number))
    random.shuffle(self.cards)

  def __repr__(self):
    return "Deck<%s>" % (",".join(str(x) for x in self.cards))

  def draw(self):
    return self.cards.pop(0)

class Board(object):
  def __init__(self):
    self.piles = {}
    for color in COLORS:
      self.piles[color] = 0

  def __repr__(self):
    return "Board<%s>" % (",".join("%s%s" % (self.piles[color], color)
                                   for color in COLORS))
  def legal(self, card):
    return self.piles[card.color] == card.number - 1

  def update(self, card):
    assert self.legal(card)
    self.piles[card.color] = card.number

  def score(self):
    return sum(self.piles.values())

class Game(object):
  def __init__(self, num_players):
    self.deck = Deck()
    self.hands = [Hand(self.deck) for i in range(num_players)]
    self.board = Board()
    self.turn = 0
    self.mistakes = 0
    self.information = num_players * 4
    self.num_players = num_players
    self.told = None

  def take_turn(self):
    active_index = self.turn % self.num_players
    next_index = (self.turn + 1) % self.num_players

    print "Turn %s" % self.turn
    print "mistakes: %s" % self.mistakes
    print "information: %s" % self.information

    print self.deck
    for i, hand in enumerate(self.hands):
      print hand, "*" if i == active_index else ""
    print self.board

    active_hand = self.hands[active_index]
    next_hand = self.hands[next_index]

    moved = False

    if self.told:
      told_index = MEANING[self.told]

      chosen_card = active_hand.play(index=told_index, deck=self.deck)
      print "playing", chosen_card

      moved = True
      if self.board.legal(chosen_card):
        self.board.update(chosen_card)
        if chosen_card.number == 5:
          self.information += 1
      else:
        self.mistakes += 1

      self.told = None

    def choose_message():
      options = []

      for potential_index in [0, 1, 2, 3, 4]:
        if self.board.legal(next_hand.cards[potential_index]):
          tell_color = None
          tell_number = None
          for color in COLORS:
            if MEANING[color] == potential_index:
              matching_colors = len([x.color == color for x in next_hand.cards])
              tell_color = color
          for number in [1, 2, 3, 4, 5]:
            if MEANING[number] == potential_index:
              matching_numbers = len([x.number == number for x in next_hand.cards])
              tell_number = number

          if matching_colors:
            tell = tell_color
          elif matching_numbers:
            tell = tell_number
          else:
            print "Would like to signal %s for %s but can't" % (
              potential_index, next_hand.cards[potential_index])
            continue # no legal signal

          score = -potential_index
          if potential_index == 4:
            score += 5

          score += 4*(matching_colors + matching_numbers)

          options.append([score, tell])

      if not options:
        return None
      if len(options) == 1:
        return options[0][-1]

      options.sort()
      for score, option in options:
        print score, option
      print "choosing ", options[-1][-1]
      return options[-1][-1]

    if not moved and self.information > 0:
      message = choose_message()
      if message:
        self.told = message
        print "Told %s to mean play #%s" % (message, MEANING[message])
        moved = True

    if not moved:
      chosen_card = active_hand.play(index=len(active_hand.cards)-1,
                                     deck=self.deck)
      self.information += 1
      print "discarding", chosen_card
      moved = True

    score = self.board.score()
    if score == 25 or len(self.deck.cards) < 5 or self.mistakes >= 3:
      return str(score)

    self.turn += 1
    return "continue"

def start():
  g = Game(num_players=2)
  while True:
    status = g.take_turn()
    if status == "continue":
      print "-"*60
      continue
    print status
    return

if __name__ == "__main__":
  start()

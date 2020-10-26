# Anne LoVerso
# Python Set Game

import random
import time

import pygame
from pygame.locals import *
import planes
import planes.gui

from class_utils import Button
from class_utils import ScreenText

####################
# DEFINE CONSTANTS #
####################
AUTO_ADD3 = True

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

CARD_WIDTH = 200
CARD_HEIGHT = 100

TOP_MARGIN = 50
LEFT_MARGIN = 50
SPACE_HORIZ = ((3*WINDOW_WIDTH/4)-2*LEFT_MARGIN-3*CARD_WIDTH)/2

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)


HINTS = False
NUM_HINTS = 5
TIME_DEDUC = 3000

FONT_BIG = pygame.font.SysFont("Arial", 40)
FONT_SMALL = pygame.font.SysFont("Arial", 20)

COLORS = ['green', 'red', 'purple']
SHAPES = ['oval', 'diamond', 'squiggle']
NUMBERS = [1, 2, 3]
SHADES = ['filled', 'shaded', 'empty']


def check_set(card1, card2, card3):
    """
    Given three cards, checks whether they form a Set
    Args: card1, card2, card3 - objects of type Card
    Returns: True if cards form a Set, False otherwise
    """
    color_check = all_same_or_all_diff(card1.color, card2.color, card3.color)
    shape_check = all_same_or_all_diff(card1.shape, card2.shape, card3.shape)
    num_check = all_same_or_all_diff(card1.number, card2.number, card3.number)
    shade_check = all_same_or_all_diff(card1.shade, card2.shade, card3.shade)
    return color_check and shape_check and num_check and shade_check


def all_same_or_all_diff(attr1, attr2, attr3):
    """
    Given three attributes (one from each of three cards), checks whether the
    they are either all the same, or all different
    Functions as a helper method to check_set
    Args: attr1, attr2, attr3 - attributes of a card (color, shape, number, shade)
    Returns: True if all three attributes are equal OR none of them are equal, False otherwise
    """
    if attr1 == attr2 and attr2 == attr3:
        return True
    elif (attr1 != attr2) and (attr2 != attr3) and (attr3 != attr1):
        return True
    else:
        return False

def format_secs(secs):
    """
    Helper function, takes a game time in seconds and formats it into a human-readable string
    Returns string in format, for example: "1m 20s"
    """
    minutes = secs / 60
    seconds = secs % 60
    return str(minutes) + "m " + str(seconds) + "s"

class Card(planes.Plane):
    """
    a Card has attributes of color, shape, number, and shade
    """
    def __init__(self, name, color, shape, number, shade):
        planes.Plane.__init__(self, name, pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT), False, False)
        self.color = color
        self.shape = shape
        self.number = number
        self.shade = shade
        self.been_clicked = False

    def __eq__(self, other):
        return  self.color == other.color and \
                self.shape == other.shape and \
                self.number == other.number and \
                self.shade == other.shade

    def __ne__(self, other):
        return not self.__eq__(other)

    def clicked(self, button_name):
        self.been_clicked = not self.been_clicked

    def update(self):
        pass

##################
# BUTTON CLASSES #
##################


# GAME BUTTON
class AddThreeCardsButton(Button):
    """When clicked, adds three new cards if no Set on the board"""
    def __init__(self, name, rect, callback, model):
        Button.__init__(self, name, rect, callback, model)
        self.image = pygame.image.load("img/plus3_icon.png")

    def clicked(self, button_name):
        if self.model.check_in_play():
            if not self.model.check_if_any_sets():
                self.model.add_new_cards(3)


# GAME BUTTON
class HintButton(Button):
    """
    When clicked, gives a hint
    If Set on the board: highlights the next card in the Set
    If no Set on board: adds three new cards
    Ignores cards already clicked, so user should not click when cards are highlighted
    """
    def __init__(self, name, rect, callback, model):
        Button.__init__(self, name, rect, callback, model)
        self.image = pygame.image.load("img/hint_icon.png")

    def clicked(self, button_name):
        if self.model.check_in_play():
            if self.model.hints_left > 0:
                self.model.hints_left -= 1
                for card1 in self.model.in_play_cards:
                    for card2 in self.model.in_play_cards:
                        for card3 in self.model.in_play_cards:
                            if card1 != card2 and card2 != card3 and card1 != card3:
                                if check_set(card1, card2, card3):
                                    if not card1.been_clicked:
                                        card1.been_clicked = True
                                        return
                                    elif not card2.been_clicked:
                                        card2.been_clicked = True
                                        return
                                    else:
                                        card3.been_clicked = True
                                        return
                self.model.add_new_cards(3)


# HOME BUTTON
class Game():
    """
    A Game is a single game that ends when won, lost or cancelled
    """
    def __init__(self, model):
        ########################
        # GAME SCREEN ELEMENTS #
        ########################
        self.deck = []
        self.model = model

        #  make 81 unique cards, add to deck
        for color in COLORS:
            for shape in SHAPES:
                for number in NUMBERS:
                    for shade in SHADES:
                        card_to_add = Card(color + shape + shade + str(number),
                                           color, shape, number, shade)
                        self.deck.append(card_to_add)
                        card_to_add.image = pygame.image.load("img/" + card_to_add.name + ".png")

        self.actors = []

        self.in_play_cards = []
        self.clicked_cards = []
        self.out_of_play_cards = []

        self.sets_found = 0
        self.sets_wrong = 0 # should we take off points for these?
        self.hints_left = NUM_HINTS

        #### Elements of a game ####
        self.sets_found_label = ScreenText("sets_found_label",
                                           "Sets: " + str(self.sets_found),
                                           pygame.Rect(3*WINDOW_WIDTH/4, 290, WINDOW_WIDTH/4, 50),
                                           FONT_BIG)
        self.left_in_deck_label = ScreenText("left_in_deck_label",
                                             "Deck: " + str(len(self.deck) - (len(self.in_play_cards) + len(self.out_of_play_cards))),
                                             pygame.Rect(3*WINDOW_WIDTH/4, 505, WINDOW_WIDTH/4, 25),
                                             FONT_SMALL)
        if not AUTO_ADD3:
            self.add3_button = AddThreeCardsButton("add_three_cards_button",
                                                   pygame.Rect(3*WINDOW_WIDTH/4 + (WINDOW_WIDTH/4 - 200)/2, 360, 100, 100),
                                                   AddThreeCardsButton.clicked,
                                                   self)
        if HINTS:
            self.hint_button = HintButton("hint_button",
                                          pygame.Rect(3*WINDOW_WIDTH/4 + (WINDOW_WIDTH/4 - 200)/2 + 100, 360, 100, 100),
                                          HintButton.clicked,
                                          self)
            self.hints_left_label = ScreenText("hints_left_label",
                                               "Hints Remaining: " + str(self.hints_left),
                                               pygame.Rect(3*WINDOW_WIDTH/4, 475, WINDOW_WIDTH/4, 25),
                                               FONT_SMALL)

        self.logo = planes.Plane("setlogo",
                                 pygame.Rect(3*WINDOW_WIDTH/4, 50, 240, 162),
                                 False, False)
        self.logo.image = pygame.image.load("img/set.jpg")

        #### CATEGORIES ####
        self.gamebuttons = [self.logo]
        self.gamelabels = [self.sets_found_label, self.left_in_deck_label]
        if HINTS:
            self.gamebuttons.append(self.hint_button)
            self.gamelabels.append(self.hints_left_label)
        if not AUTO_ADD3:
            self.gamebuttons.append(self.add3_button)

        # start the game
        self.add_new_cards(12)

    # Add cards to the in-play cards
    # Number = number of cards to add
    # Index allows adding 1 card in the same position as a removed card
    # Does not check whether we SHOULD because assumes we have checked that before calling
    def add_new_cards(self, number, index=0):
        if not len(self.in_play_cards) + len(self.out_of_play_cards) == len(self.deck):
            i = 0
            while i < number:
                num = random.randint(0, len(self.deck)-1)
                card = self.deck[num]
                if card not in self.in_play_cards and card not in self.out_of_play_cards:
                    self.in_play_cards.insert(index, card)
                    i += 1
            if AUTO_ADD3:
                if not self.check_if_any_sets():
                    self.add_new_cards(3)

    # Checks if any sets on the board
    def check_if_any_sets(self):
        for card1 in self.in_play_cards:
            for card2 in self.in_play_cards:
                for card3 in self.in_play_cards:
                    if card1 != card2 and card2 != card3 and card1 != card3:
                        if check_set(card1, card2, card3):
                            return True
        return False

    # Checks if game is won
    def check_if_won(self):
        return(not self.check_if_any_sets()) and \
               (len(self.in_play_cards) + len(self.out_of_play_cards) == len(self.deck))

    # Game can only be lost if playing in time mode
    def check_in_play(self):
        return True  # TODO: add multiplayer set counter so winner is one with most sets

    # Called infinitely
    def update(self):
        # if game not in play, display messages, not cards
        if not self.check_in_play():
            self.actors = []
            self.actors += self.gamelabels + self.gamebuttons
            if HINTS:
                self.hints_left_label.update_text("Hints Remaining: " + str(self.hints_left))
            self.left_in_deck_label.update_text("Deck: " + str(len(self.deck) - (len(self.in_play_cards) + len(self.out_of_play_cards))))

            message_box = planes.Plane('message_box',
                                       pygame.Rect(LEFT_MARGIN,
                                                   TOP_MARGIN,
                                                   3*CARD_WIDTH + 2*SPACE_HORIZ,
                                                   4*CARD_HEIGHT + 3*((WINDOW_HEIGHT - 4*CARD_HEIGHT - 2*TOP_MARGIN) / 3)))
            message_box.image.fill((0, 0, 0))
            message_texts = []

            self.actors.append(message_box)
            self.actors += message_texts

        # game in play
        else:
            self.actors = []

            #check which cards are clicked
            self.clicked_cards = []
            for card in self.in_play_cards:
                self.actors.append(card)
                if card.been_clicked:
                    self.clicked_cards.append(card)
                card.update()

            #add click boxes
            for card in self.clicked_cards:
                clicked_box = planes.Plane("box" + card.name,
                                           pygame.Rect(card.rect.x-5,
                                                       card.rect.y-5,
                                                       card.rect.width + 10,
                                                       card.rect.height + 10),
                                           False, False)
                clicked_box.image = pygame.image.load("img/clickbox.png")
                self.actors.insert(0, clicked_box)

            #check for sets
            if len(self.clicked_cards) == 3:
                is_set = check_set(self.clicked_cards[0],
                                   self.clicked_cards[1],
                                   self.clicked_cards[2])
                if is_set:
                    self.sets_found += 1
                    self.sets_found_label.update_text("Sets: " + str(self.sets_found))

                    #remove cards and add new ones
                    for card in self.clicked_cards:
                        self.out_of_play_cards.append(card)
                        index = self.in_play_cards.index(card)
                        self.in_play_cards.remove(card)
                        if len(self.in_play_cards) < 12:
                            self.add_new_cards(1, index)
                else:
                    self.sets_wrong += 1
                for card in self.clicked_cards:
                    card.been_clicked = False


            self.actors += self.gamelabels + self.gamebuttons
            if HINTS:
                self.hints_left_label.update_text("Hints Remaining: " + str(self.hints_left))
            self.left_in_deck_label.update_text("Deck: " + str(len(self.deck) - (len(self.in_play_cards) + len(self.out_of_play_cards))))

class Model:
    """
    The Model is the overall object in controlling the entire program
    It instantiates Game objects as needed but also contains home screen
    """
    def __init__(self):
        self.background = (20, 20, 20)

        self.game = Game(self)
        self.actors = []

        ########################
        # HOME SCREEN ELEMENTS #
        ########################
        self.title = planes.Plane("title", pygame.Rect(LEFT_MARGIN, TOP_MARGIN, 13*WINDOW_WIDTH/16, (WINDOW_HEIGHT-300)))

    # update model
    def update(self):
        self.game.update()
        self.actors = self.game.actors[:]


class View:
    """
    Draw elements of Model actors onto screen
    """
    def __init__(self, model, screen):
        self.model = model
        self.screen = screen

    def draw(self):
        self.screen.remove_all()
        if isinstance(self.model.background, str):
            self.screen.image = pygame.transform.scale(pygame.image.load(self.model.background),
                                                       (WINDOW_WIDTH, WINDOW_HEIGHT))
        else:
            self.screen.image.fill(self.model.background)

        #put cards in play into a grid:

        if self.model.game is not None:
            space_vert = 50
            # space_vert changes so that cards adjust themselves if more than 12
            # never more than 21, any collection of 20 cards must contain a Set
            if len(self.model.game.in_play_cards) == 12:
                space_vert = (WINDOW_HEIGHT - 4*CARD_HEIGHT - 2*TOP_MARGIN) / 3
            elif len(self.model.game.in_play_cards) == 15:
                space_vert = (WINDOW_HEIGHT - 5*CARD_HEIGHT - 2*TOP_MARGIN) / 4
            elif len(self.model.game.in_play_cards) == 18:
                space_vert = (WINDOW_HEIGHT - 6*CARD_HEIGHT - 2*TOP_MARGIN) / 5
            elif len(self.model.game.in_play_cards) == 21:
                space_vert = (WINDOW_HEIGHT - 7*CARD_HEIGHT - 2*TOP_MARGIN) / 6

            # create positions of cards
            positions = [(LEFT_MARGIN, TOP_MARGIN),
                         (LEFT_MARGIN + CARD_WIDTH + SPACE_HORIZ, TOP_MARGIN),
                         (LEFT_MARGIN + 2*CARD_WIDTH + 2*SPACE_HORIZ, TOP_MARGIN),

                         (LEFT_MARGIN, TOP_MARGIN + CARD_HEIGHT + space_vert),
                         (LEFT_MARGIN + CARD_WIDTH + SPACE_HORIZ, TOP_MARGIN + CARD_HEIGHT + space_vert),
                         (LEFT_MARGIN + 2*CARD_WIDTH + 2*SPACE_HORIZ, TOP_MARGIN + CARD_HEIGHT + space_vert),

                         (LEFT_MARGIN, TOP_MARGIN + 2*CARD_HEIGHT + 2*space_vert),
                         (LEFT_MARGIN + CARD_WIDTH + SPACE_HORIZ, TOP_MARGIN + 2*CARD_HEIGHT + 2*space_vert),
                         (LEFT_MARGIN + 2*CARD_WIDTH + 2*SPACE_HORIZ, TOP_MARGIN + 2*CARD_HEIGHT + 2*space_vert),

                         (LEFT_MARGIN, TOP_MARGIN + 3*CARD_HEIGHT + 3*space_vert),
                         (LEFT_MARGIN + CARD_WIDTH + SPACE_HORIZ, TOP_MARGIN + 3*CARD_HEIGHT + 3*space_vert),
                         (LEFT_MARGIN + 2*CARD_WIDTH + 2*SPACE_HORIZ, TOP_MARGIN + 3*CARD_HEIGHT + 3*space_vert),

                         (LEFT_MARGIN, TOP_MARGIN + 4*CARD_HEIGHT + 4*space_vert),
                         (LEFT_MARGIN + CARD_WIDTH + SPACE_HORIZ, TOP_MARGIN + 4*CARD_HEIGHT + 4*space_vert),
                         (LEFT_MARGIN + 2*CARD_WIDTH + 2*SPACE_HORIZ, TOP_MARGIN + 4*CARD_HEIGHT + 4*space_vert),

                         (LEFT_MARGIN, TOP_MARGIN + 5*CARD_HEIGHT + 5*space_vert),
                         (LEFT_MARGIN + CARD_WIDTH + SPACE_HORIZ, TOP_MARGIN + 5*CARD_HEIGHT + 5*space_vert),
                         (LEFT_MARGIN + 2*CARD_WIDTH + 2*SPACE_HORIZ, TOP_MARGIN + 5*CARD_HEIGHT + 5*space_vert),

                         (LEFT_MARGIN, TOP_MARGIN + 6*CARD_HEIGHT + 6*space_vert),
                         (LEFT_MARGIN + CARD_WIDTH + SPACE_HORIZ, TOP_MARGIN + 6*CARD_HEIGHT + 6*space_vert),
                         (LEFT_MARGIN + 2*CARD_WIDTH + 2*SPACE_HORIZ, TOP_MARGIN + 6*CARD_HEIGHT + 6*space_vert)]

            # assign positions to cards in play
            for i in range(len(self.model.game.in_play_cards)):
                self.model.game.in_play_cards[i].rect.x = positions[i][0]
                self.model.game.in_play_cards[i].rect.y = positions[i][1]

        # add all actors to screen
        for actor in self.model.actors:
            self.screen.sub(actor)

# THE MAIN LOOP
def main():
    pygame.init()
    size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    main_screen = planes.Display(size)
    main_screen.grab = False
    main_screen.image.fill(BLACK)
    main_model = Model()
    view = View(main_model, main_screen)
    running = True

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                raise SystemExit

        main_screen.process(events)
        main_model.update()
        main_screen.update()
        main_screen.render()

        view.draw()
        pygame.display.flip()
        time.sleep(.001)

    pygame.quit()

if __name__ == "__main__":
    main()

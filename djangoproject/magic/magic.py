# magic.py
"""
Sandbox to begin experimenting with building a few useful
tools for magic the gathering deck building
"""
import string


class Card(object):
    def __init__(self, title,
                 multiverseid="",
                 manaCost="",
                 convertedManaCost=0,
                 type="",
                 rules="",
                 cardSet="",
                 rarity=""):
        self.title = title
        self.multiverseid = multiverseid
        self.manaCost = manaCost
        self.convertedManaCost = convertedManaCost
        self.type = type
        self.rules = rules
        self.cardSet = cardSet
        self.rarity = rarity

    def convertManaCost(self):
        cost = 0
        number = ""
        for i, c in enumerate(self.manaCost):
            if c in string.digits:
                number += c
            elif c in ("W","U","B", "R", "G"):
                cost += 1
                if number:
                    cost += int(number)
                    number = ""
        if number:
            cost += int(number)
        return cost

    wubrg = ("W","U", "B", "R", "G")
    wubrgSet = set(("W","U","B","R","G"))
    def getColors(self):
        result = ""
        colors = set(self.manaCost)
        mycolors = colors.intersection(Card.wubrgSet)
        for color in Card.wubrg:
            if color in mycolors:
                result += color
        return result


class Deck(object):
    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def __len__(self):
        return len(self.cards)

    def colorBreakdown(self):
        colors = {}
        counts = {}
        for card in self.cards:
            cardColor = card.getColors()
            if cardColor not in counts:
                counts[cardColor] = 0
            counts[cardColor] += 1
            colors[cardColor] = (counts[cardColor] * 1.0) / len(self.cards)
        return colors

    def manaColorCount(self):
        colors = {}
        for card in self.cards:
            for symbol in card.manaCost:
                if symbol in Card.wubrg:
                    if symbol not in colors:
                        colors[symbol] = 0
                    colors[symbol] += 1
        return colors

    def manaCurve(self):
        curve = {}
        for card in self.cards:
            convertedManaCost = int(card.convertedManaCost)
            if convertedManaCost == 0:
                continue
            if convertedManaCost not in curve:
                curve[convertedManaCost] = 0
            curve[convertedManaCost] += 1
        return curve

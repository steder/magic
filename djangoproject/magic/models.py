import string

from django.db import models


class Card(models.Model):
    class Meta:
        db_table = "cards"
    id = models.AutoField(primary_key=True, db_column='id')
    multiverseid = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    manaCost = models.CharField(max_length=256)
    convertedManaCost = models.IntegerField()
    type = models.CharField(max_length=256)
    rules = models.TextField()
    cardSet = models.CharField(max_length=256)
    rarity = models.CharField(max_length=256)

    def __unicode__(self):
        return self.title

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


class Deck(models.Model):
    class Meta:
        db_table = "decks"

    id = models.AutoField(primary_key=True, db_column='id')
    title = models.CharField(max_length=256)
    cards = models.ManyToManyField(Card, through="DeckCards")

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return "/magic:/deck/%i"%(self.id,)
        
    def add(self, card, count=1):
        DeckCards.objects.create(count=count, cardid=card, deckid=self)

    def __len__(self):
        return self.cards.count()

    def colorBreakdown(self):
        colors = {}
        counts = {}
        for card in self.cards.all():
            cardColor = card.getColors()
            if cardColor not in counts:
                counts[cardColor] = 0
            counts[cardColor] += 1
            colors[cardColor] = (counts[cardColor] * 1.0) / self.cards.count()
        return colors

    def manaColorCount(self):
        colors = {}
        for card in self.cards.all():
            for symbol in card.manaCost:
                if symbol in Card.wubrg:
                    if symbol not in colors:
                        colors[symbol] = 0
                    colors[symbol] += 1
        return colors

    def copiesOfCard(self, card):
        return card.deckcards_set.filter(deckid=self)[0].count

    def manaCurve(self):
        curve = {}
        for card in self.cards.all():
            convertedManaCost = int(card.convertedManaCost)
            if convertedManaCost == 0:
                continue
            if convertedManaCost not in curve:
                curve[convertedManaCost] = 0
            curve[convertedManaCost] += self.copiesOfCard(card)
        return curve
        
    def manaCurveSortedList(self):
        curve = self.manaCurve()
        keys = curve.keys()
        keys.sort()
        return [(key, curve[key]) for key in keys]

class DeckCards(models.Model):
    """A model representing the many to mana relationship between
    cards and decks"""
    class Meta:
        db_table = "deck_cards"

    id = models.AutoField(primary_key=True, db_column="id")
    count = models.IntegerField(db_column="count")
    deckid = models.ForeignKey(Deck, db_column="deckid")
    cardid = models.ForeignKey(Card, db_column="cardid")

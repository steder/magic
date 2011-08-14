import os

from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm import sessionmaker

import magic


engine = create_engine("sqlite:///magic.db", echo=False)

metadata = MetaData()
cards_table = Table("cards", metadata,
                    Column("id", Integer, primary_key=True),
                    Column("multiverseid", String),
                    Column("title", String),
                    Column("manaCost", String),
                    Column("convertedManaCost", Integer),
                    Column("type", String),
                    Column("rules", String),
                    Column("cardSet", String),
                    Column("rarity", String)
)

decks_table = Table("decks", metadata,
                    Column("id", Integer, primary_key=True),
                    Column("title", String)
                    )

deck_cards_table = Table('deck_cards', metadata,
                   Column("id", Integer, primary_key=True),
                   Column("count", Integer),
                   Column("deckid", Integer, ForeignKey('decks.id')),
                   Column('cardid', Integer, ForeignKey('cards.id')),
                   )

# map our objects:
mapper(magic.Card, cards_table)
mapper(magic.Deck, decks_table,
       properties={
        'cards':relation(magic.Card,
                         secondary=deck_cards_table,
                         backref='decks'),
        }
)


# Create a new session so we can issue queries:
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

# create any tables we've defined that don't already exist:
#metadata.bind = engine
#metadata.create_all()
cards_table.create(bind=engine, checkfirst=True)
decks_table.create(bind=engine, checkfirst=True)
deck_cards_table.create(bind=engine, checkfirst=True)


print "# CARDS IN DB:", session.query(magic.Card).count()

myDeck = magic.Deck()

#myDeck.add(session.query(magic.Card).filter_by(title="Bogardan Hellkite").first())
#for x in xrange(5): # adding 5 forests
#    myDeck.add(session.query(magic.Card).filter_by(title="Forest").first())

import exceptions

class MissingCardError(exceptions.Exception):
    pass

def getCardByName(name):
    card = session.query(magic.Card).filter_by(title=name).first()
    if not card:
        raise MissingCardError("Unable to locate card %s!"%(name,))
    return card

def addCardsWithQuantityToDeck(deck, cards_with_quantities):
    for cardName, quantity in cards_with_quantities:
        card = getCardByName(cardName)
        for i in xrange(quantity):
            deck.add(card)
    return deck

deckDescription = (
    ("Bogardan Hellkite", 1),
    ("Forest", 6),
    ("Mountain", 4),
    ("Swamp", 4),
    ("Dragonskull Summit", 4),
    ("Jund Panorama", 4),
    ("Dragon Fodder", 4),
    ("Hellkite Hatchling", 4),
    ("Shivan Dragon", 3),
    ("Crucible of Fire", 1),
    ("Predator Dragon", 2),
    ("Lightning Bolt", 4),
)

addCardsWithQuantityToDeck(myDeck, deckDescription)

print myDeck, "has", len(myDeck), "cards in it"
colors = myDeck.colorBreakdown()
for color in colors:
    print "My Deck is %s%% %s"%(colors[color]*100.0,
                                color or "COLORLESS")


curve = myDeck.manaCurve()
print "Mana Curve:"
keys = curve.keys()
keys.sort()
for key in keys:
    print "%s "%(key,) + ("*" * curve[key])

session.add(myDeck)
session.flush()
print "decks:", session.query(magic.Deck).count()
session.rollback()

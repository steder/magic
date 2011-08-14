"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import unittest

from django.test import TestCase

from djangoproject.magic import models as magic


class TestCard(unittest.TestCase):
    def test_title(self):
        card = magic.Card.objects.create(
            title="Serra Angel", 
            convertedManaCost=5,
        )
        self.assertEqual("Serra Angel", card.title)


class TestCardColor(unittest.TestCase):
    def test_white(self):
        card = magic.Card.objects.create(
            title="Serra Angel",
            convertedManaCost=5
        )
        card.manaCost = "3WW"
        self.assertEqual("W", card.getColors())

    def test_colorless(self):
        card = magic.Card.objects.create(title="Darksteel Colossus",
            convertedManaCost=10,
        )
        card.manaCost = "10"
        self.assertEqual("", card.getColors())

#     def test_color_colorless(self):
#         """What color(s) does a card identify itself as?"""

#         card = magic.Card("Darksteel Colossus")
#         card.manaCost = "10"


class TestCardConvertManaCost(unittest.TestCase):
    def setUp(self):
        self.card = magic.Card.objects.create(title="Test Card",
            convertedManaCost=1
        )

    def test_zero(self):
        self.assertEqual(0, self.card.convertManaCost())

    def test_1W(self):
        self.card.manaCost = "1W"
        self.assertEqual(2, self.card.convertManaCost())

    def test_2W(self):
        self.card.manaCost = "2W"
        self.assertEqual(3, self.card.convertManaCost())

    def test_WUBRG(self):
        self.card.manaCost = "WUBRG"
        self.assertEquals(5, self.card.convertManaCost())

    def test_10(self):
        self.card.manaCost = "10"
        self.assertEquals(10, self.card.convertManaCost())

    def test_XW(self):
        self.card.manaCost = "XW"
        self.assertEqual(1, self.card.convertManaCost())

    def test_X10W3U4R5G10B(self):
        """X is ignored and 
        10 + W(1) + 3 + U(1) + 4 + R(1) + 5 + G(1) + 10 + B(1) = 37"""
        self.card.manaCost = "X10W3U4R5G10B"
        self.assertEqual(37, self.card.convertManaCost())

class TestDeck(unittest.TestCase):
    def setUp(self):
        self.mydeck = magic.Deck.objects.create()

    def test_addOneCard(self):
        self.mydeck.add(magic.Card.objects.create(title="Serra Angel",
            convertedManaCost=5,
        ))
        self.assertEqual(1, len(self.mydeck))

    def test_addTwoCards(self):
        self.mydeck.add(magic.Card.objects.create(title="Serra Angel", convertedManaCost=5))
        self.mydeck.add(magic.Card.objects.create(title="Plains", convertedManaCost=0))
        self.assertEqual(2, len(self.mydeck))


class TestDeckColorPercentageBreakdown(unittest.TestCase):
    def setUp(self):
        self.mydeck = magic.Deck.objects.create()

        self.card1 = magic.Card.objects.create(title="Cancel", convertedManaCost=3,
        manaCost="B")
        self.card2 = magic.Card.objects.create(title="Serra Angel", convertedManaCost=5,
        manaCost="W")

    def test_whiteDeck(self):
        self.mydeck.add(self.card2)
        colors = self.mydeck.colorBreakdown()
        self.assertEqual(1.0, colors["W"])

    def test_blueWhiteDeck(self):
        """50/50 split blue and white"""
        self.mydeck.add(self.card1)
        self.mydeck.add(self.card2)
        colors = self.mydeck.colorBreakdown()
        self.assertEqual(0.5, colors["W"])
        self.assertEqual(0.5, colors["B"])

    def test_bluerWhiteDeck(self):
        """66/33 split blue white """
        self.mydeck.add(self.card1)
        self.mydeck.add(self.card1)
        self.mydeck.add(self.card2)
        colors = self.mydeck.colorBreakdown()
        self.assertEqual(0.33333333333333331, colors["W"])
        self.assertEqual(0.66666666666666663, colors["B"])

    def test_emptyDeck(self):
        colors = magic.Deck.objects.create().colorBreakdown()
        self.assertEqual({}, colors)

class TestManaColorCount(unittest.TestCase):
    def setUp(self):
        self.mydeck = magic.Deck.objects.create()

        self.card1 = magic.Card.objects.create(title="Cancel", convertedManaCost=3,
        manaCost="1BB")
        self.card2 = magic.Card.objects.create(title="Serra Angel", convertedManaCost=5,
        manaCost="3WW")

    def test_emptyDeck(self):
        colors = self.mydeck.manaColorCount()
        self.assertEqual({}, colors)

    def test_3colorless_2w(self):
        self.mydeck.add(self.card2)
        colors = self.mydeck.manaColorCount()
        self.assertEqual(2, colors['W'])

    def test_4colorless2B2W(self):
        self.mydeck.add(self.card1)
        self.mydeck.add(self.card2)
        colors = self.mydeck.manaColorCount()
        self.assertEqual(2, colors['B'])
        self.assertEqual(2, colors['W'])

class TestManaCurve(unittest.TestCase):
    def setUp(self):
        self.mydeck = magic.Deck.objects.create()

        self.card1 = magic.Card.objects.create(title="Cancel", convertedManaCost=3,
        manaCost="B")
        self.card2 = magic.Card.objects.create(title="Serra Angel", convertedManaCost=5,
        manaCost="W")

    def test_emptyDeck(self):
        colors = self.mydeck.manaColorCount()
        self.assertEqual({}, colors)

    def test_oneCard_1(self):
        self.mydeck.add(self.card1)
        curve = self.mydeck.manaCurve()
        self.assert_( 3 in curve )
        self.assertEqual(1, curve[3])

    def test_oneCard_2(self):
        self.mydeck.add(self.card2)
        curve = self.mydeck.manaCurve()
        self.assert_( 5 in curve )
        self.assertEqual(1, curve[5])

    def test_twoCards(self):
        self.mydeck.add(self.card2)
        self.mydeck.add(self.card1)
        curve = self.mydeck.manaCurve()
        self.assert_( 3 in curve)
        self.assert_( 5 in curve )
        self.assertEqual(1, curve[3])
        self.assertEqual(1, curve[5])

    def test_threeCards(self):
        self.mydeck.add(self.card2, 2)
        self.mydeck.add(self.card1)
        curve = self.mydeck.manaCurve()
        self.assert_(3 in curve)
        self.assert_(5 in curve)
        self.assertEqual(1, curve[3])
        self.assertEqual(2, curve[5])

    def test_zeroMana(self):
        self.card2.convertedManaCost = 0
        self.card2.save() # actually update the mana cost on the card object
        self.mydeck.add(self.card2)
        curve = self.mydeck.manaCurve()
        self.assertEqual({}, curve)

    def test_costRepresentedAsIntegers(self):
        """Costs should be represented as integers,
        not as strings.  Discovered that strings were
        being stored in the database"""
        self.card2.convertedManaCost = "0"
        self.mydeck.add(self.card2)
        curve = self.mydeck.manaCurve()
        self.assertEqual({5:1}, curve)

    def test_zeroAndNonZeroCards(self):
        self.card2.convertedManaCost = 0
        self.mydeck.add(self.card1)
        self.mydeck.add(self.card2)
        curve = self.mydeck.manaCurve()
        self.assert_(0 not in curve)
        self.assertEqual(1, curve[3])

    

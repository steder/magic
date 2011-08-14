# Create your views here.

from django.shortcuts import render_to_response, get_object_or_404

from djangoproject.magic import models

def index(request):
    return render_to_response('magic/index.html')

def card(request, card_id):
    c = get_object_or_404(models.Card, pk=card_id)
    imageUrl = "http://gatherer.wizards.com/Handlers/Image.ashx"
    imageParams = "?multiverseid=%s&type=card"%(c.multiverseid,)
    imageUrl += imageParams
    return render_to_response('magic/card.html', {'card':c,
                                                  'imageUrl':imageUrl})

def deck(request, deck_id):
    d = get_object_or_404(models.Deck, pk=deck_id)
    return render_to_response('magic/deck.html', {'deck':d,
                                                  })

from django.contrib import admin

from djangoproject.magic.models import Card, Deck, DeckCards


class DeckCardsInline(admin.TabularInline):
    model = DeckCards
    #extra = 1
    max_num = 0
    raw_id_fields = ("cardid",)


class DeckAdmin(admin.ModelAdmin):
    inlines = (DeckCardsInline,)


class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'cardSet',
                    'convertedManaCost', 'rarity')
    list_filter = ('cardSet', 'rarity')
    search_fields = ["title",
                     "type",
                     "cardSet"
                     ]
    
admin.site.register(Card, CardAdmin)
admin.site.register(Deck, DeckAdmin)

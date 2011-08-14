# magic.urls

from django.conf.urls.defaults import patterns

urlpatterns = patterns('djangoproject.magic.views',
    (r'^$', 'index'),
    (r'^card/(?P<card_id>\d+)/$', 'card'),
    (r'^deck/(?P<deck_id>\d+)/$', 'deck'),
)

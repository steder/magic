import glob
import sqlite3

import html5lib
from html5lib import treebuilders

connection = sqlite3.connect("magic.db")

cards = []
for htmlfile in glob.glob("html/*.html"):
    print "processing:", htmlfile
    # open the file and get ready to parse
    f = open(htmlfile, "r")
    parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("beautifulsoup"))
    bs = parser.parse(f)

    # replace images with plaintext
    for img in bs.findAll(u"img"):
        if img.get('alt', None) is not None:
            img.replaceWith('('+img['alt']+')')

    cardsInFile = 0
    # scrap card data
    for row in bs.findAll(u"tr"):
        card = {}
        card['id'] = row.find("a")['href'].split("=")[-1]
        titleSpan = row.find("span", {"class":"cardTitle",})
        titleLink = titleSpan.find("a")
        card['title'] = titleLink.contents[0]
        manaCost = "".join([unicode(x) for x in row.find("span", {"class":"manaCost",}).contents])
        card['manaCost'] = manaCost.rstrip().lstrip()
        convertedManaCost = row.find("span", {"class":"convertedManaCost",}).contents[0]
        card['convertedManaCost'] = convertedManaCost.rstrip().lstrip()
        typeSpan = row.find("span", {"class":"typeLine",})
        card['type'] = "\n".join([unicode(x) for x in typeSpan.contents])
        card['type'] = card['type'].replace(u"\xe2\u20ac\u201d","-")
        card['type'] = card['type'].rstrip().lstrip()
        rulesDiv = row.find("div", {"class":"rulesText",})
        # print "rulesDiv.contents:", rulesDiv.contents
        rules = "\n".join([unicode(x) for x in rulesDiv.contents])
        card['rules'] = rules.rstrip().lstrip()
        card['rules'] = card['rules'].replace("<p>", "")
        card['rules'] = card['rules'].replace("</p>","")
        card['rules'] = card['rules'].replace("<i>", "")
        card['rules'] = card['rules'].replace("</i>","")
        setRarity = row.find("td", {'class':"rightCol setVersions",}).find("a").contents[0]
        set = setRarity.split("(")
        card['set'] = set[1]
        card['rarity'] = set[2].split(")")[0]
        # done stripping card info
        cards.append(card)
        cardsInFile += 1
    print "parsed %s cards from %s"%(cardsInFile, htmlfile)

print "Total cards parsed:", len(cards)    
print "sorting cards:"
cards.sort(key=lambda x: x['title'])

#for card in cards:
#    print "*"*50
#    print "title:", card['title'], "/", card['manaCost'], "/", card['convertedManaCost']
#    print "type:", card['type']
#    print "rules:", card['rules']
#    print "set:", card['set']
#    print "rarity:", card['rarity']
#    print "gatherer multiverseid:", card['id']

print "inserting cards into db:"

cursor = connection.cursor()

card_generator = ((c['id'], c['title'], c['manaCost'],
                   c['convertedManaCost'], c['type'],
                   c['rules'], c['set'], c['rarity']) for c in cards)

cursor.executemany("""INSERT INTO cards
       (multiverseid, title, manaCost,
        convertedManaCost, type,
        rules, cardSet, rarity)
        VALUES
       (?, ?, ?,
        ?, ?,
        ?, ?, ?);
""", card_generator)

cursor.execute("select count(*) from cards")

print "We've got", cursor.fetchall(), "cards"

connection.commit()
cursor.close()

                  

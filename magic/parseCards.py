import sys
from xml.etree import cElementTree

import html5lib
from html5lib import treebuilders

def main():
    cards = []
    fileToParse = sys.argv[1]
    source = open(fileToParse, "r")
    parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("etree", cElementTree))
    tree = parser.parse(source)

    # replace image tags with their alt text:
    #for element in tree.findall(".//img@alt")

    for parent in tree.getiterator():
        for index, child in enumerate(parent.findall("img")):
            if child.get("alt",None) is not None:
                altText = child.get("alt")
                parent.remove(child)
                try:
                    print "adding (%s) to parent text (%s)"%(altText, parent.text)
                    parent.text += altText
                except Exception, e:
                    print "replacing parent.text (%s) with (%s)"%(parent.text, altText)
                    parent.text = altText

    print cElementTree.tostring(tree, encoding="UTF-8")

    for element in tree.findall(".//tr"):
        if "class" in element.keys():
            if "cardItem" in element.get("class"):
                card = {}
                # left - card image
                left, middle, right = element.getchildren()
                left_a = left.getchildren()[1]
                image_url = left_a.get("href")
                card['multiverseid'] = image_url.split("=")[-1]
                # middle - card info
                cardInfo = middle.getchildren()[1]
                card['title'] = [span for span in cardInfo.getchildren() if span.get("class",None) == "cardTitle"][0].getchildren()[0].text
                card['typeLine'] = [span for span in cardInfo.getchildren() if span.get("class",None) == "typeLine"][0].text
                rulesTextDiv = [span for span in cardInfo.getchildren() if span.get("class",None) == "rulesText"][0]
                #print "rulesTextDiv:",rulesTextDiv
                rulesText = [p.text for p in rulesTextDiv.getchildren()]
                #print "rulesText:", rulesText
                try:
                    card['rulesText'] = "\n".join(rulesText)
                except Exception, e:
                    #print e
                    card['rulesText'] = ""

                # right - set versions

                # done with this card
                card['title'] = card['title'].lstrip().rstrip()
                card['typeLine'] = card['typeLine'].lstrip().rstrip()
                card['typeLine'] = card['typeLine'].replace(u"\xe2\u20ac\u201d","-")
                card['rulesText'] = card['rulesText'].lstrip().rstrip()
                cards.append(card)                

    cards.sort(key=lambda x: x['title'])
    for card in cards:
        print "*"*50
        print "title:", card['title']
        print "type:", card['typeLine']
        print "rules:", card["rulesText"]

    return cards

if __name__=="__main__":
    tree = main()

from fontTools.ttLib import TTFont

font = TTFont('iconfont_da2e2ef.ttf')
font.saveXML('./11.xml')
uniList = font['cmap'].tables[0].ttFont.getGlyphOrder()
print(uniList)
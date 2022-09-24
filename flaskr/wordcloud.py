from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

def create_wordcloud_from_file(filename):
    text = open(filename).read()
    wordcloud = WordCloud().generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    splitName = filename.split("/")
    imgName = splitName[len(splitName)-1]
    extension = filename.split(".")
    extname = extension[len(extension)-1]
    derivedName = imgName.replace(f'.{extname}',"")
    i = 0
    imgPath = f'flaskr/WordCloud/{derivedName}{i}.png'
    while True:
        #Check if a image with the name wordcloud.png exists
        if os.path.exists(imgPath):
            i = i + 1
        else:
            img = wordcloud.to_file(imgPath)
            break
    return imgPath
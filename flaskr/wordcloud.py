from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

def create_wordcloud_from_file(filename):
    text = open(filename).read()
    wordcloud = WordCloud().generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    newFileName = os.path.splitext(filename)[0]
    i = 0
    imgPath = f'WordCloud/{newFileName}{i}.png'
    while True:
        #Check if a image with the name wordcloud.png exists
        if os.path.exists(imgPath):
            i = i + 1
        else:
            img = wordcloud.to_file(imgPath)
            break
    return imgPath
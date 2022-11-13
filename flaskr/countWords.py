import string
import os

def countWords1(doc):
    if os.path.exists('./flaskr/WordCount/count.txt'):
        os.remove('./flaskr/WordCount/count.txt')
    strings = ""
    d = dict()
    stringlist = doc.split()
    for word in stringlist:
        word = word.strip(string.punctuation)
        word = word.lower()
        if word not in d:
            d[word] = 1
        else:
            d[word] += 1
        strings += word+","
    stop_words = (" ")
    for word in stringlist:
        #Dont count words that are stop words
        if word in stop_words:
                continue
        if word in d:
            d[word] = d[word] + 1
        else:
            d[word] = 1
    counter = 0
    for key in sorted(d, key=d.get, reverse=True):
        print(key, ":", d[key])
        with open('./flaskr/WordCount/count.txt', 'a', encoding="utf8") as f:
                f.write(key + " : " + str(d[key]) + "\n")
                counter = counter + 1
                # if(counter == 100 or str(key) == ""):
                #     break


def countWords2(doc):
    if os.path.exists('./flaskr/WordCount/count2.txt'):
        os.remove('./flaskr/WordCount/count2.txt')
    strings = ""
    d = dict()
    stringlist = doc.split()
    for word in stringlist:
        word = word.strip(string.punctuation)
        word = word.lower()
        if word not in d:
            d[word] = 1
        else:
            d[word] += 1
        strings += word+","
    stop_words = (" ")
    for word in stringlist:
        #Dont count words that are stop words
        if word in stop_words:
                continue
        if word in d:
            d[word] = d[word] + 1
        else:
            d[word] = 1
    counter = 0
    for key in sorted(d, key=d.get, reverse=True):
        print(key, ":", d[key])
        with open('./flaskr/WordCount/count2.txt', 'a', encoding="utf8") as f:
                f.write(key + " : " + str(d[key]) + "\n")
                counter = counter + 1
                # if(counter == 100 or str(key) == ""):
                #     break
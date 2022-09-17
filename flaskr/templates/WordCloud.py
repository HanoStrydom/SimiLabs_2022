import sys
import os
import re
import string
import random
import math
import operator
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import re
from flask import Flask, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from html import escape
import cs50
import docx2txt
import PyPDF2


def wordCloud():
        if request.files["file1"].filename.endswith('.docx'):
                file1 = docx2txt.process(request.files["file1"])
        elif request.files["file1"].filename.endswith('.pdf'):
            pdfReader = PyPDF2.PdfFileReader(request.files["file1"])
            pageObj = pdfReader.getPage(0)
            file1 = pageObj.extractText()
        else:
            file1 = request.files["file1"].read().decode("utf-8")
        #Read in the text file
        text = file1
        #Create a word cloud object
        wordcloud = WordCloud().generate(text)
        #Display the generated image
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()

wordCloud()
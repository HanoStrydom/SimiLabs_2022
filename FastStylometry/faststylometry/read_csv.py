import pandas as pd


def convertTohtml(filename):
    a = pd.read_csv('./csvFiles/burrows_delta_output.csv')
    a.to_html('D:/Uni 2022/ISE/Project/github similabs/SimiLabs_2022/FastStylometry/Generated_HTML/' + filename + '.html')
    html_file = a.to_html()
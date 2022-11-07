import pdfkit

# def readToPDF(htmlfile, filename):
#     pdfkit.from_file(htmlfile, './PDFReports/' + filename + '.pdf')

pdfkit.from_url('https://www.google.com/','sample.pdf')
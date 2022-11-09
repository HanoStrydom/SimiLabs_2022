import docx
import PyPDF2
from datetime import datetime

def getMetaDataDoc(doc):
    metadata = {}
    prop = doc.core_properties
    metadata["author"] = prop.author
    metadata["created"] = prop.created
    metadata["last_modified_by"] = prop.last_modified_by
    metadata["modified"] = prop.modified
    return metadata

def getRowColor(author, lastModifiedBy):
    if(author == lastModifiedBy):
        return "w3-light-grey w3-hover-green"
    else:
        return "w3-light-grey w3-hover-red"

def getMetaDataPDF(pdf):
    author = ""
    created_date = ""
    last_modified_date = ""
    # pdfFile = PyPDF2.PdfFileReader(open(pdf,'rb'))
    pdfFile = PyPDF2.PdfReader(open(pdf,'rb'))
    data = pdfFile.getDocumentInfo()
    print(data)
    for metadata in data:
        if(metadata == '/Author'):
            author = data[metadata]
        if(metadata == '/CreationDate'):
            created_date = data[metadata]
            created_dt = datetime.strptime(created_date.replace("'", ""), "D:%Y%m%d%H%M%S%z")
            createdDate = created_dt.strftime("%Y-%m-%d %H:%M:%S")
        if(metadata == '/ModDate'):
            last_modified_date =  data[metadata]
            last_dt = datetime.strptime(created_date.replace("'", ""), "D:%Y%m%d%H%M%S%z")
            lastDate = last_dt.strftime("%Y-%m-%d %H:%M:%S")
    return [author, createdDate, "UNKNOWN", lastDate]


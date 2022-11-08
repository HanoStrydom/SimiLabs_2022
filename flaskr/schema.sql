CREATE DATABASE IF NOT EXISTS SimiLabs DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE Similabs;

--DROP TABLE IF EXISTS accounts;

CREATE TABLE IF NOT EXISTS Accounts (
  id int PRIMARY KEY AUTO_INCREMENT,
  username nvarchar(55) UNIQUE NOT NULL,
  password nvarchar(255) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

Create TABLE IF NOT EXISTS Students (
  StudentID int PRIMARY KEY AUTO_INCREMENT,
  studentFullName varchar(50) NOT NULL,
  studentNumber varchar(8) NOT NULL,
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


Create TABLE IF NOT EXISTS Corpus (
  CorpusID int PRIMARY KEY AUTO_INCREMENT,
  studentID int NOT NULL,
  DocumentID int NOT NULL,
  corpusName varchar(50) NOT NULL,
  corpusDescription varchar(255) NOT NULL,
  FOREIGN KEY (studentID) REFERENCES students(StudentID)
  FOREIGN KEY (documentID) REFERENCES Document(DocumentID)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


Create TABLE IF NOT EXISTS Document (
  DocumentID int PRIMARY KEY AUTO_INCREMENT,
  corpusID int NOT NULL,
  MetadataID int NOT NULL,
  documentName varchar(50) NOT NULL,
  FOREIGN KEY (corpusID) REFERENCES Corpus(CorpusID)
  FOREIGN KEY (MetadataID) REFERENCES Metadata(MetadataID)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


Create TABLE IF NOT EXISTS Metadata (
  MetadataID int PRIMARY KEY AUTO_INCREMENT,
  documentID int NOT NULL,
  author varchar(50) NOT NULL,
  dateCreate date NOT NULL,
  lastModifiedDate date NOT NULL,
  lastModifiedUser varchar(50) NOT NULL,
  FOREIGN KEY (documentID) REFERENCES Document(id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


Create TABLE IF NOT EXISTS Stylometry (
  stylometryID int PRIMARY KEY AUTO_INCREMENT,
  documentID int NOT NULL,
  wordCount int NOT NULL,
  sentenceCount int NOT NULL,
  averageWordLength int NOT NULL,
  averageSentenceLength int NOT NULL,
  FOREIGN KEY (documentID) REFERENCES Document(DocumentID)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS QuickComparison (
  quickComparisonID int PRIMARY KEY AUTO_INCREMENT,
  documentID int NOT NULL,
  documentID2 int NOT NULL,
  FOREIGN KEY (documentID) REFERENCES Document(DocumentID),
  FOREIGN KEY (documentID2) REFERENCES Document(DocumentID)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;	

--Hanno en Annika 
-- create extensive comparison table (
--   extensiveComparisonID int PRIMARY KEY AUTO_INCREMENT,
--   documentID int NOT NULL,
--   documentID2 int NOT NULL,
--   FOREIGN KEY (documentID) REFERENCES Document(DocumentID),
--   FOREIGN KEY (documentID2) REFERENCES Document(DocumentID)
-- ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



CREATE TABLE IF NOT EXISTS QuickAnalysisReport (
  quickAnalysisReportID int PRIMARY KEY AUTO_INCREMENT,
  quickComparisonID int NOT NULL,
  SimilarityPercentage float NOT NULL,
  Author varchar(50) NOT NULL,
  dateCreatedReport date NOT NULL,
  dateCreatedDocument date NOT NULL,
  lastModifiedDate date NOT NULL,
  lastModifiedUser varchar(50) NOT NULL,
  FOREIGN KEY (quickComparisonID) REFERENCES QuickComparison(quickComparisonID),
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


--create report for extensive analysis
--Hanno en annika 
CREATE TABLE IF NOT EXISTS ExtensiveAnalysisReport (
  extensiveAnalysisReportID int PRIMARY KEY AUTO_INCREMENT,
  extensiveComparisonID int NOT NULL,
  SimilarityPercentage float NOT NULL,
  FOREIGN KEY (extensiveComparisonID) REFERENCES ExtensiveComparison(extensiveComparisonID),
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS StylometryAnalysisReport (
  stylometryAnalysisReportID int PRIMARY KEY AUTO_INCREMENT,
  stylometryID int NOT NULL,
  SourceAuthor varchar(50) NOT NULL,
  ComparisonAuthor varchar(50) NOT NULL,
  burrowsDeltaScore float NOT NULL, --a higher score means that the two texts are more similar
  probabilityOfAuthorship float NOT NULL, --a higher score means that the author of the comparison text is more likely to be the same as the source text
  dateOfStylomertyAnalysis date NOT NULL,
  FOREIGN KEY (stylometryID) REFERENCES Stylometry(stylometryID),
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- password is admin
INSERT INTO accounts VALUES (1,'admin','pbkdf2:sha256:260000$j2dCQrXnaDgBrbmO$896a6fe3480ca5cca5a433f78a52dc123ecd81c479620e5bb179de0cce115fef');
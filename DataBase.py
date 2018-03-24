import os
import sqlite3 as sq

import PDFParse
import WebSCraping



class PaperDataBase:

    def __init__(self):
        self.db, self.c = self.__set_DB()
        self.__set_Table()



    def __set_DB(self):
        db = sq.connect('JData.db')
        c = db.cursor()

        return db, c



    def __set_Table(self):
        try:
            self.c.execute("create table Journal(FileName, URL, Title, Authors, Year, JName, Vol, Abst);")
        except sq.OperationalError:
            pass



    def SearchDB(self, FileName, Author, KeyWords):
        """
        Connect to SetResult in main.py and connect to Search button
        :param FileName: File name of .pdf
        :param Author: Authors' name or empty
        :param KeyWords: Key words' list
        :return: String list shows FileName. We will also use this result to open PDF file
        """
        result = []

        if FileName != '':
            self.c.execute("select * from Journal FileName=" + "'" + FileName + "'")
            for row in self.c:
                result.append(row[0])
            return result

        if Author != "":
            condition = "Author like " +"'%" + Author + "%'"
        else:
            condition = ""

        if KeyWords != []:
            for i in range(len(KeyWords)):
                if i == 0:
                    condition += "Abst like " + "'%" + KeyWords[i] + "%'"
                else:
                    condition += " and Abst like " + "'%" + KeyWords[i] + "%'"

        self.c.execute("select * from Journal where " + condition)
        for row in self.c:
            result.append(row[0])

        return result



    def RegistDB(self, FileName, URL):
        """
        Regist (FileName, URL, Title, AuthorsName, Year, JournalName, Vol., Abstract) to DataBase
        If could not get paper's info, raise AssertionError
        :param FileName: File name of .pdf
        :param URL: URL to the info page of the paer
        :return: None. Registrate the journal info to DataBase
        """

        StrList = list
        sq.register_adapter(StrList, lambda l: ';'.join([str(i) for i in l]))
        sq.register_converter("StrList", lambda s: [str(i) for i in s.split(';')])


        if URL == '':
            PDF_Directory = PDFPath().SearchDB(FileName)
            URL = PDFParse.URL(PDF_Directory).get_URL()
        if URL == -1:
            raise AssertionError

        Scrape = WebSCraping.SortJournal(URL)

        Title = Scrape.get_title()
        AuthorName = Scrape.get_authors()
        Year = Scrape.get_year()
        JournalName = Scrape.get_JName()
        Vol = Scrape.get_Vol()
        Abstract = Scrape.get_Abst()

        if Title == -1 or AuthorName == -1 or Year == -1 or JournalName == -1 or Vol == -1 or Abstract == -1:
            raise AssertionError

        self.c.execute('insert into Journal values(?,?,?,?,?,?,?,?)', (FileName, URL, Title, AuthorName, Year,
                                                                         JournalName, Vol, Abstract))
        self.db.commit()

        return None



    def paper_list(self, path):
        """
        :param path: path to paper folder
        :return: list of papers
        """
        result = []
        for dir in os.listdir(path):
            if os.path.isdir(path + "/" + dir):
                result.extend(self.paper_list(path + "/" + dir))
            elif "pdf" in dir:
                result.append((path +  '\\' + dir).replace('\\', '/'))

        return result



    def NotRregistrated(self, path):
        """
        Find PDF file not registrated in the PDF_path
        :return: List
        """
        # path = FilePath().get_path()
        registered = []
        self.c.execute('select * from Journal')
        for row in self.c:
            registered.append(row[0])

        return list(set(self.paper_list(path)) - set(registered))



    def DeletedAlready(self, path):
        """
        Find PDF files deleted already from directory but still registered in the PDF_path.
        :return: List
        """
        registered = []
        self.c.execute('select * from Journal')
        for row in self.c:
            registered.append(row[1])

        return list(set(registered) - set(self.paper_list(path)))





class FilePath:
    """
    Deta base to store the paths to paper folder.
    DataBase name : FilePath.db
    Table name : FilePath
    """

    def __init__(self):
        self.db, self.c = self.__set_DB()
        self.set_Table()



    def __set_DB(self):
        db = sq.connect('FilePath.db')
        c = db.cursor()

        return db, c



    def set_Table(self):
        try:
            self.c.execute("create table FilePath(path);")
        except sq.OperationalError:
            pass



    def is_empty(self):
        """
        If the DataBase of file path to papers is empty or there isn't FilePath.db, return True.
        :return: Boolean
        """
        self.c.execute('select * from FilePath')
        PathList = []
        for row in self.c:
            PathList.append(row)
        if PathList: return False

        return True



    def add_path(self, path):
        sql = "insert into FilePath values(?);"
        self.c.execute(sql, [path])
        self.db.commit()

        return None



    def get_path(self):
        self.c.execute('select * from FilePath')
        result = []
        for row in self.c:
            result.append(row[0])

        return result



    def clear(self, item):
        item = "'" + item + "'"
        self.c.execute("delete from FilePath where path=" + item)
        self.db.commit()



    def close(self):
        self.db.close()






class PDFPath:
    """
    Data base to store paths to all paper in paper folders.
    DataBase name : PDFPath.db
    table name : PDF_path
    """
    def __init__(self):
        self.db, self.c = self.__set_DB()
        self.__set_Table()



    def __set_DB(self):
        db = sq.connect('PDFPath.db')
        c = db.cursor()

        return db, c



    def __set_Table(self):
        try:
            self.c.execute('create table PDF_path(FileName, Path);')
        except sq.OperationalError:
            pass



    def SearchDB(self, FileName):
        """
        Return absolute path of a paper. Using this path, open PDF with os.popen(path) connected to QListWidget.
        :param FileName: PDF File Name
        :return: Absolute Path to the FileName
        """
        FileName += ".pdf"
        self.c.execute("select * from PDF_path where FileName=" + "'" + FileName +"'")
        for row in self.c:
            return row[1]



    def RegistDB(self, FileName, Path):
        self.c.execute('insert into PDF_path values(?, ?)', (FileName, Path))
        self.db.commit()

    def clear(self):
        self.c.execute('delete from PDF_path')

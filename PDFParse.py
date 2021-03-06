from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal

import re
import logging


class PDFAnalyze:

    def __init__(self, path):
        self.path = path

    def get_PDFLayout(self, p):

        fp = open(self.path, 'rb')
        try:
            logging.propagate = False
            logging.getLogger().setLevel(logging.ERROR)
            parser = PDFParser(fp)
            document = PDFDocument()
            parser.set_document(document)

            document.set_parser(parser)
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            pages = list(document.get_pages())
            page_1 = pages[p]
            interpreter.process_page(page_1)
            layout = device.get_result()
        except:
            return -1
        fp.close()

        return layout


class PhysRev(PDFAnalyze):
    def __init__(self, path):
        super().__init__(path)

    def get_URL(self, layout):

        for l in layout:
            if isinstance(l, LTTextBoxHorizontal):
                JournalInfo = re.search(
                    r'DOI: \d+\.\d+/\w+\.\d+\.\d+', l.get_text())

                if JournalInfo:
                    if 'PhysRevLett' in JournalInfo.group():
                        return 'https://journals.aps.org/prl/abstract/' + JournalInfo.group()[5:]

                    elif 'PhysRevB' in JournalInfo.group():
                        return 'https://journals.aps.org/prb/abstract/' + JournalInfo.group()[5:]

                    elif 'RevModPhys' in JournalInfo.group():
                        return 'https://journals.aps.org/rmp/abstract/' + JournalInfo.group()[5:]

        return -1


class Nature(PDFAnalyze):
    def __init__(self, path):
        super().__init__(path)

    def get_URL(self, layout):
        for l in layout:
            if isinstance(l, LTTextBoxHorizontal):
                JournalInfo1 = re.search(r'DOI: \d+\.\d+/\w+\d+', l.get_text())
                JournalInfo2 = re.search(
                    r'DOI: \d+\.\d+/\w+\.\d+.\d+', l.get_text())
                JournalInfo3 = re.search(r'doi:\d+\.\d+/\w+\d+', l.get_text())

                if JournalInfo1:
                    if 'NMAT' in JournalInfo1.group() or 'ncomms' in JournalInfo1.group() or\
                            'NPHYS' in JournalInfo1.group():
                        return 'https://www.nature.com/articles/' + JournalInfo1.group()[13:].lower()

                if JournalInfo2:
                    if 'NNANO' in JournalInfo2.group() or 'NPHOTON' in JournalInfo2.group():
                        return 'https://www.nature.com/articles/' + JournalInfo2.group()[13:].lower()

                if JournalInfo3:
                    if 'nature' in JournalInfo3.group():
                        return 'https://www.nature.com/articles/' + JournalInfo3.group()[12:].lower()

        return -1


class JPSJ(PDFAnalyze):
    def __init__(self, path):
        super().__init__(path)

    def get_URL(self, layout):
        for l in layout:
            if isinstance(l, LTTextBoxHorizontal):
                JournalInfo = re.search(
                    r'\d+\.\d+/JPSJ\.\d+\.\d+', l.get_text())
                if JournalInfo:
                    return 'http://journals.jps.jp/doi/' + JournalInfo.group()

        return -1


class APL(PDFAnalyze):
    def __init__(self, path):
        super().__init__(path)

    def get_URL(self, layout):
        for l in layout:
            if isinstance(l, LTTextBoxHorizontal):
                JournalInfo = re.search(
                    r'http://dx.doi.org/\d+\.\d+/\d+\.\d+', l.get_text())
                if JournalInfo:
                    return JournalInfo.group()

        return -1


class URL:
    def __init__(self, path):
        self.path = path

    def DecideJournal(self):
        """
        Judge from which journal the paper is published. First this function search first page,
        next search last page, because in 'Science' the journal info is in the last page
        :return: String
        """
        layout = PDFAnalyze(self.path).get_PDFLayout(0)
        for l in layout:
            if isinstance(l, LTTextBoxHorizontal):
                if 'PhysRevLett' in l.get_text():
                    return 'PRL', layout
                if 'PhysRevB' in l.get_text():
                    return 'PRB', layout
                if 'RevModPhys' in l.get_text():
                    return 'RMP', layout
                if 'nature' in l.get_text():
                    return 'Nature', layout
                if 'JPSJ' in l.get_text():
                    return 'JPSJ', layout
        # TODO : search last page

        return -1

    def get_URL(self):
        """
        Judge what is the journal name and get URL of the paper
        :return: URL of the paper.
        """
        J, layout = self.DecideJournal()
        if J == "PRB" or J == "PRL" or J == "RMP":
            return PhysRev(self.path).get_URL(layout)

        if J == 'Nature':
            return Nature(self.path).get_URL(layout)

        if J == 'JPSJ':
            return JPSJ(self.path).get_URL(layout)

        return -1

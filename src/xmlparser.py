# coding: utf-8

from bs4 import BeautifulSoup
import re
import os

class XMLParser:
    def __init__(self, xml):
        self.xml = xml

    def parse(self):
        soup = BeautifulSoup(self.xml, 'xml')
        questions_and_answers = []
        chapters = soup.find_all('Chapitre')
        
        for chapter in chapters:
            question = chapter.find('Titre').find('Paragraphe').get_text().replace('\xa0', ' ')
            
            if question.endswith('?'):
                answer_paragraphs = chapter.find_all('Paragraphe')[1:]
                answer = ' '.join([p.get_text().replace('\xa0', ' ') for p in answer_paragraphs])

                if any(p.get_text().strip().endswith('?') for p in answer_paragraphs):
                    questions_and_answers.append((question, ''))

                    for p in answer_paragraphs:
                        if p.get_text().strip().endswith('?'):
                            questions = re.findall(r'\.\s*\w+\s*\?', p.get_text())
                            if questions:
                                for found_question in questions:
                                    questions_and_answers.append((found_question, p.get_text().replace('\xa0', ' ')))
                            else:
                                print("No questions found in paragraph:", p.get_text())
                        else:
                            questions_and_answers[-1] = (questions_and_answers[-1][0], questions_and_answers[-1][1] + ' ' + p.get_text().replace('\xa0', ' '))
                else:
                    questions_and_answers.append((question, answer))
                    
        return questions_and_answers


    def get_xml(self):
        return self.xml
    
    def set_xml(self, xml):
        self.xml = xml
    
    def import_xml(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

if __name__ == '__main__':
    xml_parser = XMLParser('')
    xml_doc = xml_parser.import_xml('../data/part/F32485.xml')
    xml_parser.set_xml(xml_doc)
    parsed_questions_and_answers = xml_parser.parse()
    print(parsed_questions_and_answers)



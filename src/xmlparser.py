# coding: utf-8
from bs4 import BeautifulSoup
import json
import re
## A AMELIORER 
class XMLParser:
    def __init__(self, xml, output_path=None):
        self.xml = xml
        self.parsed_data = None
        self.output_path = output_path

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
                    questions_and_answers.append({'question': question, 'response': ''})

                    for p in answer_paragraphs:
                        if p.get_text().strip().endswith('?'):
                            questions = re.findall(r'\.\s*\w+\s*\?', p.get_text())
                            if questions:
                                for found_question in questions:
                                    questions_and_answers.append({'question': found_question, 'response': p.get_text().replace('\xa0', ' ')})
                            else:
                                pass
                        else:
                            questions_and_answers[-1]['response'] += ' ' + p.get_text().replace('\xa0', ' ')
                else:
                    questions_and_answers.append({'question': question, 'response': answer})
                    
        self.parsed_data = questions_and_answers
        self.unique_data()

        return self.parsed_data


    def unique_data(self):
        unique_pairs = set()
        unique_data = []

        for pair in self.parsed_data:
            pair_tuple = (pair['question'], pair['response'])  # Convert dictionary to tuple
            if pair_tuple not in unique_pairs:
                unique_data.append(pair)
                unique_pairs.add(pair_tuple)
        self.parsed_data = unique_data


    def output_json(self):
        with open(self.output_path, 'w') as json_file:
            json.dump(self.parsed_data, json_file, indent=4, ensure_ascii=False)


    def get_xml(self):
        return self.xml
    
    def set_xml(self, xml):
        self.xml = xml
    

if __name__ == '__main__':
    pass



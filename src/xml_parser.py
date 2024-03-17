from bs4 import BeautifulSoup
import json
import re
# Très lent et degueulasse
class XMLParser:
    def __init__(self, xml):
        self.xml = xml
        self.parsed_data = []

    def parse(self) -> list[dict[str, str]]:
        soup = BeautifulSoup(self.xml, 'xml')
        chapters = soup.find_all('Chapitre')
        
        for chapter in chapters:
            question = chapter.find('Titre').find('Paragraphe').get_text().replace('\xa0', ' ')
            if question.endswith('?'):
                answer_paragraphs = chapter.find_all('Paragraphe')[1:]
                answer = ' '.join(p.get_text().replace('\xa0', ' ') for p in answer_paragraphs)

                if any(p.get_text().strip().endswith('?') for p in answer_paragraphs):
                    self.parsed_data.append({'question': question, 'response': ''})

                    for p in answer_paragraphs:
                        if p.get_text().strip().endswith('?'):
                            questions = re.findall(r'\.\s*\w+\s*\?', p.get_text())
                            if questions:
                                for found_question in questions:
                                    self.parsed_data.append({'question': found_question, 'response': p.get_text().replace('\xa0', ' ')})
                        else:
                            self.parsed_data[-1]['response'] += ' ' + p.get_text().replace('\xa0', ' ')
                else:
                    self.parsed_data.append({'question': question, 'response': answer})
                    
        self.unique_data()
        return self.parsed_data

    def unique_data(self):
        unique_pairs = set()
        unique_data = []

        for pair in self.parsed_data:
            pair_tuple = (pair['question'], pair['response'])
            if pair_tuple not in unique_pairs:
                unique_data.append(pair)
                unique_pairs.add(pair_tuple)
        self.parsed_data = unique_data


if __name__ == '__main__':
    pass

from bs4 import BeautifulSoup
import re

class XMLParser:
    def __init__(self, xml):
        self.xml = xml.encode('utf-8')

    def parse(self)-> list[dict]:
        soup = BeautifulSoup(self.xml, 'xml')
        chapters = soup.find_all('Chapitre')
        parsed_data = []
        seen_questions = set()

        for chapter in chapters:
            question = self.normalize_text(chapter.find('Titre').find('Paragraphe').get_text())
            if question.endswith('?') and question not in seen_questions:
                paragraphs = chapter.find_all('Paragraphe')[1:]
                answer = ' '.join(self.normalize_text(p.get_text()) for p in paragraphs)
                parsed_data.append({'question': question, 'response': answer})
                seen_questions.add(question)

        return parsed_data

    def normalize_text(self, text)-> str:
        return text.replace('\xa0', ' ').strip()

if __name__ == '__main__':
    pass

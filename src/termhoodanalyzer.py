import spacy
import json

class DataAnalyzer:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.data = self.load_json()
        self.nlp = spacy.load("fr_core_news_sm")
        self.all_text = []

    def load_json(self):
        with open(self.json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data

    def analyze_responses(self):
        for index, pair in enumerate(self.data):
            response = pair['response']
            question = pair['question']
            self.all_text.append(question)
            self.all_text.append(response)

    def compute_named_entities(self, output_file):
        named_entities = dict()
        for doc in self.nlp.pipe(self.all_text):
            for ent in doc.ents:
                named_entities.setdefault(ent.text, ent.label_)

        with open(output_file, 'w', encoding='utf-8') as file:
            for key, value in named_entities.items():
                if value not in ['LOC', 'MISC']:
                    file.write(f"{key}: {value}\n")

if __name__ == '__main__':
    json_file_path = '../data/results/output.json'
    analyzer = DataAnalyzer(json_file_path)
    analyzer.analyze_responses()
    analyzer.compute_named_entities('../data/analysis/named_entities.txt')

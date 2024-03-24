import spacy
import json
from spacy.lang.fr.stop_words import STOP_WORDS
from pathlib import Path

class NamedEntitiesAnalyzer:
    def __init__(self, data, fast: bool = True):
        self.data = data
        if fast:
            self.nlp = spacy.load('fr_core_news_sm', disable=["parser"])
        else:
            self.nlp = spacy.load('fr_dep_news_trf', disable=["parser"])
        self.stop_words = STOP_WORDS

    def load_text(self) -> list[str]:
        all_text = []
        for item in self.data:
            all_text.append(item['question'] + " " + item['response'])
        return all_text

    def compute_named_entities_and_lemmas(self, all_text: list[str]) -> dict:
        named_entities = {}
        lemmas_freq = {}
        for doc in self.nlp.pipe(all_text, batch_size=1000, n_process=-1):
            for ent in doc.ents:
                if ent.label_ not in named_entities:
                    named_entities[ent.text] = ent.label_

            for token in doc:
                if not token.is_stop and not token.is_punct and token.lemma_.lower() not in self.stop_words:
                    lemmas = lemmas_freq.get(token.lemma_.lower(), {})
                    lemmas['freq'] = lemmas.get('freq', 0) + 1
                    lemmas['pos'] = token.pos_
                    lemmas_freq[token.lemma_.lower()] = lemmas

        return {'entities': named_entities, 'lemmas': lemmas_freq}

    def analyze_data(self):
        all_text = self.load_text()
        analysis_results = self.compute_named_entities_and_lemmas(all_text)
        return analysis_results

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    data_location = absolute_file_dir / "../data/results/output.json"
    results_location = absolute_file_dir / "../data/results/analysis_results.json"
    data = json.load(open(data_location, 'r', encoding='utf-8'))

    analyzer = NamedEntitiesAnalyzer(data, fast=False)
    results = analyzer.analyze_data()
    with open(results_location, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

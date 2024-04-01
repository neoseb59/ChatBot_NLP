import json
from spacy.lang.fr.stop_words import STOP_WORDS
from pathlib import Path
from spacy.tokens import Doc
from token_tagger import TokenTagger

class NamedEntitiesAnalyzer:

    def __init__(self, docs: dict[str, list[Doc]]):
        self.docs = docs
        self.stop_words = STOP_WORDS

    def run(self) -> dict[str, dict[str, str]]:
        print("[Named Entities Analyzer] Computing named entities and lemmas...")
        named_entities = {}
        lemmas_freq = {}
        all_docs = self.docs['question'] + self.docs['response']
        for doc in all_docs:
            for ent in doc.ents:
                named_entities[ent.text] = ent.label_

            for token in doc:
                if not token.is_stop and not token.is_punct and token.lemma_.lower() not in self.stop_words:
                    lemmas = lemmas_freq.get(token.lemma_.lower(), {})
                    lemmas['freq'] = lemmas.get('freq', 0) + 1
                    lemmas['pos'] = token.pos_
                    lemmas_freq[token.lemma_.lower()] = lemmas

        return { 'entities': named_entities, 'lemmas': lemmas_freq }

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    data_location = absolute_file_dir.parent / "data/results/Argent_Impôts_Consommation/output.json"
    with open(data_location, 'r', encoding='utf-8') as file:
        data = json.load(file)

    tagger = TokenTagger(data, fast=True)
    tagger.run()

    analyzer = NamedEntitiesAnalyzer(tagger.docs)
    result = analyzer.run()

    for entity, label in result['entities'].items():
        print(entity, label)

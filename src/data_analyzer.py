import spacy
import json
from spacy.lang.fr.stop_words import STOP_WORDS

class DataAnalyzer:
    def __init__(self, data, fast : bool = True):
        self.data = data
        self.stop_words = STOP_WORDS
        if fast:
            self.nlp = spacy.load('fr_core_news_sm', disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"])
        else:
            self.nlp = spacy.load('fr_dep_news_trf', disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"])

    def load_text(self)-> list[str]:
        all_text = []
        for index, pair in enumerate(self.data):
            response = pair['response']
            question = pair['question']
            all_text.append(question)
            all_text.append(response)
        return all_text

    def compute_named_entities(self, all_text: list[str])-> dict[str, str]:
        named_entities = dict()
        for doc in self.nlp.pipe(all_text, batch_size=1000, n_process=-1):
            for ent in doc.ents:
                if ent.text.lower() not in self.stop_words:
                    named_entities.setdefault(ent.text, ent.label_)
        return named_entities

    def analyze_data_into_named_entities(self):
        all_text = self.load_text()
        named_entities = self.compute_named_entities(all_text)
        return named_entities


if __name__ == '__main__':
    pass

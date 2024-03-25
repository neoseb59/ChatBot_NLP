import json
import spacy
from pathlib import Path

class TermhoodAnalyzer:
    def __init__(self, data: list[dict[str, str]]):
        self.data = data
        self.corpus = self._create_corpus()
        self.tagged_words = {}  # response (as element from corpus) indexing: List[] of TaggedWord objects
        self.candidates = []  # list of potential terms to run the C value algorithm on

    def _create_corpus(self) -> list[str]:
        return [pair['response'] for pair in self.data]

    def tag_all_words(self):
        nlp = spacy.load('fr_core_news_sm')
        for response in self.corpus:
            tagged_response_words = []
            for token in nlp(response):
                tagged_response_words.append(TaggedWord(token.text, token.tag_))
            self.tagged_words[response] = tagged_response_words

    def find_term_candidates(self):
        for response in self.corpus:
            candidate = ""  # replace with dedicated state machine
            for tagged_word in self.tagged_words[response]:
                pass

class TaggedWord:
    def __init__(self, word: str, tag: str):
        self.word = word
        self.tag = tag

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    data_location = absolute_file_dir.parent / "data/results/Social_Santé/output.json"
    with open(data_location, 'r', encoding='utf-8') as file:
        data = json.load(file)

    tagger = TermhoodAnalyzer(data)
    tagger.tag_all_words()
    tagger.find_term_candidates()

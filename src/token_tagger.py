import json
import spacy
import re
from pathlib import Path
from tqdm import tqdm

class TokenTagger:

    curation_replacements_regex = [  # replacement operations to be performed when building the corpus itself
        { 'regex': re.compile(r"’"), 'replacement': r"'" },  # typographic apostrophe
        { 'regex': re.compile(r" "), 'replacement': r" " },  # no-break space
        { 'regex': re.compile(r"(N|n)°"), 'replacement': r"\1uméro" },
        { 'regex': re.compile(r"([0-9]+)h"), 'replacement': r"\1 h" },
    ]

    def __init__(self, data: list[dict[str, str]], fast: bool = False):
        self.nlp = spacy.load('fr_core_news_sm' if fast else 'fr_dep_news_trf')
        self.corpus = [{ 'question': self._curate_string(pair['question']), 'response': self._curate_string(pair['response']) } for pair in data]
        self.questions = []
        self.responses = []
        self.number_of_pairs = 0
        for faq_pair in self.corpus:
            self.questions.append(self._curate_string(faq_pair['question']))
            self.responses.append(self._curate_string(faq_pair['response']))
            self.number_of_pairs += 1
        self.docs = { 'question': [], 'response': [] }  # run the run() method to fill this in (result of running slf.nlp.pipe() on the list of questions and the list of results)
        self.tagged_corpus = [{ 'question': [], 'response': [] } for i in range(self.number_of_pairs)]  # run the run() method to fill this (actual tokens for each word in order, same format as input data)

    def _curate_string(self, string: str) -> str:
        curated_string = string
        for replacement_dict in self.curation_replacements_regex:
            curated_string = replacement_dict['regex'].sub(replacement_dict['replacement'], curated_string)
        return curated_string

    def run(self):
        print("Tagging questions in corpus...")
        for i, doc in tqdm(enumerate(self.nlp.pipe(self.questions)), total=len(self.questions), miniters=1):
            self.docs['question'].append(doc)
            for token in doc:
                self.tagged_corpus[i]['question'].append(token)
        print("Tagging responses in corpus...")
        for i, doc in tqdm(enumerate(self.nlp.pipe(self.responses)), total=len(self.responses), miniters=1):
            self.docs['response'].append(doc)
            for token in doc:
                self.tagged_corpus[i]['response'].append(token)

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    data_location = absolute_file_dir.parent / "data/results/Argent_Impôts_Consommation/output.json"
    with open(data_location, 'r', encoding='utf-8') as file:
        data = json.load(file)

    tagger = TokenTagger(data, fast=True)
    tagger.run()

    for pair in tagger.tagged_corpus:
        for token in pair['question'] + pair['response']:
            print(token.text, token.tag_)

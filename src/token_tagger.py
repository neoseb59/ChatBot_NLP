import json
import spacy
import re
from pathlib import Path
from tqdm import tqdm

class TokenTagger:

    curation_replacements_regex = [  # replacement operations to be performed when building the corpus itself
        { 'regex': re.compile(r"’"), 'replacement': r"'" },
        { 'regex': re.compile(r"(N|n)°"), 'replacement': r"\1uméro" },
        { 'regex': re.compile(r"([0-9]+)h"), 'replacement': r"\1 h" },
    ]

    def __init__(self, data: list[dict[str, str]], fast: bool = False):
        self.nlp = spacy.load('fr_core_news_sm' if fast else 'fr_dep_news_trf')
        self.corpus = [{'question': self.curate_string(pair['question']), 'response': self.curate_string(pair['response'])} for pair in data]
        self.questions = []
        self.responses = []
        self.number_of_pairs = 0
        for faq_pair in self.corpus:
            self.questions.append(self.curate_string(faq_pair['question']))
            self.responses.append(self.curate_string(faq_pair['response']))
            self.number_of_pairs += 1
        self.tagged_corpus = [{} for i in range(self.number_of_pairs)]  # run the run() method to fill this

    def curate_string(self, string: str):
        curated_string = string
        for replacement_dict in self.curation_replacements_regex:
            curated_string = replacement_dict['regex'].sub(replacement_dict['replacement'], curated_string)
        return curated_string

    def run(self):
        print("Tagging words in corpus...")
        for i in tqdm(range(self.number_of_pairs)):
            self.tagged_corpus[i]['question'] = [TaggedWord(token) for token in self.nlp(self.questions[i])]
            self.tagged_corpus[i]['response'] = [TaggedWord(token) for token in self.nlp(self.responses[i])]

class TaggedWord:

    def __init__(self, token):
        self.text = token.text
        self.lemma = token.lemma_
        self.tag = token.tag_
        morph = str(token.morph)
        self.gender = "Und_Gender"
        self.number = "Und_Number"
        for category in morph.split('|'):
            pair = category.split('=')
            if len(pair) != 2:
                continue
            if pair[0] == "Gender":
                self.gender = pair[1]
            elif pair[0] == "Number":
                self.number = pair[1]

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    data_location = absolute_file_dir.parent / "data/results/Argent_Impôts_Consommation/output.json"
    with open(data_location, 'r', encoding='utf-8') as file:
        data = json.load(file)

    tagger = TokenTagger(data, fast=True)
    tagger.run()

    for pair in tagger.tagged_corpus:
        for token in pair['question'] + pair['response']:
            print(token.text, token.tag)

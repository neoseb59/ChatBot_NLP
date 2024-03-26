import json
import spacy
import re
import numpy as np
from enum import Enum
from pathlib import Path
from tqdm import tqdm

class TermhoodAnalyzer:

    curation_replacements_regex = [  # replacement operations to be performed when building the corpus itself
        { 'regex': re.compile(r"’"), 'replacement': r"'" },
        { 'regex': re.compile(r"(N|n)°"), 'replacement': r"\1uméro" },
        { 'regex': re.compile(r"([0-9]+)h"), 'replacement': r"\1 h" },
    ]

    bad_words_regex = [  # if any word in a term matches any of these regex, that term will be disregarded (abort recognition)
        re.compile(r"[€%«»/0-9]"),
        re.compile(r"^[;:\?!-]$"),
    ]

    def __init__(self, data: list[dict[str, str]]):
        self.data = data
        self.corpus = self._create_corpus()
        self.tagged_words = {}  # response (as string element from corpus) indexing: List[] of TaggedWord objects
        self.candidate_lemma_mappings = {}
        self.candidate_lemmas = []
        self.candidate_lemmas_set = set()
        self.term_frequencies = {}  # candidate indexing: int (giving that term's number of occurrences in the corpus)
        self.super_terms = {}  # candidate indexing: List[] of all candidates (terms) that contain that candidate
        self.c_values = {}  # candidate indexing: float (giving that term's C-value)

        self.nlp = spacy.load('fr_core_news_sm')  # runs quite fast but will sometimes tag inaccurately
        # self.nlp = spacy.load('fr_dep_news_trf')  # tags more accurately but runs slower

    def check_bad_word(self, word: str):
        for regex in self.bad_words_regex:
            if regex.match(word):
                return True
        return False

    def curate_string(self, string: str):
        curated_string = string
        for replacement_dict in self.curation_replacements_regex:
            curated_string = replacement_dict['regex'].sub(replacement_dict['replacement'], curated_string)
        return curated_string

    def full_text(self, lemma: str):
        return self.candidate_lemma_mappings[lemma].text

    def _create_corpus(self) -> list[str]:
        return [self.curate_string(pair['response']) for pair in self.data]

    def tag_all_tokens(self):
        print("Tagging words in corpus...")
        for response in tqdm(self.corpus):
            tagged_response_words = []
            for token in self.nlp(response):
                tagged_response_words.append(TaggedWord(token.text, token.lemma_.lower(), token.tag_))
            self.tagged_words[response] = tagged_response_words

    def find_term_candidates(self):
        detector = CandidateAutomaton()
        print("Searching for terms...")
        for response in self.corpus:
            detector.reset()
            for tagged_word in self.tagged_words[response]:
                if self.check_bad_word(tagged_word.text):
                    detector.reset()
                    continue
                detector.transition(tagged_word)
                if detector.result is not None:
                    if detector.result is True:
                        new_candidate = TermCandidate(detector.buffer)
                        self.candidate_lemma_mappings[new_candidate.lemma] = new_candidate
                        self.candidate_lemmas.append(new_candidate.lemma)
                        self.candidate_lemmas_set.add(new_candidate.lemma)
                    detector.reset()
                    detector.transition(tagged_word)

    def calculate_frequencies(self):
        for c in self.candidate_lemmas:
            if c not in self.term_frequencies.keys():
                self.term_frequencies[c] = 0
            self.term_frequencies[c] += 1

    def work_out_super_terms(self):
        for c in self.candidate_lemmas_set:
            if c not in self.super_terms.keys():
                self.super_terms[c] = []
            for super_term_candidate in self.candidate_lemmas_set:
                if c in super_term_candidate:
                    self.super_terms[c].append(super_term_candidate)

    def compute_c_values(self):
        for a in self.candidate_lemmas_set:
            self.c_values[a] = np.log2(len(a))
            if a in self.super_terms.keys() and len(self.super_terms[a]) > 0:
                self.c_values[a] *= self.term_frequencies[a] - ((1/len(self.super_terms[a])) * sum([self.term_frequencies[b] for b in self.super_terms[a]]))
            else:
                self.c_values[a] *= self.term_frequencies[a]

class TaggedWord:

    def __init__(self, word: str, lemma: str, tag: str):
        self.text = word
        self.lemma = lemma
        self.tag = tag

class TermCandidate:

    def __init__(self, tagged_words: list[TaggedWord]):
        self.tagged_words = tagged_words
        self.lemma = " ".join([tw.text for tw in self.tagged_words])
        self.text = " ".join([tw.text for tw in self.tagged_words])
        self.text = self.text.replace("' ", "'")  # special case of apostrophes

class CandidateAutomaton:

    class State(Enum):
        none = 0
        NOUN = 1
        ADJ = 2
        ADP = 3
        DET = 4
        NOUN2 = 5

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = self.State.none
        self.result = None
        self.buffer = []

    def transition(self, token: TaggedWord):
        if self.state == self.State.none:
            if token.tag == "NOUN":
                self.state = self.State.NOUN
                self.buffer.append(token)
        elif self.state == self.State.NOUN:
            if token.tag == "ADJ":
                self.state = self.State.ADJ
                self.buffer.append(token)
            elif token.tag == "ADP":
                self.state = self.State.ADP
                self.buffer.append(token)
            else:
                self.result = False
        elif self.state == self.State.ADJ:
            if token.tag != "ADJ":
                self.result = True
            else:
                self.buffer.append(token)
        elif self.state == self.State.ADP:
            if token.tag == "DET":
                self.state = self.State.DET
                self.buffer.append(token)
            elif token.tag == "NOUN":
                self.state = self.State.NOUN2
                self.buffer.append(token)
            else:
                self.result = False
        elif self.state == self.State.DET:
            if token.tag == "NOUN":
                self.state = self.State.NOUN2
                self.buffer.append(token)
            else:
                self.result = False
        elif self.state == self.State.NOUN2:
            self.result = True

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    data_location = absolute_file_dir.parent / "data/results/Argent_Impôts_Consommation/output.json"
    with open(data_location, 'r', encoding='utf-8') as file:
        data = json.load(file)

    tagger = TermhoodAnalyzer(data)
    tagger.tag_all_tokens()
    tagger.find_term_candidates()
    tagger.calculate_frequencies()
    tagger.work_out_super_terms()
    tagger.compute_c_values()

    threshold = 0
    for lemma, c_value in tagger.c_values.items():
        if c_value > threshold:
            print(tagger.full_text(lemma), c_value)

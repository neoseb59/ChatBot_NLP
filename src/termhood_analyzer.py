import json
import re
import numpy as np
from spacy.tokens import Token
from enum import Enum
from pathlib import Path
from token_tagger import TokenTagger

class TermhoodAnalyzer:

    bad_words_regex = [  # if any word in a term matches any of these regex, that term will be disregarded (abort recognition)
        re.compile(r"[€%«»/0-9]"),
        re.compile(r"^[;:\?!-]$"),
    ]

    def __init__(self, tagged_corpus: list[dict[str, list[Token]]]):
        self.tagged_corpus = tagged_corpus
        self.term_lemma_mappings = {}
        self.candidate_lemmas = []  # term candidates in responses
        self.candidate_lemmas_set = set()  # term candidates in responses (without duplicates)
        self.term_frequencies = {}  # candidate (lemma) indexing: int (giving that term's number of occurrences in the corpus)
        self.super_terms = {}  # candidate (lemma) indexing: List[] of all candidates (terms) that contain that candidate
        self.c_values = {}  # candidate (full) indexing: float (giving that term's C-value)

    def _check_bad_word(self, word: str) -> bool:
        for regex in self.bad_words_regex:
            if regex.match(word):
                return True
        return False

    def _get_full_term(self, lemma: str) -> str:
        return self.term_lemma_mappings[lemma].text

    def find_term_candidates(self):
        detector = CandidateAutomaton()
        for pair in self.tagged_corpus:
            response_tokens = pair['response']
            detector.reset()
            for token in response_tokens:
                if self._check_bad_word(token.text):
                    detector.reset()
                    continue
                detector.transition(token)
                if detector.result is not None:
                    if detector.result is True:
                        new_candidate = TermCandidate(detector.buffer)
                        self.term_lemma_mappings[new_candidate.lemma] = new_candidate
                        self.candidate_lemmas.append(new_candidate.lemma)
                        self.candidate_lemmas_set.add(new_candidate.lemma)
                    detector.reset()
                    detector.transition(token)

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
            full_a = self._get_full_term(a)
            self.c_values[full_a] = np.log2(len(a))
            if a in self.super_terms.keys() and len(self.super_terms[a]) > 0:
                self.c_values[full_a] *= self.term_frequencies[a] - ((1/len(self.super_terms[a])) * sum([self.term_frequencies[b] for b in self.super_terms[a]]))
            else:
                self.c_values[full_a] *= self.term_frequencies[a]

    def run(self) -> dict[str, float]:
        print("Searching for terms...")
        self.find_term_candidates()
        self.calculate_frequencies()
        self.work_out_super_terms()
        self.compute_c_values()
        return self.c_values

class TermCandidate:

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.lemma = " ".join([tw.lemma_ for tw in self.tokens])
        self.text = " ".join([tw.text for tw in self.tokens])
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

    def transition(self, token: Token):
        if self.state == self.State.none:
            if token.tag_ == "NOUN":
                self.state = self.State.NOUN
                self.buffer.append(token)
        elif self.state == self.State.NOUN:
            if token.tag_ == "ADJ":
                self.state = self.State.ADJ
                self.buffer.append(token)
            elif token.tag_ == "ADP":
                self.state = self.State.ADP
                self.buffer.append(token)
            else:
                self.result = False
        elif self.state == self.State.ADJ:
            if token.tag_ != "ADJ":
                self.result = True
            else:
                self.buffer.append(token)
        elif self.state == self.State.ADP:
            if token.tag_ == "DET":
                self.state = self.State.DET
                self.buffer.append(token)
            elif token.tag_ == "NOUN":
                self.state = self.State.NOUN2
                self.buffer.append(token)
            else:
                self.result = False
        elif self.state == self.State.DET:
            if token.tag_ == "NOUN":
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

    tagger = TokenTagger(data, fast=True)
    tagger.run()

    analyzer = TermhoodAnalyzer(tagger.tagged_corpus)
    results = analyzer.run()

    threshold = 0
    for term, c_value in results.items():
        if c_value > threshold:
            print(term, c_value)

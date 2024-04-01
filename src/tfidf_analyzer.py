import json
import numpy as np
from pathlib import Path
from token_tagger import TokenTagger
from termhood_analyzer import TermhoodAnalyzer

class TfidfAnalyzer:

    def __init__(self, corpus: list[dict[str, str]], terms: set[str]):
        self.corpus = corpus
        self.terms = terms
        self.document_frequencies = self.find_document_frequencies()

    def find_document_frequencies(self):
        document_frequencies = {}
        for term in self.terms:
            document_frequency = 0
            for response in [pair['response'] for pair in self.corpus]:
                if term in response:
                    document_frequency += 1
            document_frequencies[term] = document_frequency
        return document_frequencies

    def run(self) -> dict[str, dict[str, float]]:
        print("[TF-IDF Analyzer] Computing TF-IDF scores...")
        all_feature_scores = {}
        for response in [pair['response'] for pair in self.corpus]:
            feature_scores = {}
            terms_in_response = 0
            for any_term in self.terms:
                terms_in_response += response.count(any_term)
            for term in self.terms:
                if self.document_frequencies[term] > 0 and terms_in_response > 0:
                    term_frequency = response.count(term) / terms_in_response
                    inverse_document_frequency = np.log(len(self.corpus) / self.document_frequencies[term])
                    feature_scores[term] = term_frequency * inverse_document_frequency
                else:
                    feature_scores[term] = 0
            all_feature_scores[response] = feature_scores
        return all_feature_scores

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    data_location = absolute_file_dir.parent / "data/results/Argent_Impôts_Consommation/output.json"
    with open(data_location, 'r', encoding='utf-8') as file:
        data = json.load(file)

    tagger = TokenTagger(data, fast=True)
    tagger.run()

    th_analyzer = TermhoodAnalyzer(tagger.tagged_corpus)
    th_results = th_analyzer.run()

    terms = set()
    th_threshold = 0
    for term, c_value in th_results.items():
        if c_value > th_threshold:
            terms.add(term)

    analyzer = TfidfAnalyzer(tagger.corpus, terms)
    result = analyzer.run()
    threshold = 0
    for response, scores in result.items():
        for term, tfidf in scores.items():
            if tfidf > threshold:
                print(term, tfidf)

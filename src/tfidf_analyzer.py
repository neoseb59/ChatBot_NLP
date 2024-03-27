import json
import numpy as np
from pathlib import Path
from tqdm import tqdm
from token_tagger import TokenTagger
from termhood_analyzer import TermhoodAnalyzer

class TfidfAnalyzer:

    def __init__(self, corpus: list[dict[str, str]], terms: list[str], document_frequencies: dict[str, int]):
        self.corpus = corpus
        self.terms = terms
        self.document_frequencies = document_frequencies

    def run(self) -> dict[str, dict[str, float]]:
        print("Computing TF-IDF scores...")
        all_feature_scores = {}
        for response in tqdm([pair['response'] for pair in self.corpus], total=len(self.corpus)):
            feature_scores = {}
            terms_in_response = 0
            for any_term in self.terms:
                terms_in_response += response.count(any_term)
            for term in self.terms:
                if terms_in_response > 0:
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

    terms = []
    th_threshold = 0
    for term, c_value in th_results.items():
        if c_value > th_threshold:
            terms.append(term)

    document_frequencies = {}
    for term, frequency in th_analyzer.term_frequencies.items():
        document_frequencies[th_analyzer.get_full_term(term)] = frequency

    analyzer = TfidfAnalyzer(tagger.corpus, terms, document_frequencies)
    result = analyzer.run()
    threshold = 0
    for response, scores in result.items():
        for term, tfidf in scores.items():
            if tfidf > threshold:
                print(term, tfidf)

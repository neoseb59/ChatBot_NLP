import math
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

class TFIDFAnalyzer:
    def __init__(self, data: list[dict[str, str]]):
        self.data = data
        self.vectorizer = TfidfVectorizer(stop_words=stopwords.words('french'))
        self._build_tfidf_matrix()

    def _get_text(self):
        all_text = ""
        for pair in self.data:
            all_text += pair['question'] + " " + pair['response'] + " "
        return all_text


    def _build_tfidf_matrix(self):
        corpus = [self._get_text()]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def get_tfidf_scores(self)->dict[str, float]:
        features = self.vectorizer.get_feature_names_out()
        feature_scores = defaultdict(float)
        doc_scores = self.tfidf_matrix[0].toarray().flatten()
        for feature_index, score in enumerate(doc_scores):
            if score > 0:
                feature_scores[features[feature_index]] = score
        return feature_scores

    def get_top_keywords(self, top_n:int=5)->list[tuple[str, float]]:
        tfidf_scores = self.get_tfidf_scores()
        sorted_scores = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_n]

if __name__ == '__main__':
    pass
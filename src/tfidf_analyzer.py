from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import json
from scipy.sparse import csr_matrix
from pathlib import Path
from tqdm import tqdm

class TFIDFAnalyzer:
    def __init__(self, data: list[dict[str, str]]):
        self.data = data
        self.vectorizer = TfidfVectorizer(stop_words=stopwords.words('french'), max_features=20000)
        self.corpus = self._create_corpus()
        self._build_tfidf_matrix()
        self._tfidf_scores = None

    def _create_corpus(self) -> list[str]:
        return [pair['response'] for pair in self.data]

    def _build_tfidf_matrix(self):
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def get_tfidf_scores(self) -> dict[str, float]:
        if self._tfidf_scores is not None:
            return self._tfidf_scores

        feature_scores = {}
        summed_matrix = self.tfidf_matrix.sum(axis=0)
        scores = csr_matrix(summed_matrix).toarray().flatten()

        for index, score in tqdm(enumerate(scores), total=scores.size):
            feature = self.vectorizer.get_feature_names_out()[index]
            feature_scores[feature] = score

        self._tfidf_scores = feature_scores
        return feature_scores

    def get_top_keywords(self, top_n=5) -> list[tuple[str, float]]:
        tfidf_scores = self.get_tfidf_scores()
        sorted_scores = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_n]

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    data_location = absolute_file_dir.parent / "data/results/Social_Santé/output.json"
    with open(data_location, 'r', encoding='utf-8') as file:
        data = json.load(file)

    analyzer = TFIDFAnalyzer(data)
    top_keywords = analyzer.get_top_keywords(10)
    print("Top TF-IDF Keywords:")
    for word, score in top_keywords:
        print(f"{word}: {score}")

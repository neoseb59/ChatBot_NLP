import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

class DataVisualizer:
    def __init__(self, analysis_results):
        self.analysis_results = analysis_results

    def plot_named_entities_distribution(self):
        entities = [ent for ent in self.analysis_results['entities'].values()]
        entities = entities[:3]
        plt.figure(figsize=(10, 6))
        sns.countplot(y=entities, order = sns.countplot(y=entities).get_xticklabels())
        plt.title('Named Entities Distribution')
        plt.xlabel('Count')
        plt.ylabel('Entity Type')
        plt.show()

    def plot_top_lemmas(self, top_n=20):
        lemmas_freq = {lemma: details['freq'] for lemma, details in self.analysis_results['lemmas'].items()}
        top_lemmas = sorted(lemmas_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        plt.figure(figsize=(10, 8))
        sns.barplot(x=[item[1] for item in top_lemmas], y=[item[0] for item in top_lemmas])
        plt.title(f'Top {top_n} Lemmas')
        plt.xlabel('Frequency')
        plt.ylabel('Lemma')
        plt.show()

    def generate_wordcloud(self):
        wordcloud_text = ' '.join([f"{lemma} " * details['freq'] for lemma, details in self.analysis_results['lemmas'].items()])
        wordcloud = WordCloud(width=800, height=400, background_color ='white').generate(wordcloud_text)
        
        plt.figure(figsize=(10, 7), facecolor=None)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.show()
        
def plot_top_tfidf_scores(self, top_n=20):
        if 'tfidf_scores' not in self.analysis_results:
            print("TF-IDF scores are not available in the analysis results.")
            return

        tfidf_scores = self.analysis_results['tfidf_scores']
        top_tfidf = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

        plt.figure(figsize=(10, 8))
        sns.barplot(x=[score for _, score in top_tfidf], y=[term for term, _ in top_tfidf])
        plt.title(f'Top {top_n} TF-IDF Scores')
        plt.xlabel('TF-IDF Score')
        plt.ylabel('Terms')
        plt.show()

if __name__ == '__main__':
    analysis_results = {
        'entities': {'Paris': 'LOC', 'France': 'LOC', 'Python': 'MISC', '2021': 'DATE'},
        'lemmas': {'learn': {'freq': 10, 'pos': 'VERB'}, 'python': {'freq': 5, 'pos': 'NOUN'}},
        'tfidf_scores': {'python': 1.2, 'learn': 1.1, 'programming': 1.05, 'course': 1.0}
    }
    visualizer = DataVisualizer(analysis_results)
    visualizer.plot_named_entities_distribution()
    visualizer.plot_top_lemmas()
    visualizer.generate_wordcloud()
    visualizer.plot_top_tfidf_scores()
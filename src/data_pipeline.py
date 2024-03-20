import os
import json
import time
from named_entities_analyzer import NamedEntitiesAnalyzer
from data_visualizer import DataVisualizer
import xml_loader
import xml_parser
import tfidf_analyzer

class DataPipeline:
    def __init__(self, data_folder, output_path, analysis_output_path, tfidf_output_path):
        self.data_folder = data_folder
        self.parsing_output_path = output_path
        self.analysis_output_path = analysis_output_path
        self.tfidf_output_path = tfidf_output_path

    def load_and_parse_xml(self) -> list[dict[str, str]]:
        print("Loading XML files from", self.data_folder)
        output_data = []
        for filename in os.listdir(self.data_folder):
            if filename.endswith(".xml"):
                file_path = os.path.join(self.data_folder, filename)
                loader = xml_loader.XMLloader(file_path)
                xml_data = loader.load()

                parser = xml_parser.XMLParser(xml_data)
                parsed_data = parser.parse()
                output_data.extend(parsed_data)
        return output_data

    def save_parsed_data(self, output_data: list[dict[str, str]]):
        with open(self.parsing_output_path, 'w', encoding='utf-8') as output_file:
            json.dump(output_data, output_file, ensure_ascii=False, indent=4)

    def analyze_data(self, output_data: list[dict[str, str]]):
        print("Analyzing data...")
        analyzer = NamedEntitiesAnalyzer(output_data)
        analysis_results = analyzer.analyze_data()
        # Save analysis results for potential future use
        with open(self.analysis_output_path, 'w', encoding='utf-8') as file:
            json.dump(analysis_results, file, ensure_ascii=False, indent=4)
        return analysis_results

    def visualize_analysis_results(self, analysis_results):
        print("Visualizing analysis results...")
        visualizer = DataVisualizer(analysis_results)
        visualizer.plot_named_entities_distribution()
        visualizer.plot_top_lemmas(20)
        visualizer.generate_wordcloud()

    def run_pipeline(self):
        start_time = time.time()

        # Load and save parsed XML data
        print("Running data pipeline...")
        output_data = self.load_and_parse_xml()
        self.save_parsed_data(output_data)

        # Analyze data for named entities and lemmas
        analysis_results = self.analyze_data(output_data)

        # Visualize analysis results
        self.visualize_analysis_results(analysis_results)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Pipeline completed in {:.2f} seconds.".format(elapsed_time))

if __name__ == '__main__':
    data_folder = '../data/part/'
    output_json_path = '../data/results/output.json'
    analysis_output_path = '../data/analysis/analysis_results.json'
    tfidf_output_path = '../data/analysis/tfidf_scores.txt'

    # Run the data pipeline
    pipeline = DataPipeline(data_folder, output_json_path, analysis_output_path, tfidf_output_path)
    pipeline.run_pipeline()

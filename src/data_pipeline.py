import os
from pathlib import Path
import json
import time
from named_entities_analyzer import NamedEntitiesAnalyzer
from data_visualizer import DataVisualizer
import xml_loader
import xml_parser
import tfidf_analyzer
from tqdm import tqdm

class DataPipeline:
    def __init__(self, base_data_folder, base_output_folder):
        self.base_data_folder = base_data_folder
        self.base_output_folder = base_output_folder

    def set_paths_for_theme(self, theme_name):
        self.data_folder = self.base_data_folder / theme_name
        theme_output_folder = self.base_output_folder / theme_name
        os.makedirs(theme_output_folder, exist_ok=True)
        self.parsing_output_path = theme_output_folder / 'output.json'
        self.analysis_output_path = theme_output_folder / 'analysis_results.json'
        self.tfidf_output_path = theme_output_folder / 'tfidf_scores.txt'

    def load_and_parse_xml(self) -> list[dict[str, str]]:
        print("Loading XML files from", self.data_folder)
        output_data = []
        files = os.listdir(self.data_folder)
        for filename in tqdm(files, total=len(files)):
            if filename.endswith(".xml"):
                file_path = self.data_folder / filename
                loader = xml_loader.XMLloader(file_path)
                xml_data = loader.load()

                parser = xml_parser.XMLParser(xml_data)
                parsed_data = parser.parse()
                output_data.extend(parsed_data)
        return output_data

    def save_parsed_data(self, output_data: list[dict[str, str]]):
        with open(self.parsing_output_path, 'w', encoding='utf-8') as output_file:
            json.dump(output_data, output_file, ensure_ascii=False, indent=4)

    def get_tfidf_scores(self, output_data: list[dict[str, str]]):
        print("Computing TF-IDF scores...")
        analyzer = tfidf_analyzer.TfidfAnalyzer(output_data)
        top_keywords = analyzer.get_top_keywords(10)
        return top_keywords
    
    def save_tfidf_scores(self, top_keywords):
        print("Saving TF-IDF scores...")
        with open(self.tfidf_output_path, 'w', encoding='utf-8') as file:
            for word, score in top_keywords:
                file.write(f"{word}: {score}\n")

    def run_pipeline_for_theme(self, theme_name):
        self.set_paths_for_theme(theme_name)
        start_time = time.time()

        print("Running data pipeline for theme:", theme_name)
        output_data = self.load_and_parse_xml()
        self.save_parsed_data(output_data)
        if not output_data:
            print("No data found for theme", theme_name)
            return
        top_keywords = self.get_tfidf_scores(output_data)
        self.save_tfidf_scores(top_keywords)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Pipeline for theme '{}' completed in {:.2f} seconds.".format(theme_name, elapsed_time))

    def run(self):
        themes = [theme for theme in os.listdir(self.base_data_folder) if os.path.isdir(self.base_data_folder / theme)]
        for theme in themes:
            self.run_pipeline_for_theme(theme)

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    base_data_folder = absolute_file_dir.parent / "data/themes"
    base_output_folder = absolute_file_dir.parent / "data/results"
    pipeline = DataPipeline(base_data_folder, base_output_folder)
    pipeline.run()

import os
import json
import time
from data_analyzer import DataAnalyzer
import xml_parser
import xml_loader
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

    def get_named_entities(self, parsed_data: list[dict[str, str]]) -> dict[str, str]:
        analyzer = DataAnalyzer(parsed_data)
        return analyzer.analyze_data_into_named_entities()

    def save_named_entities(self, named_entities: dict[str, str]):
        with open(self.analysis_output_path, 'w', encoding='utf-8') as output_file:
            for entity, label in named_entities.items():
                output_file.write(f"{entity} : {label}\n")

    def get_tfidf_keywords(self, parsed_data: list[dict[str, str]]) -> list[tuple[str, float]]:
        analyzer = tfidf_analyzer.TFIDFAnalyzer(parsed_data)
        return analyzer.get_top_keywords()

    def save_tfidf_keywords(self, tfidf_keywords: list[tuple[str, float]]):
        with open(self.tfidf_output_path, 'w', encoding='utf-8') as output_file:
            for keyword, score in tfidf_keywords:
                output_file.write(f"{keyword} : {score}\n")

    def run_pipeline(self):
        start_time = time.time()

        print("Running data pipeline...")
        load_start_time = time.time()
        output_data = self.load_and_parse_xml()
        load_end_time = time.time()
        load_elapsed_time = load_end_time - load_start_time
        print("Loading XML files took {:.2f} seconds.".format(load_elapsed_time))

        print("Saving parsed data...")
        save_start_time = time.time()
        self.save_parsed_data(output_data)
        save_end_time = time.time()
        save_elapsed_time = save_end_time - save_start_time
        print("Saving parsed data took {:.2f} seconds.".format(save_elapsed_time))

        # print("Analyzing data...")
        # analysis_start_time = time.time()
        # named_entities = self.get_named_entities(output_data)
        # analysis_end_time = time.time()
        # analysis_elapsed_time = analysis_end_time - analysis_start_time
        # print("Analyzing data took {:.2f} seconds.".format(analysis_elapsed_time))
        
        # print("Saving analysis data...")
        # save_analysis_start_time = time.time()
        # self.save_named_entities(named_entities)
        # save_analysis_end_time = time.time()
        # analysis_elapsed_time = save_analysis_end_time - save_analysis_start_time
        # print("Saving analysis data took {:.2f} seconds.".format(analysis_elapsed_time))

        print("TF-IDF analysis...")
        tfidf_start_time = time.time()
        tfidf_keywords = self.get_tfidf_keywords(output_data)
        print(tfidf_keywords)
        tfidf_end_time = time.time()
        tfidf_elapsed_time = tfidf_end_time - tfidf_start_time
        print("TF-IDF analysis took {:.2f} seconds.".format(tfidf_elapsed_time))

        # print("Saving TF-IDF analysis...")
        # save_tfidf_start_time = time.time()
        # self.save_tfidf_scores(tfidf_scores)
        # save_tfidf_end_time = time.time()
        # save_tfidf_elapsed_time = save_tfidf_end_time - save_tfidf_start_time
        # print("Saving TF-IDF analysis took {:.2f} seconds.".format(save_tfidf_elapsed_time))

        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Pipeline completed in {:.2f} seconds.".format(elapsed_time))

if __name__ == '__main__':
    data_folder = '../data/part/'
    output_json_path = '../data/results/output.json'
    analysis_output_path = '../data/analysis/named_entities.txt'
    tfidf_output_path = '../data/analysis/tfidf_scores.txt'

    # Run the data pipeline
    pipeline = DataPipeline(data_folder, output_json_path, analysis_output_path, tfidf_output_path)
    pipeline.run_pipeline()

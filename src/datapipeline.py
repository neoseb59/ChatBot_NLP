import os
import json
import time
from termhoodanalyzer import DataAnalyzer
import xmlparser
import xmlloader

class DataPipeline:
    def __init__(self, data_folder, output_path, analysis_output_folder):
        self.data_folder = data_folder
        self.output_path = output_path
        self.analysis_output_folder = analysis_output_folder

    def run_pipeline(self):
        start_time = time.time()

        print("Running data pipeline...")

        # Step 1: Load XML files
        load_start_time = time.time()
        print("Loading XML files from", self.data_folder)
        output_data = []
        for filename in os.listdir(self.data_folder):
            if filename.endswith(".xml"):
                file_path = os.path.join(self.data_folder, filename)
                loader = xmlloader.XMLloader(file_path)
                xml_data = loader.load()

                parser = xmlparser.XMLParser(xml_data, self.output_path)
                parsed_data = parser.parse()
                output_data.extend(parsed_data)
        load_end_time = time.time()
        load_elapsed_time = load_end_time - load_start_time
        print("Loading XML files took {:.2f} seconds.".format(load_elapsed_time))

        # Step 2: Save parsed data to JSON file
        save_start_time = time.time()
        print("Saving parsed data to", self.output_path)
        with open(self.output_path, 'w', encoding='utf-8') as output_file:
            json.dump(output_data, output_file, ensure_ascii=False, indent=4)
        save_end_time = time.time()
        save_elapsed_time = save_end_time - save_start_time
        print("Saving parsed data took {:.2f} seconds.".format(save_elapsed_time))

        # Step 3: Analyze the parsed data
        analysis_start_time = time.time()
        print("Analyzing data...")
        analyzer = DataAnalyzer(self.output_path)
        analyzer.analyze_responses()
        analysis_end_time = time.time()
        analysis_elapsed_time = analysis_end_time - analysis_start_time
        print("Analyzing data took {:.2f} seconds.".format(analysis_elapsed_time))


        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Pipeline completed in {:.2f} seconds.".format(elapsed_time))

if __name__ == '__main__':
    data_folder = '../data/part/'
    output_json_path = '../data/results/output.json'
    analysis_output_folder = '../data/analysis/'

    # Run the data pipeline
    pipeline = DataPipeline(data_folder, output_json_path, analysis_output_folder)
    pipeline.run_pipeline()

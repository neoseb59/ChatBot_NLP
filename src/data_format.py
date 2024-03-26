## Get all the output.json and aggregate them in one file
import json
import os
from pathlib import Path
import csv 

class DataFormat:
    def __init__(self, base_input_folder, base_output_folder):
        self.base_input_folder = base_input_folder
        self.base_output_folder = base_output_folder

    def get_all_parsed_data(self):
        all_parsed_data = []
        for theme_folder in os.listdir(self.base_output_folder):
            theme_output_folder = self.base_output_folder / theme_folder
            output_path = theme_output_folder / 'output.json'
            if output_path.exists():
                with open(output_path, 'r', encoding='utf-8') as file:
                    parsed_data = json.load(file)
                    all_parsed_data.extend(parsed_data)
        return all_parsed_data

    def format_data_for_training(self):
        all_parsed_data = self.get_all_parsed_data()
        formatted_data = []
        for data in all_parsed_data:
            formatted_data.append("###Human:\n"+data['question']+ "\n\n###Assistant:\n"+ data['response'])
        output_path = self.base_output_folder / 'formatted_data.json'
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(formatted_data, file, ensure_ascii=False, indent=4)

    def format_data_to_csv(self):
        ## Create a column named text and put every element of the list under it
        all_parsed_data = self.get_all_parsed_data()
        formatted_data = []
        for data in all_parsed_data:
            formatted_data.append("###Human:\\n"+data['question']+ "\\n\\n###Assistant:\\n"+ data['response'])
        
        output_path = self.base_output_folder / 'formatted_data.csv'
        with open(output_path, 'w', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['text'])
            for row in formatted_data:
                writer.writerow([row])
        

    def aggregate_parsed_data(self):
        all_parsed_data = self.get_all_parsed_data()
        output_path = self.base_output_folder / 'all_parsed_data.json'
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(all_parsed_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    base_input_folder = Path('../data/results')
    base_output_folder = Path('../data/results')
    formatter = DataFormat(base_input_folder, base_output_folder)
    formatter.format_data_to_csv()
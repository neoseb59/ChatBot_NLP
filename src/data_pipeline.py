import os
from pathlib import Path
import json
import re
import time
from xml_loader import XMLLoader
from xml_parser import XMLParser
from token_tagger import TokenTagger
from termhood_analyzer import TermhoodAnalyzer
from tfidf_analyzer import TfidfAnalyzer
from named_entities_analyzer import NamedEntitiesAnalyzer
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
        self.terms_output_path = theme_output_folder / 'terms.json'
        self.analysis_output_path = theme_output_folder / 'analysis_results.json'

    def load_and_parse_xml(self) -> list[dict[str, str]]:
        print("Loading XML files from", self.data_folder)
        output_data = []
        files = os.listdir(self.data_folder)
        for filename in tqdm(files, total=len(files), miniters=1):
            if filename.endswith(".xml"):
                file_path = self.data_folder / filename
                loader = XMLLoader(file_path)
                xml_data = loader.load()

                parser = XMLParser(xml_data)
                parsed_data = parser.parse()
                output_data.extend(parsed_data)
        return output_data

    def save_parsed_data(self, output_data: list[dict[str, str]]):
        with open(self.parsing_output_path, 'w', encoding='utf-8') as output_file:
            json.dump(output_data, output_file, ensure_ascii=False, indent=4)

    def run_pipeline_for_theme(self, theme_name, reparse_xml: bool = False, fast: bool = False, analyze_named_entities: bool = False):
        print("Running data pipeline for theme '", theme_name, "'", sep='')
        self.set_paths_for_theme(theme_name)
        start_time = time.time()

        output_data = {}
        if reparse_xml or not self.parsing_output_path.is_file():
            output_data = self.load_and_parse_xml()
            self.save_parsed_data(output_data)
            if not output_data:
                print("No data found for theme", theme_name)
                return
        else:
            with open(self.parsing_output_path, 'r', encoding='utf-8') as file:
                output_data = json.load(file)

        tagger = TokenTagger(output_data, fast=fast)
        tagger.run()

        th_analyzer = TermhoodAnalyzer(tagger.tagged_corpus)
        th_results = th_analyzer.run()

        terms = set()
        th_threshold = 0
        for term, c_value in th_results.items():
            if c_value > th_threshold:
                terms.add(term)

        if analyze_named_entities:
            ne_analyzer = NamedEntitiesAnalyzer(tagger.docs)
            ne_result = ne_analyzer.run()
            named_entities = ne_result['entities']
            for entity, label in named_entities.items():
                # Only keep organizations (ORG-labeled entities that match the regex below)
                org_regex = re.compile(r"^([A-Z]{2,}|[A-Za-zÀÂÇÉÈÊËÎÏÔÙÛÜÆŒàâçéèêëîïôùûüæœ]+(\s+[A-Za-zÀÂÇÉÈÊËÎÏÔÙÛÜÆŒàâçéèêëîïôùûüæœ]+)+)$")
                if label == "ORG" and org_regex.search(entity):
                    terms.add(entity)

        tfidf_analyzer = TfidfAnalyzer(tagger.corpus, terms)
        tfidf_result = tfidf_analyzer.run()

        final_terms = {}
        tfidf_threshold = 0
        for response, scores in tfidf_result.items():
            final_terms[response] = []
            for term, tfidf in scores.items():
                if tfidf > tfidf_threshold:
                    final_terms[response].append(term)

        with open(self.terms_output_path, 'w', encoding='utf-8') as output_file:
            json.dump(final_terms, output_file, ensure_ascii=False, indent=4)  # THIS IS THE FILE (under data/results/<Topic>/terms.json) that contains context paragraphs with associated relevant terms

        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Pipeline for theme '{}' completed in {:.2f} seconds".format(theme_name, elapsed_time), end='')
        if len(final_terms) == 0:
            print(" (was empty)", end='')
        print(".\n")

    def run(self, reparse_xml: bool = False, fast: bool = False, analyze_named_entities: bool = False):
        themes = [theme for theme in os.listdir(self.base_data_folder) if os.path.isdir(self.base_data_folder / theme)]
        for theme in themes:
            self.run_pipeline_for_theme(theme, reparse_xml=reparse_xml, fast=fast, analyze_named_entities=analyze_named_entities)
        print("Finished. You may now run question_generator.py!")

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    base_data_folder = absolute_file_dir.parent / "data/themes"
    base_output_folder = absolute_file_dir.parent / "data/results"
    pipeline = DataPipeline(base_data_folder, base_output_folder)
    pipeline.run(fast=True, analyze_named_entities=True)

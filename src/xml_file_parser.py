from bs4 import BeautifulSoup
import xml_loader
import re
import os
from pathlib import Path
import shutil

class XMLFileParser:
    def __init__(self, xml, data_folder, base_directory, file_path=None):
        self.data_folder = data_folder
        self.base_directory = base_directory
        self.xml = xml.encode('utf-8') if xml else None
        self.file_path = file_path

    def parse_theme(self) -> str | None:
        soup = BeautifulSoup(self.xml, 'xml')
        themes = soup.find_all('Theme')
        titles = [t.find('Titre') for t in themes]
        return titles[0].get_text() if titles else None

    def order_file(self):
        theme = self.parse_theme()
        
        if theme:
            theme_directory = re.sub('[^0-9a-zA-Z]+', '_', theme)
            full_path = self.base_directory / theme_directory
            
            if not os.path.exists(full_path):
                os.makedirs(full_path)
            
            shutil.move(self.file_path, full_path / self.file_path.name)
            print(f"File moved to {full_path / self.file_path.name}")
        else:
            print("Theme could not be parsed. File not moved.")
    
    def parse_files(self):
        for filename in os.listdir(self.data_folder):
            if filename.endswith(".xml"):
                file_path = self.data_folder / filename
                loader = xml_loader.XMLLoader(file_path)
                xml_data = loader.load()
                self.file_path = file_path
                self.xml = xml_data.encode('utf-8')
                self.order_file()

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    data_folder = absolute_file_dir.parent / "data/part/"
    base_directory = absolute_file_dir.parent / "data/themes/"
    parser = XMLFileParser(None, data_folder, base_directory)
    parser.parse_files()

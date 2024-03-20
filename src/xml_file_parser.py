from bs4 import BeautifulSoup
import xml_loader
import re
import os
import shutil

class XMLFileParser:
    def __init__(self, xml, data_folder, base_directory, file_path=None):
        self.data_folder = data_folder
        self.base_directory = base_directory
        self.xml = xml.encode('utf-8') if xml else None
        self.file_path = file_path

    def parse_theme(self)->str or None:
        soup = BeautifulSoup(self.xml, 'xml')
        themes = soup.find_all('Theme')
        titles = [t.find('Titre') for t in themes]
        return titles[0].get_text() if titles else None

    def order_file(self):
        theme = self.parse_theme()
        
        if theme:
            theme_directory = re.sub('[^0-9a-zA-Z]+', '_', theme)
            full_path = os.path.join(self.base_directory, theme_directory)
            
            if not os.path.exists(full_path):
                os.makedirs(full_path)
            
            shutil.move(self.file_path, os.path.join(full_path, os.path.basename(self.file_path)))
            print(f"File moved to {os.path.join(full_path, os.path.basename(self.file_path))}")
        else:
            print("Theme could not be parsed. File not moved.")
    
    def parse_files(self):
        for filename in os.listdir(self.data_folder):
            if filename.endswith(".xml"):
                file_path = os.path.join(self.data_folder, filename)
                loader = xml_loader.XMLloader(file_path)
                xml_data = loader.load()
                self.file_path = file_path
                self.xml = xml_data.encode('utf-8')
                self.order_file()

if __name__ == '__main__':
    parser = XMLFileParser(None, '../data/part/', '../data/themes/')
    parser.parse_files()
class XMLloader:
    def __init__(self, data_path:str):
        self.data_path = data_path

    def load(self):
        with open(self.data_path, 'r') as f:
            return f.read()


if __name__ == '__main__':
    pass
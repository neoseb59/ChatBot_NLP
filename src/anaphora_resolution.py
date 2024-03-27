from pathlib import Path
import json
from spacy.tokens import Token
from token_tagger import TokenTagger

class AnaphoraResolver:

    def __init__(self, tagged_corpus: list[dict[str,list[Token]]]):
        self.input = tagged_corpus
        self.output = []

        self.pronouns_rules = {
            "je": ["Undefined", "Sing"],
            "tu": ["Undefined", "Sing"],
            "il": ["Masc", "Sing"],
            "elle": ["Fem", "Sing"],
            # "on": ["Undefined", "Sing"],
            "nous": ["Undefined", "Plur"],
            # "vous": ["Undefined", "Plur"],
            "ils": ["Masc", "Plur"],
            "elles": ["Fem", "Plur"]
        }

    def match_rule(self, candidate: list[str], gender_rule, number_rule) -> bool:
        gender_filter = (candidate[0] == "Masc" and gender_rule == "Fem") or (candidate[0] == "Fem" and gender_rule == "Masc")
        number_filter = (candidate[1] == "Sing" and number_rule == "Plur") or (candidate[1] == "Plur" and number_rule == "Sing")
        return not gender_filter and not number_filter

    def matching_score(self, noun_index, pronoun_index):
        if noun_index < pronoun_index:
            return pronoun_index - noun_index
        return float("Inf")

    def resolve_anaphoras(self, data: list[Token]) -> list[Token]:
        result = data.copy()
        nouns_indexes = []
        pronouns_indexes = []

        # We get nouns and pronouns indexes
        for i in range(len(data)):
            if data[i].tag_ in ("NOUN", "PROPN"):
                nouns_indexes.append(i)
            elif data[i].tag_ == "PRON":
                pronouns_indexes.append(i)

        for p in pronouns_indexes:
            pronoun = data[p]
            if pronoun.text.lower() in self.pronouns_rules.keys():  # supported pronoun
                best_score = float("Inf")
                index = -1
                for n in nouns_indexes:
                    noun = data[n]
                    morph = str(noun.morph)
                    gender = "Undefined"
                    number = "Undefined"
                    for category in morph.split('|'):
                        pair = category.split('=')
                        if len(pair) != 2:
                            continue
                        if pair[0] == "Gender":
                            gender = pair[1]
                        elif pair[0] == "Number":
                            number = pair[1]
                    if self.match_rule(self.pronouns_rules[pronoun.text.lower()], gender, number):
                        score = self.matching_score(n, p)
                        if score < best_score:
                            best_score = score
                            index = n
                if index != -1: # we found a matching noun
                    result[p] = data[index]
        return result

    def run(self):
        print("Resolving anaphoras in corpus...")
        for q_and_a in self.input:
            question = self.resolve_anaphoras(q_and_a['question'])
            response = self.resolve_anaphoras(q_and_a['response'])
            output_q_and_a = { 'question': question, 'response': response }
            self.output.append(output_q_and_a)
        return self.output

if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    data_location = absolute_file_dir.parent / "data/results/Argent_Impôts_Consommation/output.json"
    with open(data_location, 'r', encoding='utf-8') as file:
        data = json.load(file)

    tagger = TokenTagger(data, fast=True)
    tagger.run()

    resolver = AnaphoraResolver(tagger.tagged_corpus)
    results = resolver.run()
    for i in range(len(results)):
        x = ' '.join([word.text for word in resolver.input[i]['question']])
        y = ' '.join([word.text for word in results[i]['question']])
        if x != y:
            print("Original :", x)
            print("Changed  :", y)

from termhood_analyzer import TaggedWord
from pathlib import Path
import json
from token_tagger import TokenTagger

class AnaphoraResolver:

    def __init__(self, tagged_corpus : list[dict[str,list[TaggedWord]]]):
        self.input = tagged_corpus
        self.output = []

        self.pronouns_rules = {
            "je": ["Undefined", "Sing"],
            "tu": ["Undefined", "Sing"],
            "il": ["Masc", "Sing"],
            "elle": ["Fem", "Sing"],
            "on": ["Undefined", "Sing"],
            "nous": ["Undefined", "Plur"],
            "vous": ["Undefined", "Plur"],
            "ils": ["Masc", "Plur"],
            "elles": ["Fem", "Plur"]
        }

    def match_rule(self, candidate: list[str], gender_rule, number_rule) -> bool:
        gender_filter = (candidate[0] == "Masc" and gender_rule == "Fem") or (candidate[0] == "Fem" and gender_rule == "Masc")
        number_filter = (candidate[1] == "Sing" and number_rule == "Plur") or (candidate[1] == "Plur" and number_rule == "Sing")
        return not (gender_filter or number_filter)

    def matching_score(self, noun_index, pronoun_index):
        if noun_index < pronoun_index:
            return pronoun_index - noun_index
        return float("Inf")

    def resolve_anaphora(self, data : list[TaggedWord]) -> list[TaggedWord] :
        result = data.copy()
        nouns_indexes = []
        pronouns_indexes = []

        # We get nouns and pronouns indexes
        for i in range(len(data)):
            if data[i].tag == "NOUN" or data[i].tag == "PROPN":
                nouns_indexes.append(i)
            elif data[i].tag == "PRON":
                pronouns_indexes.append(i)

        for p in pronouns_indexes:
            pronoun = data[p].text.lower()
            if pronoun in self.pronouns_rules.keys(): # supported pronoun
                best_score = float("Inf")
                index = -1
                for n in nouns_indexes:
                    noun = data[n]
                    if self.match_rule(self.pronouns_rules[pronoun], noun.gender, noun.number):
                        score = self.matching_score(n, p)
                        if score < best_score:
                            best_score = score
                            index = n
                if index != -1: # we found a matching noun
                    result[p] = noun
        return result

    def anaphora_resolution(self) :

        for q_and_a in self.input:
            question = self.resolve_anaphora(q_and_a["question"])
            response = self.resolve_anaphora(q_and_a["response"])
            output_q_and_a = {"question":question, "response":response}
            self.output.append(output_q_and_a)


if __name__ == '__main__':
    absolute_file_dir = Path(__file__).resolve().parent
    data_location = absolute_file_dir.parent / "data/results/Argent_Impôts_Consommation/output.json"
    with open(data_location, 'r', encoding='utf-8') as file:
        data = json.load(file)

    tagger = TokenTagger(data, fast=True)
    tagger.run()

    resolver = AnaphoraResolver(tagger.tagged_corpus)
    resolver.anaphora_resolution()
    for i in range(len(resolver.output)):
        x = ' '.join([word.text for word in resolver.input[i]["response"]])
        y = ' '.join([word.text for word in resolver.output[i]["response"]])
        if x != y:
            print(x)
            print(y)
    

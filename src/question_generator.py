from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# from transformers import Text2TextGenerationPipeline
import re
import os
from pathlib import Path
import json
from tqdm import tqdm

model_name = 'lincoln/barthez-squadFR-fquad-piaf-question-generation'

loaded_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
loaded_tokenizer = AutoTokenizer.from_pretrained(model_name)

absolute_file_dir = Path(__file__).resolve().parent
input_folder = absolute_file_dir.parent / "data/results"
output_path = absolute_file_dir.parent / "data/train.csv"

trainset = "text\n"
# example_context = """
# Je m'inscris auprès d'une maternité ou d'une maison de <hl>santé<hl>
# Je transmets ma déclaration de grossesse à ma caisse d'assurance maladie et à ma caisse d'allocations familiales (Caf : Caf : Caisse d'allocations familiales ou MSA : MSA : Mutualité sociale agricole) et je me renseigne sur la prime à la naissance et l'allocation de base de la prestation d'accueil du jeune enfant (Paje)
# J'effectue les examens médicaux obligatoires
# J'ai droit à des autorisations d'absence pour m'y rendre, ainsi que la personne avec qui je vis en couple : Mariage, Pacs ou concubinage (union libre).
# Je m'informe sur la prise en charge des dépenses de <hl>santé<hl>
# Je demande l'aide à domicile, si je suis confrontée à des difficultés médicales ou sociales et financières
# Je peux, à compter de la 1re consultation médicale de grossesse et au plus tard avant la fin du 5e mois de grossesse déclarer une sage-femme référente. Cette sage-femme m'accompagne de la grossesse à la maternité. Cette déclaration se fait auprès de l'Assurance maladie et reste valable 14 semaines après l'accouchement.
# """

special_regex_chars = re.compile(r"([\.\?\+\*\(\)\[\]\{\}\\])")
themes = [theme for theme in os.listdir(input_folder) if os.path.isdir(input_folder / theme)]
print("Please ignore any warning messages about sequence length. In such cases, a new attempt will automatically be made with shorter paragraphs.")
for theme in themes:
    print("Generating train data for theme '", theme, "'...", sep='')
    with open(input_folder / theme / "terms.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
    for context, terms in tqdm(data.items(), total=len(data), miniters=1):  # contexts are paragraphs (i.e. responses from the corpus)
        for term in terms:
            highlighted_context = context
            search = re.compile('(' + special_regex_chars.sub(r"\___\1", term).replace('___', '') + ')', re.IGNORECASE)
            if not search.search(context):
                continue
            highlighted_context = search.sub(r"<hl>\1<hl>", highlighted_context)
            sentences = highlighted_context.split(". ")
            retained_number_of_sentences = len(sentences)
            success = False
            # HACK: Shorten the context paragraph, otherwise the model is not happy with some (one, actually) of the longer responses given as input (max length exceeded)
            while not success and retained_number_of_sentences > 0:
                subcontext = ". ".join(sentences[:retained_number_of_sentences])
                subcontext += '.'
                try:
                    inputs = loaded_tokenizer(subcontext, return_tensors='pt')
                    out = loaded_model.generate(
                        input_ids=inputs.input_ids,
                        attention_mask=inputs.attention_mask,
                        num_beams=16,
                        num_return_sequences=16,
                        length_penalty=10,
                    )
                    for question in out:
                        question_string = loaded_tokenizer.decode(question, skip_special_tokens=True)
                        question_string = question_string.strip()
                        if not question_string.endswith("?"):
                            question_string += " ?"
                        elif not question_string.endswith(" ?"):
                            question_string = question_string[:-1].strip()
                            question_string += " ?"
                        question_string = question_string.replace("+?", "?")
                        question_string = question_string.replace("- ", "-")
                        question_string = question_string.replace(" -", "-")
                        question_string = question_string.replace(" '", "'")
                        newline = f"\"###Human:\\n{question_string}\\n\\n###Assistant:\\n{term}\"\n"
                        trainset += newline
                    success = True
                except:
                    retained_number_of_sentences -= 1

if output_path.is_file():
    os.remove(output_path)
with open(output_path, 'w', encoding='utf-8') as file:
    file.write(trainset)
print("\nAll concatenated train data has been saved in the trainset file under data/train.csv.")

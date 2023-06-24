import os
import json
from question import *
                    
def read_questions_and_answers(questions_filename, answers_filename):
    stockllll=0
    questions = []
    with open(questions_filename, 'r', encoding='utf-8') as q_file, open(answers_filename, 'r', encoding='utf-8') as a_file:
        q_lines = q_file.readlines()
        a_lines = a_file.readlines()

        current_chapter = ""
        answers = {}
        for line in a_lines:
            if line.startswith("Chapitre"):
                current_chapter = line.strip()
                answers[current_chapter] = []
            elif line.strip() and current_chapter and line.strip()[0].isdigit():
                answers[current_chapter].extend(line.strip().split(';')[:-1])

        current_chapter = ""
        question_count = 0
        for line in q_lines:
            if line.startswith("Chapitre"):
                current_chapter = line.strip()
                stockllll=stockllll+1
                question_count = 0
            elif line.strip():
                if line.strip()[0].isdigit() and "." in line:
                    question_number = int(line.split('.')[0].strip())
                    question = line.split('.')[1].strip()
                    options = [q_lines[q_lines.index(line) + i].strip() for i in range(1, 6) if q_lines.index(line) + i < len(q_lines)]

                    if current_chapter in answers and question_number - 1 < len(answers[current_chapter]):
                        correct_answers_raw = answers[current_chapter][question_number - 1].split('.')[1].strip()
                        correct_answers = [i.strip() for i in correct_answers_raw.split(',') if i.strip()]
                    else:
                        correct_answers = []

                    questions.append(Question(stockllll,question_count+1,question, options, correct_answers))
                    question_count += 1
    return questions

questions = read_questions_and_answers("questions.txt", "reponses.txt")

input_file = "edit.txt"

with open(input_file, "r") as f:
    reponses = f.readlines()

for question, reponse in zip(questions, reponses):
    # Supprime les sauts de ligne, les espaces et les virgules
    reponse = reponse.strip().replace(" ", "").replace(",", "")
    # Ajoute les réponses correctes à l'objet Question
    question.correct_answers = list(reponse)

for question in questions:
    print(question.chapitre)
    print(f"Question: {question.question}")
    print("Options:")
    for option in question.options:
        print(f"{option}")
    print(f"Correct Answers: {', '.join(question.correct_answers)}")
    print("\n")

# Divisez les questions en 11 groupes en fonction de leur chapitre
chapitres = set(q.chapitre for q in questions)
groupes = {chapitre: [] for chapitre in chapitres}
for question in questions:
    groupes[question.chapitre].append(question)

# Pour chaque groupe de questions, écrivez les questions dans un fichier JSON séparé
for chapitre, groupe in groupes.items():
    nom_fichier = f"chapitre{chapitre}.json"
    with open(nom_fichier, "w") as f:
        json.dump([q.__dict__ for q in groupe], f, indent=4)
print(len(questions))
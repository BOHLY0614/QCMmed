import tkinter as tk
from tkinter import ttk
import json
import random
import time

class QCMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")

        self.title("Quiz QCM")

        self.chapter_files = [f"chapitre{i}.json" for i in range(1, 12)]
        self.chapters = self.load_chapters()

        self.create_main_menu()

    def load_chapters(self):
        chapters = {}
        for file in self.chapter_files:
            with open(file, "r", encoding="utf-8") as f:
                chapter_data = json.load(f)
                chapters[file] = chapter_data
        return chapters

    def create_main_menu(self):
        self.main_menu_frame = ttk.Frame(self)
        self.main_menu_frame.pack(pady=100)

        title = ttk.Label(self.main_menu_frame, text="Choisissez un chapitre", font=("Arial", 24))
        title.pack(pady=20)

        for i in range(1, len(self.chapter_files) + 1):
            name=chapter_name(i)
            chapter_button = ttk.Button(self.main_menu_frame, text=(name[0]+name[1:].lower()),
                                        command=lambda i=i: self.start_quiz(i))
            chapter_button.pack(pady=5)

        mix_three_button = ttk.Button(self.main_menu_frame, text="Mélange de trois chapitres",
                                      command=self.select_three_chapters)
        mix_three_button.pack(pady=10)

        mix_all_button = ttk.Button(self.main_menu_frame, text="Mélange de tous les chapitres",
                                    command=self.mix_all_chapters)
        mix_all_button.pack(pady=10)

    def start_quiz(self, chapter):
        self.main_menu_frame.pack_forget()
        self.quiz_frame = ttk.Frame(self)
        self.quiz_frame.pack(pady=100)

        self.current_question = 0
        if chapter == -1:
         self.current_chapter = self.mixed_chapter
        else:
            self.current_chapter = self.chapters[self.chapter_files[chapter - 1]]
            random.shuffle(self.current_chapter)
        self.total_questions = len(self.current_chapter)  # Ajout de l'attribut total_questions
        self.score = 0
        self.start_time = time.time()

        self.show_question()

    def show_question(self):
        self.clear_frame(self.quiz_frame)
        self.randomized_options = []

        question_data = self.current_chapter[self.current_question]
        question_label = ttk.Label(self.quiz_frame, text=question_data["question"], wraplength=700)
        question_label.pack(pady=20)

        self.selected_answers = [tk.BooleanVar() for _ in question_data["options"]]

        self.randomized_options = question_data["options"]
        random.shuffle(self.randomized_options)

        for i, option in enumerate(self.randomized_options):
            answer_checkbutton = ttk.Checkbutton(self.quiz_frame, text=associate(i)+option[1:], variable=self.selected_answers[i])
            answer_checkbutton.pack(pady=5)

        next_button = ttk.Button(self.quiz_frame, text="Suivant", command=self.check_answer)
        next_button.pack(pady=20)

        elapsed_time = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_label = ttk.Label(self.quiz_frame, text=f"Temps écoulé : {hours}h {minutes}m {seconds}s")
        time_label.pack(side="left", padx=10)

        remaining_questions = len(self.current_chapter) - self.current_question
        remaining_label = ttk.Label(self.quiz_frame, text=f"Questions restantes : {remaining_questions}")
        remaining_label.pack(side="right", padx=10)


    def check_answer(self):

        correct_answers = self.current_chapter[self.current_question]["correct_answers"]
        new_correct_answers = []
        for answer in correct_answers:
            for index, option in enumerate(self.randomized_options):
                if option[0]==answer:
                    new_correct_answers.append(associate(index))
        correct_answers=new_correct_answers

        user_answers = [chr(i + 65) for i, selected in enumerate(self.selected_answers) if selected.get()]

        result_text = ""
        if sorted(correct_answers) == sorted(user_answers):
            self.score += 1
            result_text = "Bonne réponse !"
        else:
            result_text = f"Mauvaise réponse...\nLa bonne réponse est : {', '.join(sorted(correct_answers))}"

        self.show_result(result_text)

    def show_result(self, result_text):
        result_window = tk.Toplevel(self)
        result_window.title("Résultat")

        result_label = ttk.Label(result_window, text=result_text)
        result_label.pack(pady=20)

        continue_button = ttk.Button(result_window, text="Continuer", command=result_window.destroy)
        continue_button.pack(pady=10)

        result_window.transient(self)
        result_window.grab_set()
        self.wait_window(result_window)

        self.current_question += 1
        if self.current_question < len(self.current_chapter):
            self.show_question()
        else:
            self.show_final_score()

    def select_three_chapters(self):
        self.chapter_selection_window = tk.Toplevel(self)
        self.chapter_selection_window.title("Sélection de chapitres")

        instruction_label = ttk.Label(self.chapter_selection_window, text="Choisissez trois chapitres à mélanger :")
        instruction_label.pack(pady=10)

        self.chapter_vars = [tk.BooleanVar() for _ in self.chapter_files]
        for i in range(len(self.chapter_files)):
            chapter_checkbutton = ttk.Checkbutton(self.chapter_selection_window, text=f"Chapitre {i + 1}",
                                                  variable=self.chapter_vars[i])
            chapter_checkbutton.pack(pady=5)

        confirm_button = ttk.Button(self.chapter_selection_window, text="Confirmer",
                                    command=self.confirm_three_chapters)
        confirm_button.pack(pady=10)

    def confirm_three_chapters(self):
        selected_chapter_indices = [i for i, var in enumerate(self.chapter_vars) if var.get()]
        if len(selected_chapter_indices) != 3:
            error_label = ttk.Label(self.chapter_selection_window, text="Veuillez sélectionner exactement trois chapitres.",
                                    foreground="red")
            error_label.pack(pady=10)
            return

        selected_chapters = [self.chapters[self.chapter_files[i]] for i in selected_chapter_indices]
        self.chapter_selection_window.destroy()
        self.start_mixed_quiz(selected_chapters)

    def mix_three_chapters(self):
        chapter_indices = random.sample(range(len(self.chapter_files)), 3)
        selected_chapters = [self.chapters[self.chapter_files[i]] for i in chapter_indices]
        self.start_mixed_quiz(selected_chapters)

    def mix_all_chapters(self):
        all_chapters = [self.chapters[file] for file in self.chapter_files]
        self.start_mixed_quiz(all_chapters)

    def start_mixed_quiz(self, selected_chapters):
        mixed_questions = [question for chapter in selected_chapters for question in chapter]
        random.shuffle(mixed_questions)
        self.mixed_chapter = random.sample(mixed_questions, min(70, len(mixed_questions)))  # Création d'un attribut mixed_chapter
        self.start_quiz(-1)

    def show_final_score(self):
        self.clear_frame(self.quiz_frame) 

        score_label = ttk.Label(self.quiz_frame, text=f"Score final : {self.score}/{len(self.current_chapter)}", font=("Arial", 24))
        score_label.pack(pady=20)

        menu_button = ttk.Button(self.quiz_frame, text="Retour au menu principal", command=self.return_to_main_menu)
        menu_button.pack(pady=10)

        quit_button = ttk.Button(self.quiz_frame, text="Quitter", command=self.quit)
        quit_button.pack(pady=10)

    def return_to_main_menu(self):
        self.clear_frame(self.quiz_frame)
        self.quiz_frame.pack_forget()  # Ajout de cette ligne pour oublier le quiz_frame
        self.create_main_menu()

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

def associate(index):
        if index == 0:
            return "A"
        elif index == 1:
            return "B"
        elif index == 2:
            return "C"
        elif index == 3:
            return "D"
        elif index == 4:
            return "E"
        
def chapter_name(index):
    index-=1
    if index == 0:
        return "LE CORPS HUMAIN"
    elif index == 1:
        return "LE SYSTÈME NERVEUX"
    elif index == 2:
        return "ANALISATEURS"
    elif index == 3:
        return "LES GLANDES ENDOCRINES"
    elif index == 4:
        return "MOUVEMENT"
    elif index == 5:
        return "DIGESTION ET ABSORPTION"
    elif index == 6:
        return "CIRCULATION"
    elif index == 7:
        return "RESPIRATION"
    elif index == 8:
        return "EXCRÉTION"
    elif index == 9:
        return "MÉTABOLISME"
    elif index == 10:
        return "LA REPRODUCTION"
        
if __name__ == "__main__":
    app = QCMApp()
    app.mainloop()
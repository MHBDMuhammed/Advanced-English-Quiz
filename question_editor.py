import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from ttkthemes import ThemedTk # Modern temalar için

# Sabitler
JSON_FILENAME = "questions.json"
NUM_OPTIONS = 4 # Sabit şık sayısı (web sitesiyle uyumlu olmalı)

class QuestionEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Question Editor")
        # Pencere boyutunu ayarla ve yeniden boyutlandırmayı etkinleştir
        self.root.geometry("850x650")
        self.root.resizable(True, True)

        # Stil ve Tema Ayarları
        self.style = ttk.Style()
        # Kullanılabilir temaları görmek için: print(self.style.theme_names())
        # Denenebilecek bazı temalar: 'arc', 'adapta', 'plastik', 'ubuntu', 'yaru'
        try:
            # 'adapta' veya 'arc' genellikle modern görünür
            self.root.set_theme("adapta")
        except tk.TclError:
            print("Seçilen tema bulunamadı, varsayılan tema kullanılıyor.")
            # Varsayılan ttk temasını kullan

        # Ana Çerçeveler
        self.main_frame = ttk.Frame(root, padding="15 15 15 15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # -- Sol Taraf: Soru Listesi --
        self.list_frame = ttk.LabelFrame(self.main_frame, text="Questions", padding="10")
        self.list_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")

        # Treeview (Soru Listesi)
        self.tree_scroll_y = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = ttk.Scrollbar(self.list_frame, orient=tk.HORIZONTAL)

        self.question_tree = ttk.Treeview(
            self.list_frame,
            columns=("Question", "Correct Answer"),
            show="headings", # Sadece başlıkları göster, ilk sütunu gizle
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set,
            selectmode="browse" # Sadece tekil seçim
        )
        self.tree_scroll_y.config(command=self.question_tree.yview)
        self.tree_scroll_x.config(command=self.question_tree.xview)

        self.question_tree.heading("Question", text="Question")
        self.question_tree.heading("Correct Answer", text="Correct Answer")
        self.question_tree.column("Question", width=250, anchor=tk.W)
        self.question_tree.column("Correct Answer", width=150, anchor=tk.W)

        # Scrollbar'ları ve Treeview'ı yerleştir
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.question_tree.pack(fill=tk.BOTH, expand=True)

        # Seçim değiştiğinde formu doldur
        self.question_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # -- Sağ Taraf: Düzenleme Formu --
        self.form_frame = ttk.LabelFrame(self.main_frame, text="Edit Question Details", padding="15")
        self.form_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")

        # Form Alanları
        ttk.Label(self.form_frame, text="Question Text:").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.question_text_var = tk.StringVar()
        self.question_text_entry = ttk.Entry(self.form_frame, textvariable=self.question_text_var, width=50)
        self.question_text_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        ttk.Label(self.form_frame, text="Options:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        ttk.Label(self.form_frame, text="Correct?").grid(row=2, column=1, sticky="w", padx=(10,0), pady=(0, 5))

        self.option_vars = []
        self.option_entries = []
        self.correct_answer_var = tk.IntVar(value=-1) # Başlangıçta hiçbiri seçili değil

        for i in range(NUM_OPTIONS):
            option_var = tk.StringVar()
            self.option_vars.append(option_var)

            option_entry = ttk.Entry(self.form_frame, textvariable=option_var, width=40)
            option_entry.grid(row=3 + i, column=0, sticky="ew", pady=2)
            self.option_entries.append(option_entry)

            rb = ttk.Radiobutton(self.form_frame, variable=self.correct_answer_var, value=i)
            rb.grid(row=3 + i, column=1, sticky="w", padx=(15, 0))

        # Form Butonları
        self.form_buttons_frame = ttk.Frame(self.form_frame)
        self.form_buttons_frame.grid(row=3 + NUM_OPTIONS, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        self.add_button = ttk.Button(self.form_buttons_frame, text="✨ Add New", command=self.add_question, style="Accent.TButton") # Stil denemesi
        self.add_button.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)

        self.update_button = ttk.Button(self.form_buttons_frame, text="💾 Update Selected", command=self.update_question, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.clear_button = ttk.Button(self.form_buttons_frame, text="🧹 Clear Form", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=(5, 0), expand=True, fill=tk.X)


        # Ana Butonlar (Alt Kısım)
        self.main_buttons_frame = ttk.Frame(self.main_frame)
        self.main_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        self.delete_button = ttk.Button(self.main_buttons_frame, text="❌ Delete Selected", command=self.delete_question, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=(0, 10))

        # Boşluk bırakmak için spacer
        spacer = ttk.Frame(self.main_buttons_frame)
        spacer.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.save_button = ttk.Button(self.main_buttons_frame, text="💾 Save All Changes to JSON", command=self.save_questions, style="Accent.TButton")
        self.save_button.pack(side=tk.RIGHT)


        # Sütun ve Satır Ağırlıklarını Ayarla (Yeniden Boyutlandırma İçin)
        self.main_frame.columnconfigure(0, weight=1) # Liste sütunu genişlesin
        self.main_frame.columnconfigure(1, weight=2) # Form sütunu daha fazla genişlesin
        self.main_frame.rowconfigure(0, weight=1)    # Üst satır (liste+form) dikey genişlesin

        self.list_frame.rowconfigure(0, weight=1) # Treeview dikey genişlesin
        self.list_frame.columnconfigure(0, weight=1) # Treeview yatay genişlesin

        self.form_frame.columnconfigure(0, weight=1) # Entry'ler genişlesin
        # Diğer sütunların ağırlığı varsayılan (0) kalabilir

        # Verileri Yükle
        self.questions_data = []
        self.load_questions()
        self.populate_treeview()

        # Tema özel stilleri (isteğe bağlı)
        self.style.configure("Accent.TButton", foreground="white", background="#007bff") # Bootstrap primary rengi gibi


    def load_questions(self):
        """JSON dosyasından soruları yükler."""
        try:
            if os.path.exists(JSON_FILENAME):
                with open(JSON_FILENAME, 'r', encoding='utf-8') as f:
                    self.questions_data = json.load(f)
                    if not isinstance(self.questions_data, list):
                        messagebox.showerror("Load Error", f"{JSON_FILENAME} does not contain a valid JSON list.")
                        self.questions_data = []
            else:
                # Dosya yoksa boş liste ile başla
                self.questions_data = []
                print(f"'{JSON_FILENAME}' not found. Starting with an empty list.")
        except json.JSONDecodeError:
            messagebox.showerror("Load Error", f"Could not decode JSON from {JSON_FILENAME}. Please check the file format.")
            self.questions_data = []
        except Exception as e:
            messagebox.showerror("Load Error", f"An error occurred while loading questions: {e}")
            self.questions_data = []

    def save_questions(self):
        """Mevcut soru listesini JSON dosyasına kaydeder."""
        try:
            with open(JSON_FILENAME, 'w', encoding='utf-8') as f:
                # indent=4 ile daha okunabilir JSON formatı
                json.dump(self.questions_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Success", f"Questions successfully saved to {JSON_FILENAME}")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving questions: {e}")

    def populate_treeview(self):
        """Treeview'ı questions_data ile doldurur."""
        # Önce mevcut tüm öğeleri temizle
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)
        # Yeni verileri ekle
        for i, q_data in enumerate(self.questions_data):
            # Basit bir özet göster
            question_preview = q_data.get('question', 'N/A')[:50] + ('...' if len(q_data.get('question', '')) > 50 else '')
            correct_answer = q_data.get('correctAnswer', 'N/A')
            # iid (item ID) olarak index kullanmak seçimi kolaylaştırır
            self.question_tree.insert("", tk.END, iid=str(i), values=(question_preview, correct_answer))

    def on_tree_select(self, event=None):
        """Treeview'da bir öğe seçildiğinde formu doldurur."""
        selected_items = self.question_tree.selection()
        if not selected_items:
            self.clear_form() # Seçim kalkarsa formu temizle
            self.update_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            return

        selected_iid = selected_items[0]
        try:
            selected_index = int(selected_iid)
            if 0 <= selected_index < len(self.questions_data):
                q_data = self.questions_data[selected_index]

                self.question_text_var.set(q_data.get('question', ''))
                options = q_data.get('options', [])
                correct_answer = q_data.get('correctAnswer', '')

                # Seçenekleri ve doğru cevabı ayarla
                correct_index = -1
                for i in range(NUM_OPTIONS):
                    if i < len(options):
                        self.option_vars[i].set(options[i])
                        if options[i] == correct_answer:
                            correct_index = i
                    else:
                        self.option_vars[i].set("") # Eksikse boşalt

                self.correct_answer_var.set(correct_index)

                # Butonları etkinleştir
                self.update_button.config(state=tk.NORMAL)
                self.delete_button.config(state=tk.NORMAL)
            else:
                print(f"Error: Index {selected_index} out of range.")
                self.clear_form() # Hata durumunda temizle
                self.update_button.config(state=tk.DISABLED)
                self.delete_button.config(state=tk.DISABLED)

        except ValueError:
             print(f"Error: Invalid item ID selected: {selected_iid}")
             self.clear_form()
             self.update_button.config(state=tk.DISABLED)
             self.delete_button.config(state=tk.DISABLED)


    def clear_form(self, clear_selection=True):
        """Form alanlarını temizler."""
        self.question_text_var.set("")
        for var in self.option_vars:
            var.set("")
        self.correct_answer_var.set(-1) # Radyo buton seçimini kaldırır
        if clear_selection and self.question_tree.selection():
            self.question_tree.selection_remove(self.question_tree.selection()[0])
        self.question_text_entry.focus() # İmleci ilk alana getir
        # Butonları pasifleştir
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)

    def _validate_form(self):
        """Form girdilerini doğrular."""
        question = self.question_text_var.get().strip()
        if not question:
            messagebox.showwarning("Input Error", "Question text cannot be empty.")
            return None, None, None

        options = [var.get().strip() for var in self.option_vars]
        if not all(options): # Tüm seçeneklerin dolu olup olmadığını kontrol et
             messagebox.showwarning("Input Error", f"All {NUM_OPTIONS} options must be filled.")
             return None, None, None
        if len(set(options)) != NUM_OPTIONS: # Seçeneklerin benzersiz olup olmadığını kontrol et
            messagebox.showwarning("Input Error", f"All {NUM_OPTIONS} options must be unique.")
            return None, None, None

        correct_index = self.correct_answer_var.get()
        if correct_index < 0 or correct_index >= NUM_OPTIONS:
            messagebox.showwarning("Input Error", "You must select one correct answer.")
            return None, None, None

        correct_answer = options[correct_index]
        return question, options, correct_answer

    def add_question(self):
        """Formdaki verilerle yeni bir soru ekler."""
        question, options, correct_answer = self._validate_form()
        if question is None: # Doğrulama başarısız oldu
            return

        new_question = {
            "question": question,
            "options": options,
            "correctAnswer": correct_answer
        }
        self.questions_data.append(new_question)
        self.populate_treeview()
        self.clear_form(clear_selection=False) # Sadece formu temizle, seçimi değil
        messagebox.showinfo("Success", "New question added. Remember to save changes!")
        # Yeni eklenen öğeyi seçili hale getir (isteğe bağlı)
        new_index = len(self.questions_data) - 1
        self.question_tree.selection_set(str(new_index))
        self.question_tree.focus(str(new_index))
        self.question_tree.see(str(new_index)) # Görünür alana kaydır

    def update_question(self):
        """Seçili soruyu formdaki verilerle günceller."""
        selected_items = self.question_tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Error", "Please select a question to update.")
            return

        selected_iid = selected_items[0]
        try:
            selected_index = int(selected_iid)

            question, options, correct_answer = self._validate_form()
            if question is None: # Doğrulama başarısız oldu
                return

            updated_question = {
                "question": question,
                "options": options,
                "correctAnswer": correct_answer
            }

            self.questions_data[selected_index] = updated_question
            self.populate_treeview()
            # Güncellenen öğeyi tekrar seçili tut
            self.question_tree.selection_set(selected_iid)
            self.question_tree.focus(selected_iid)
            messagebox.showinfo("Success", "Question updated. Remember to save changes!")

        except (ValueError, IndexError):
             messagebox.showerror("Error", "Could not update the selected question. Selection might be invalid.")
             self.clear_form()


    def delete_question(self):
        """Seçili soruyu siler."""
        selected_items = self.question_tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Error", "Please select a question to delete.")
            return

        selected_iid = selected_items[0]
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected question?"):
            try:
                selected_index = int(selected_iid)
                del self.questions_data[selected_index]
                self.populate_treeview()
                self.clear_form() # Formu ve seçimi temizle
                messagebox.showinfo("Success", "Question deleted. Remember to save changes!")
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Could not delete the selected question. Selection might be invalid.")
                self.clear_form()


if __name__ == "__main__":
    # ThemedTk kullanarak temalı pencere oluştur
    root = ThemedTk(theme="adapta") # Başlangıç temasını burada da belirtebilirsiniz
    app = QuestionEditorApp(root)
    root.mainloop()
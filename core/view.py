import customtkinter as ctk
from post_gen import generate_post, save_on_history

ctk.set_default_color_theme("green")
ctk.set_appearance_mode("System")

class PostGen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PostGen")
        self.geometry("500x650+710+220")

        self.title_label = ctk.CTkLabel(self, text="PostGen", font=("Inter", 24, "bold"))
        self.title_label.pack(pady=10, fill="both")

        self.description = ctk.CTkLabel(
            self, 
            text="Gere posts para suas redes sociais com facilidade", 
            font=("Inter", 14, "bold"),
        )
        self.description.pack(pady=5, fill="both")

        self.entry_label = ctk.CTkLabel(self, text="Sobre qual assunto vamos falar hoje?", font=("Inter", 18))
        self.entry_label.pack(pady=10, fill="both")
        self.entry_input = ctk.CTkEntry(self, placeholder_text="> ", font=("Inter", 16), width=280)
        self.entry_input.pack(pady=5)
        self.entry_input.bind("<Control-v>", lambda e: None)

        self.generate_btn = ctk.CTkButton(self, text="Gerar Post", font=("Inter", 14, "bold"), command=self.generate_action)
        self.generate_btn.pack(pady=5)

        self.content_panel = ctk.CTkTextbox(self, width=380, height=300, font=("Inter", 14))
        self.content_panel.pack(pady=5)

        self.save_btn = ctk.CTkButton(self, text="Salvar Post", font=("Inter", 14, "bold"), command=self.save_action)
        self.save_btn.pack(pady=5)

        self.credits = ctk.CTkLabel(
            self, 
            text="Feito por muliroZ (https://github.com/muliroZ)", 
            font=("Inter", 12, "bold"), 
            text_color="#ffae00")
        self.credits.pack(side="bottom", pady=10)

        self.current_post = ""

    def generate_action(self):
        topic = self.entry_input.get()
        if not topic:
            return
        
        self.content_panel.delete("0.0", ctk.END)
        self.content_panel.insert("0.0", "Gerando post, aguarde...")
        self.content_panel.update()

        self.current_post = generate_post(topic)
        if self.current_post is None:
            self.content_panel.delete("0.0", ctk.END)
            self.content_panel.insert("0.0", "Erro ao criar post. Tente novamente. (caso persista, verifique sua chave do Gemini)")
            return

        self.content_panel.delete("0.0", ctk.END)
        self.content_panel.insert("0.0", self.current_post)

    def save_action(self):
        topic = self.entry_input.get()
        if topic and self.current_post:
            path = save_on_history(topic, self.current_post)
            self.content_panel.insert(ctk.END, f"\n\n[SISTEMA] Post salvo: {path}")

if __name__ == "__main__":
    app = PostGen()
    app.mainloop()

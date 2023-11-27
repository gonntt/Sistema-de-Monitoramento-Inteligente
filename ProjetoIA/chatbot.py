import tkinter as tk
import subprocess
from tkinter import scrolledtext
import spacy
from collections import Counter
import pandas as pd

arquivo_a_executar = 'sistem.py'
comando = ['python', arquivo_a_executar]

arquivo_a_executar2 = 'carne.py'
comando1 = ['python', arquivo_a_executar2]

arquivo_a_executar3 = 'queijofugi.py'
comando2 = ['python', arquivo_a_executar3]

arquivo_a_executar4 = 'Vinhos.py'
comando3 = ['python', arquivo_a_executar4]

class ChatGUI:
    def __init__(self, master):
        self.master = master
        master.title("ChatBot")

        self.nlp = spacy.load('pt_core_news_md')

        self.chat_display = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=50, height=20)
        self.chat_display.pack(expand=True, fill=tk.BOTH)

        self.user_input = tk.Entry(master, width=50)
        self.user_input.pack(expand=True, fill=tk.X)

        self.send_button = tk.Button(master, text="Enviar", command=self.send_message)
        self.send_button.pack()

        self.custom_data = {
            "oi": "Olá, eu sou O AGRICULTOR, me diga qual estocagem deseja realizar?Ex(sementes,vinhos,carnes ou queijos)",
            "sementes": "ok",
            "semente": "ok",
            "carne": "ok",
            "carnes": "ok",
            "queijo": "ok",
            "queijos": "ok",
            "queijos e fungos": "ok",
            "fungos": "ok, aba queijos temperados a fungos",
            "queij": "ok",
            "vinho": "ok",
            "vinhos": "ok",
            "vinhos ": "ok"
        }

        self.similarity_count = Counter()

    def send_message(self):
        user_text = self.user_input.get().strip()

        if not user_text:
            return

        self.user_input.delete(0, tk.END)

        response = self.get_custom_response(user_text)

        self.chat_display.insert(tk.END, "Você: {}\n".format(user_text))
        self.chat_display.insert(tk.END, "Bot: {}\n\n".format(response))
        self.chat_display.see(tk.END)

    def get_custom_response(self, user_text):
        self.similarity_count.clear()  # Limpa o contador de similaridades
        doc = self.nlp(user_text)

        for key, value in self.custom_data.items():
            key_doc = self.nlp(key)

            if key_doc.similarity(doc) > 0.3:
                self.similarity_count[key] += 1
                most_common_similarity = self.similarity_count.most_common(1)[0][0]

                self.verifica_contagem(most_common_similarity)

                if most_common_similarity == "sementes":
                    subprocess.Popen(comando)
                elif most_common_similarity == "semente":
                    subprocess.Popen(comando)
                elif most_common_similarity == "carne":
                    subprocess.Popen(comando1)
                elif most_common_similarity == "carnes":
                    subprocess.Popen(comando1)
                elif most_common_similarity == "queijo":
                    subprocess.Popen(comando2)
                elif most_common_similarity == "queijos":
                    subprocess.Popen(comando2)
                elif most_common_similarity == "queijos e fungos":
                    subprocess.Popen(comando2)
                elif most_common_similarity == "fungos":
                    subprocess.Popen(comando2)
                elif most_common_similarity == "queij":
                    subprocess.Popen(comando2)
                elif most_common_similarity == "vinho":
                    subprocess.Popen(comando3)
                elif most_common_similarity == "vinhos":
                    subprocess.Popen(comando3)
                self.salva_no_excel()
                return value

        return "Desculpe, eu não entendi."

    def verifica_contagem(self, palavra):
        if self.similarity_count[palavra] == 9:
            # Obtém a saída equivalente da palavra similar
            valor_correspondente = self.custom_data.get(palavra.lower(), "Saída padrão se não encontrada")
            
            # Adiciona a palavra similar ao custom_data com a saída equivalente
            self.custom_data[palavra.lower()] = valor_correspondente

    def salva_no_excel(self):
        df = pd.DataFrame(list(self.similarity_count.items()), columns=['Palavra Similar', 'Contagem'])
        df.to_excel('similarity_count.xlsx', index=False)

root = tk.Tk()
gui = ChatGUI(root)
root.mainloop()

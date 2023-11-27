import serial
import time
import requests
import numpy as np
import skfuzzy as fuzz
from tkinter import * 
from tkinter import ttk, simpledialog, messagebox 
import tkinter as tk
from skfuzzy import control as ctrl
import pandas as pd
import json


temperatura1 = ctrl.Antecedent(np.arange(0, 30,0.1), 'temperatura1')
temperatura2 = ctrl.Antecedent(np.arange(0, 30,0.1), 'temperatura2')
umidade1 = ctrl.Antecedent(np.arange(0, 90, 0.1), 'umidade1')
umidade2 = ctrl.Antecedent(np.arange(0, 90, 0.1), 'umidade2')
porta_serial = '/dev/ttyUSB0'
baudrate = 1200
ser = serial.Serial(porta_serial, baudrate, timeout=2)
nome_da_planilha = 'Planilha1'
arquivo_excel = 'Sementes.xlsx'


temperatura_ambiente = ctrl.Consequent(np.arange(0, 30, 0.1), 'temperatura_ambiente')
umidade_ambiente = ctrl.Consequent(np.arange(0, 90,0.1), 'umidade_ambiente')


temperatura1.automf(3)
temperatura2.automf(3)
umidade1.automf(3)
umidade2.automf(3)
temperatura_ambiente.automf(3)
umidade_ambiente.automf(3)


regra1 = ctrl.Rule(temperatura1['poor'] & temperatura2['poor'] , [temperatura_ambiente['average']])
regra2 = ctrl.Rule(temperatura1['good'] & temperatura2['good'] , [temperatura_ambiente['good']])
regra3 = ctrl.Rule(temperatura1['average'] & temperatura2['average'] , [temperatura_ambiente['good']])
regra4 = ctrl.Rule(temperatura1['good'] & temperatura2['average'] , [temperatura_ambiente['good']])
regra5 = ctrl.Rule(temperatura1['average'] & temperatura2['good'] , [temperatura_ambiente['good']])
regra6 = ctrl.Rule(temperatura1['poor'] & temperatura2['average'] , [temperatura_ambiente['average']])
regra7 = ctrl.Rule(temperatura1['average'] & temperatura2['poor'] , [temperatura_ambiente['average']])
regra8 = ctrl.Rule(umidade1['good'] & umidade2['good'] , [umidade_ambiente['good']])
regra9 = ctrl.Rule(umidade1['poor'] & umidade2['poor'] , [umidade_ambiente['average']])
regra10 = ctrl.Rule(umidade1['average'] & umidade2['average'] , [umidade_ambiente['good']])
regra11 = ctrl.Rule(umidade1['good'] & umidade2['average'] , [umidade_ambiente['good']])
regra12 = ctrl.Rule(umidade1['average'] & umidade2['good'] , [umidade_ambiente['good']])
regra13 = ctrl.Rule(umidade1['poor'] & umidade2['average'] , [umidade_ambiente['average']])
regra14  = ctrl.Rule(umidade1['average'] & umidade2['poor'] , [umidade_ambiente['average']])
nome_da_planilha = 'Planilha1'
dados_excel = pd.read_excel('Sementes.xlsx', sheet_name=nome_da_planilha)

sistema_fuzzy = ctrl.ControlSystem([regra1, regra2, regra3, regra4, regra5, regra6, regra7, regra8, regra9,regra10,regra11,regra12,regra13,regra14])


simulacao = ctrl.ControlSystemSimulation(sistema_fuzzy)







        


def calcular_saida_fuzzy():
    global dados_excel
    nome_da_planilha = 'Planilha1'
    dados_excel = pd.read_excel('Sementes.xlsx', sheet_name=nome_da_planilha)
    carregar_nomes_sementes()
    indice_semente1 = cb_sementes1.current()
    indice_semente2 = cb_sementes2.current()

    if 0 <= indice_semente1 < len(dados_excel) and 0 <= indice_semente2 < len(dados_excel):
        row1 = dados_excel.iloc[indice_semente1]
        row2 = dados_excel.iloc[indice_semente2]

        temperatura_desejada1 = row1['temperatura']
        umidade_desejada1 = row1['umidade']
        temperatura_desejada2 = row2['temperatura']
        umidade_desejada2 = row2['umidade']

        
        diferenca_temperatura = abs(temperatura_desejada1 - temperatura_desejada2)
        diferenca_umidade = abs(umidade_desejada1 - umidade_desejada2)

        if diferenca_temperatura > 14 or diferenca_umidade > 30:
            resultado_text.set("Não é possível criar temperatura ambiente ou umidade ambiente \n para essas sementes, devido à distancia numérica.\n"
                               "Pois, uma valor intermedio entre temperaturas muito distantes pode prejudicar as duas sementes.")
            return

        simulacao = ctrl.ControlSystemSimulation(sistema_fuzzy)

        simulacao.input['temperatura1'] = temperatura_desejada1
        simulacao.input['umidade1'] = umidade_desejada1
        simulacao.input['temperatura2'] = temperatura_desejada2
        simulacao.input['umidade2'] = umidade_desejada2
        simulacao.compute()

        temperatura_ambiente_ideal = simulacao.output['temperatura_ambiente']
        umidade_ambiente_ideal = simulacao.output['umidade_ambiente']
        
         

        leitura_serial = ser.readline().decode('latin-1').rstrip()
        leitura_serial = leitura_serial.strip()
        print("Leitura Serial:", leitura_serial)

        if "{" in leitura_serial and "}" in leitura_serial:
            try:
                data = json.loads(leitura_serial)
                humidity = data["humidity"]
                temperature = data["temperature"]
                print(f"Umidade: {humidity}%")
                print(f"Temperatura: {temperature}°C")
            except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}")
        else:
                        print("String não contém uma estrutura JSON válida")

        if "\"humidity\"" in leitura_serial and "\"temperature\"" in leitura_serial:
            
            data = json.loads(leitura_serial)
            
            humidity = data["humidity"]
            temperature = data["temperature"]
            
            print(f"Umidade: {humidity}%")
            print(f"Temperatura: {temperature}°C")
          
            faixa_temperatura = temperature - temperatura_ambiente_ideal
            faixa_umidade = humidity - umidade_ambiente_ideal

            if (
                faixa_temperatura == 0
                or  faixa_umidade == 0
            ):
                resultado_text.set(
                    "O ambiente já estar em temperatura e umidade ideal"
                )
            else:
                resultado_text.set(
                    f"Temperatura ideal para o ambiente: {temperatura_ambiente_ideal:.2f}\n"
                    f"Umidade ideal para o ambiente: {umidade_ambiente_ideal:.2f}\n"
                    f"altere o Acondicionado em : {faixa_temperatura:.2f}\n"
                   f"altere o umidificador em : {faixa_umidade:.2f}"
                )
        else:
            resultado_text.set(
                               f"Temperatura ideal para o ambiente: {temperatura_ambiente_ideal:.2f}\n"
                               f"Umidade ideal para o ambiente: {umidade_ambiente_ideal:.2f}\n"
                               f"Não é possível Comparar com a temperatura e umidade do ambiente pela osilação de valores no sensor"
                               )
    else:
        resultado_text.set("Índice fora da planilha.")
        
        
def carregar_nomes_sementes():
    global listSementes1, listSementes2
    dados_excel = pd.read_excel('Sementes.xlsx', sheet_name=nome_da_planilha)
    listSementes1 = dados_excel["sementes"].unique()
    listSementes2 = dados_excel["sementes"].unique()
    cb_sementes1['values'] = listSementes1
    cb_sementes2['values'] = listSementes2





def adicionar_nova_semente():
    nova_janela = tk.Toplevel(janela)
    nova_janela.title("Adicionar Nova Semente")

    tk.Label(nova_janela, text="Nome da Semente:").grid(row=0, column=0)
    nome_semente_entry = tk.Entry(nova_janela)
    nome_semente_entry.grid(row=0, column=1)

    tk.Label(nova_janela, text="Temperatura Ideal:").grid(row=1, column=0)
    temp_ideal_entry = tk.Entry(nova_janela)
    temp_ideal_entry.grid(row=1, column=1)

    tk.Label(nova_janela, text="Umidade Ideal:").grid(row=2, column=0)
    umidade_ideal_entry = tk.Entry(nova_janela)
    umidade_ideal_entry.grid(row=2, column=1)

    def processar_input():
        nome_semente = nome_semente_entry.get()
        temp_ideal = float(temp_ideal_entry.get())
        umidade_ideal = float(umidade_ideal_entry.get())

        nova_semente = pd.DataFrame({"sementes": [nome_semente], "temperatura": [temp_ideal], "umidade": [umidade_ideal]})
        global dados_excel
        dados_excel = pd.concat([dados_excel, nova_semente], ignore_index=True)

        listSementes1 = dados_excel["sementes"].unique()
        listSementes2 = dados_excel["sementes"].unique()
        cb_sementes1['values'] = listSementes1
        cb_sementes2['values'] = listSementes2
        dados_excel.to_excel('Sementes.xlsx', sheet_name=nome_da_planilha, index=True)
        carregar_nomes_sementes()
        messagebox.showinfo("Sucesso", f"A semente {nome_semente} foi adicionada com sucesso!")

        nova_janela.destroy()
    tk.Button(nova_janela, text="Adicionar Semente", command=processar_input).grid(row=3, columnspan=2, pady=10)









print(dados_excel.columns)

sementes = dados_excel["sementes"]
listSementes1 = sementes.unique()
listSementes2 = sementes.unique()
janela = Tk()
janela.title("Sistema de Gerenciamento")
janela.geometry("800x500")
lb_sementes1 = tk.Label(janela, text="Sementes")
cb_sementes1 = ttk.Combobox(janela, values=listSementes1)
lb_sementes2 = tk.Label(janela, text="Sementes")
cb_sementes2 = ttk.Combobox(janela, values=listSementes2)
calcular_button = tk.Button(janela, text="Calcular Saída Fuzzy", command=calcular_saida_fuzzy)
resultado_text = tk.StringVar()
resultado_label = tk.Label(janela, textvariable=resultado_text)
lb_sementes1.pack()
cb_sementes1.pack()
lb_sementes2.pack()
cb_sementes2.pack()
calcular_button.pack()
resultado_label.pack()

btn_adicionar_semente = tk.Button(janela, text="Adicionar Nova Semente", command=adicionar_nova_semente)
btn_adicionar_semente.pack(side="bottom", pady=10)

janela.mainloop()


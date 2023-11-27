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
nome_da_planilha = 'Planilha2'
dados_excel = pd.read_excel('Carnes.xlsx', sheet_name=nome_da_planilha)

temperatura_ambiente = ctrl.Consequent(np.arange(0, 30, 0.1), 'temperatura_ambiente')
umidade_ambiente = ctrl.Consequent(np.arange(0, 90,0.1), 'umidade_ambiente')


temperatura1.automf(3)
temperatura2.automf(3)
umidade1.automf(3)
umidade2.automf(3)
temperatura_ambiente.automf(3)
umidade_ambiente.automf(3)


regra1 = ctrl.Rule(temperatura1['poor'] & temperatura2['poor'] , [temperatura_ambiente['poor']])
regra2 = ctrl.Rule(temperatura1['good'] & temperatura2['good'] , [temperatura_ambiente['average']])
regra3 = ctrl.Rule(temperatura1['average'] & temperatura2['average'] , [temperatura_ambiente['poor']])
regra4 = ctrl.Rule(temperatura1['good'] & temperatura2['average'] , [temperatura_ambiente['average']])
regra5 = ctrl.Rule(temperatura1['average'] & temperatura2['good'] , [temperatura_ambiente['average']])
regra6 = ctrl.Rule(temperatura1['poor'] & temperatura2['average'] , [temperatura_ambiente['poor']])
regra7 = ctrl.Rule(temperatura1['average'] & temperatura2['poor'] , [temperatura_ambiente['poor']])
regra8 = ctrl.Rule(umidade1['good'] & umidade2['good'] , [umidade_ambiente['good']])
regra9 = ctrl.Rule(umidade1['poor'] & umidade2['poor'] , [umidade_ambiente['average']])
regra10 = ctrl.Rule(umidade1['average'] & umidade2['average'] , [umidade_ambiente['good']])
regra11 = ctrl.Rule(umidade1['good'] & umidade2['average'] , [umidade_ambiente['good']])
regra12 = ctrl.Rule(umidade1['average'] & umidade2['good'] , [umidade_ambiente['good']])
regra13 = ctrl.Rule(umidade1['poor'] & umidade2['average'] , [umidade_ambiente['average']])
regra14  = ctrl.Rule(umidade1['average'] & umidade2['poor'] , [umidade_ambiente['average']])
nome_da_planilha = 'Planilha2'
dados_excel = pd.read_excel('Carnes.xlsx', sheet_name=nome_da_planilha)

sistema_fuzzy = ctrl.ControlSystem([regra1, regra2, regra3, regra4, regra5, regra6, regra7, regra8, regra9,regra10,regra11,regra12,regra13,regra14])


simulacao = ctrl.ControlSystemSimulation(sistema_fuzzy)







        


def calcular_saida_fuzzy():
    global dados_excel
    nome_da_planilha = 'Planilha2'
    dados_excel = pd.read_excel('Carnes.xlsx', sheet_name=nome_da_planilha)

    indice_carne1 = cb_carne1.current()
    indice_carne2 = cb_carne2.current()

    if 0 <= indice_carne1 < len(dados_excel) and 0 <= indice_carne2 < len(dados_excel):
        row1 = dados_excel.iloc[indice_carne1]
        row2 = dados_excel.iloc[indice_carne2]

        temperatura_desejada1 = row1['temperatura']
        umidade_desejada1 = row1['umidade']
        temperatura_desejada2 = row2['temperatura']
        umidade_desejada2 = row2['umidade']

        
     

      

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
        
        

def carregar_nomes_carne():
    global listCarne1, listCarne2
    listCarne1 = dados_excel["carnes"].unique()
    listCarne2 = dados_excel["carnes"].unique()
    cb_carne1['values'] = listCarne1
    cb_carne2['values'] = listCarne2


def adicionar_nova_carne():
    nova_janela = tk.Toplevel(janela)
    nova_janela.title("Adicionar Nova Carne")

    tk.Label(nova_janela, text="Nome da Carne:").grid(row=0, column=0)
    nome_carne_entry = tk.Entry(nova_janela)
    nome_carne_entry.grid(row=0, column=1)

    tk.Label(nova_janela, text="Temperatura Ideal:").grid(row=1, column=0)
    temp_ideal_entry = tk.Entry(nova_janela)
    temp_ideal_entry.grid(row=1, column=1)

    tk.Label(nova_janela, text="Umidade Ideal:").grid(row=2, column=0)
    umidade_ideal_entry = tk.Entry(nova_janela)
    umidade_ideal_entry.grid(row=2, column=1)

    def processar_input():
        nome_carne = nome_carne_entry.get()
        temp_ideal = float(temp_ideal_entry.get())
        umidade_ideal = float(umidade_ideal_entry.get())

        nova_carne = pd.DataFrame({"carnes": [nome_carne], "temperatura": [temp_ideal], "umidade": [umidade_ideal]})
        global dados_excel
        dados_excel = pd.concat([dados_excel, nova_carne], ignore_index=True)

        listCarne1 = dados_excel["carnes"].unique()
        listCarne2 = dados_excel["carnes"].unique()
        cb_carne1['values'] = listCarne1
        cb_carne2['values'] = listCarne2
        dados_excel.to_excel('Carnes.xlsx', sheet_name=nome_da_planilha, index=False)
        messagebox.showinfo("Sucesso", f"A carne {nome_carne} foi adicionada com sucesso!")

        nova_janela.destroy()

    tk.Button(nova_janela, text="Adicionar Carne", command=processar_input).grid(row=3, columnspan=2, pady=10)
    carregar_nomes_carne()









print(dados_excel.columns)

carnes = dados_excel["carnes"]
listCarne1 = carnes.unique()
listCarne2 = carnes.unique()
janela = Tk()
janela.title("Sistema de Gerenciamento")
janela.geometry("800x500")
lb_carne1 = tk.Label(janela, text="Carnes",)
cb_carne1 = ttk.Combobox(janela, values=listCarne1,width=40)
lb_carne2 = tk.Label(janela, text="Carnes")
cb_carne2 = ttk.Combobox(janela, values=listCarne2,width=40)
calcular_button = tk.Button(janela, text="Calcular Saída Fuzzy", command=calcular_saida_fuzzy)
resultado_text = tk.StringVar()
resultado_label = tk.Label(janela, textvariable=resultado_text)
lb_carne1.pack()
cb_carne1.pack()
lb_carne2.pack()
cb_carne2.pack()
calcular_button.pack()
resultado_label.pack()

btn_adicionar_carne = tk.Button(janela, text="Adicionar Nova Carne", command=adicionar_nova_carne)
btn_adicionar_carne.pack(side="bottom", pady=10)

janela.mainloop()


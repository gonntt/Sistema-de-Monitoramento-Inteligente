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
nome_da_planilha = 'Planilha3'
arquivo_excel = 'QueijosFungos.xlsx'


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
nome_da_planilha = 'Planilha3'
dados_excel = pd.read_excel('QueijosFungos.xlsx', sheet_name=nome_da_planilha)

sistema_fuzzy = ctrl.ControlSystem([regra1, regra2, regra3, regra4, regra5, regra6, regra7, regra8, regra9,regra10,regra11,regra12,regra13,regra14])


simulacao = ctrl.ControlSystemSimulation(sistema_fuzzy)







        


def calcular_saida_fuzzy():
    global dados_excel
    nome_da_planilha = 'Planilha3'
    dados_excel = pd.read_excel('QueijosFungos.xlsx', sheet_name=nome_da_planilha)
    carregar_nomes_queijo()
    indice_queijo1 = cb_queijo1.current()
    indice_queijo2 = cb_queijo2.current()

    if 0 <= indice_queijo1 < len(dados_excel) and 0 <= indice_queijo2 < len(dados_excel):
        row1 = dados_excel.iloc[indice_queijo1]
        row2 = dados_excel.iloc[indice_queijo2]

        temperatura_desejada1 = row1['temperatura']
        umidade_desejada1 = row1['umidade']
        temperatura_desejada2 = row2['temperatura']
        umidade_desejada2 = row2['umidade']

        
        diferenca_temperatura = abs(temperatura_desejada1 - temperatura_desejada2)
        diferenca_umidade = abs(umidade_desejada1 - umidade_desejada2)

        if diferenca_temperatura > 10 or diferenca_umidade > 20:
            resultado_text.set("Não é possível criar temperatura ambiente ou umidade ambiente \n para essas queijo, devido à distancia numérica.\n"
                               "Pois, uma valor intermedio entre temperaturas muito distantes pode prejudicar prolongar o prazo da criaçao do Fungo.")
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
        
        
def carregar_nomes_queijo():
    global listQueijos1, listQueijos2
    dados_excel = pd.read_excel('QueijosFungos.xlsx', sheet_name=nome_da_planilha)
    listQueijos1 = dados_excel["Queijo"].unique()
    listQueijos2 = dados_excel["Queijo"].unique()
    cb_queijo1['values'] = listQueijos1
    cb_queijo2['values'] = listQueijos2





def adicionar_nova_queijo():
    nova_janela = tk.Toplevel(janela)
    nova_janela.title("Adicionar Novo Queijo_Fungo")

    tk.Label(nova_janela, text="Nome da Queijo:").grid(row=0, column=0)
    nome_queijo_entry = tk.Entry(nova_janela)
    nome_queijo_entry.grid(row=0, column=1)

    tk.Label(nova_janela, text="Temperatura Ideal:").grid(row=1, column=0)
    temp_ideal_entry = tk.Entry(nova_janela)
    temp_ideal_entry.grid(row=1, column=1)

    tk.Label(nova_janela, text="Umidade Ideal:").grid(row=2, column=0)
    umidade_ideal_entry = tk.Entry(nova_janela)
    umidade_ideal_entry.grid(row=2, column=1)

    def processar_input():
        nome_queijo = nome_queijo_entry.get()
        temp_ideal = float(temp_ideal_entry.get())
        umidade_ideal = float(umidade_ideal_entry.get())

        nova_queijo = pd.DataFrame({"Queijo": [nome_queijo], "temperatura": [temp_ideal], "umidade": [umidade_ideal]})
        global dados_excel
        dados_excel = pd.concat([dados_excel, nova_queijo], ignore_index=True)

        listQueijos1 = dados_excel["Queijo"].unique()
        listQueijos2 = dados_excel["Queijo"].unique()
        cb_queijo1['values'] = listQueijos1
        cb_queijo2['values'] = listQueijos2
        dados_excel.to_excel('QueijosFungos.xlsx', sheet_name=nome_da_planilha, index=True)
        carregar_nomes_queijo()
        messagebox.showinfo("Sucesso", f"O queijo {nome_queijo} foi adicionada com sucesso!")

        nova_janela.destroy()
    tk.Button(nova_janela, text="Adicionar Queijo", command=processar_input).grid(row=3, columnspan=2, pady=10)









print(dados_excel.columns)

queijo = dados_excel["Queijo"]
listQueijos1 = queijo.unique()
listQueijos2 = queijo.unique()
janela = Tk()
janela.title("Sistema de Gerenciamento")
janela.geometry("800x500")
lb_queijo1 = tk.Label(janela, text="Queijos")
cb_queijo1 = ttk.Combobox(janela, values=listQueijos1)
lb_queijo2 = tk.Label(janela, text="Queijos")
cb_queijo2 = ttk.Combobox(janela, values=listQueijos2)
calcular_button = tk.Button(janela, text="Calcular Saída Fuzzy", command=calcular_saida_fuzzy)
resultado_text = tk.StringVar()
resultado_label = tk.Label(janela, textvariable=resultado_text)
lb_queijo1.pack()
cb_queijo1.pack()
lb_queijo2.pack()
cb_queijo2.pack()
calcular_button.pack()
resultado_label.pack()

btn_adicionar_queijo = tk.Button(janela, text="Adicionar Novo Queijo", command=adicionar_nova_queijo)
btn_adicionar_queijo.pack(side="bottom", pady=10)

janela.mainloop()


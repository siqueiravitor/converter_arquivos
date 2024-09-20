import tkinter as tk
from tkinter import filedialog, messagebox
import os
import cx_Oracle
import shutil

def selecionar_diretorios_entrada():
    diretorios = filedialog.askdirectory()
    if diretorios:
        entry_entrada.delete(0, tk.END)
        entry_entrada.insert(0, diretorios)


def selecionar_diretorio_saida():
    diretorio = filedialog.askdirectory()
    if diretorio:
        entry_saida.delete(0, tk.END)
        entry_saida.insert(0, diretorio)


def conectar_banco():
    global user, senha, dsn, conn

    user = entry_usuario.get()
    senha = entry_senha.get()
    dsn = entry_dsn.get()

    if not user or not dsn:
        return messagebox.showerror("Campos vazios", "Por favor, preencha todos os campos de conexão.")

    conn = None
    try:
        conn = cx_Oracle.connect(user, senha, dsn)
        messagebox.showinfo("Sucesso", "Conexão bem-sucedida!")
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")

def renomear_arquivos():
    diretorios_entrada = entry_entrada.get().split(';')
    diretorio_saida = entry_saida.get()
    modo_selecionado = var.get()
    arquivos_nao_encontrados = []

    select = "nomearquivo"
    table = "documentos"
    where = "nome"

    if not diretorios_entrada or not diretorio_saida:
        return messagebox.showerror("Campos vazios", "Por favor, preencha todos os campos.")

    try:
        cursor = conn.cursor()

        for diretorio_entrada in diretorios_entrada: # Pesquisa os arquivos dentro da pasta
            for root, dirs, files in os.walk(diretorio_entrada): # Caso haja subpastas, a mesma é percorrida para buscar os documentos dentro dela
                if modo_selecionado == 1: # Copiar todos os arquivos para uma pasta única
                    pasta_saida = diretorio_saida
                elif modo_selecionado == 2: # Preservar a estrutura original de pastas
                    nome_pasta = os.path.relpath(root, diretorio_entrada)
                    pasta_saida = os.path.join(diretorio_saida, nome_pasta)

                if not os.path.exists(pasta_saida):
                    os.makedirs(pasta_saida)

                for filename in files:
                    filename_clean = filename.replace(' (1)', '') #remove " (1)" do nome do arquivo, caso haja
                    caminho_entrada = os.path.join(root, filename)

                    query = f"SELECT {select} FROM {table} WHERE {where} = :1 ORDER BY created_at"
                    cursor.execute(query, [filename_clean])

                    result = cursor.fetchone()
                    if result:
                        novo_nome = result[0]
                        caminho_saida = os.path.join(pasta_saida, novo_nome)
                    else:
                        arquivos_nao_encontrados.append('Arquivo: ' + filename)
                        arquivos_nao_encontrados.append('Pasta de origem: ' + pasta_saida)
                        arquivos_nao_encontrados.append('-')
                        caminho_saida = os.path.join(pasta_saida, filename_clean)

                    shutil.copy(caminho_entrada, caminho_saida)

        if arquivos_nao_encontrados:
            with open(os.path.join(diretorio_saida, 'arquivos_nao_encontrados.txt'), 'w') as f:
                for arquivo in arquivos_nao_encontrados:
                    f.write(f"{arquivo}\n")

        messagebox.showinfo("Sucesso", "Arquivos copiados com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
    finally:
        if cursor:
            cursor.close()

def mover_arquivos():
    diretorios_entrada = entry_entrada.get().split(';')
    diretorio_saida = entry_saida.get()
    modo_selecionado = var.get()

    if not diretorios_entrada or not diretorio_saida:
        messagebox.showerror("Campos vazios", "Por favor, informe os diretórios de entrada e saída.")
        return

    try:
        for diretorio_entrada in diretorios_entrada: # Pesquisa os arquivos dentro da pasta
            for root, dirs, files in os.walk(diretorio_entrada): # Caso haja subpastas, a mesma é percorrida para buscar os documentos dentro dela
                if modo_selecionado == 1: # Copiar todos os arquivos para uma pasta única
                    pasta_saida = diretorio_saida
                elif modo_selecionado == 2: # Preservar a estrutura original de pastas
                    nome_pasta = os.path.relpath(root, diretorio_entrada)
                    pasta_saida = os.path.join(diretorio_saida, nome_pasta)

                if not os.path.exists(pasta_saida):
                    os.makedirs(pasta_saida)

                for filename in files:
                    filename_clean = filename.replace(' (1)', '') #remove " (1)" do nome do arquivo, caso haja
                    caminho_entrada = os.path.join(root, filename)
                    caminho_saida = os.path.join(pasta_saida, filename_clean)

                    shutil.copy(caminho_entrada, caminho_saida)


        messagebox.showinfo("Sucesso", "Arquivos copiados com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")


# Configuração da interface gráfica
root = tk.Tk()
root.title("Renomear/Mover Arquivos")
root.resizable(False, False)

var = tk.IntVar(value=1)  # Variável para armazenar a seleção dos Radiobuttons

# Campos de conexão
frame_usuario = tk.Frame(root)
frame_usuario.pack(anchor=tk.W, padx=10, pady=5)
tk.Label(frame_usuario, anchor=tk.W, width=15, text="Usuário:").pack(side=tk.LEFT)
entry_usuario = tk.Entry(frame_usuario, width=30)
entry_usuario.pack(side=tk.LEFT, fill=tk.X, expand=True)

frame_senha = tk.Frame(root)
frame_senha.pack(anchor=tk.W, padx=10, pady=5)
tk.Label(frame_senha, anchor=tk.W, width=15, text="Senha:").pack(side=tk.LEFT)
entry_senha = tk.Entry(frame_senha, width=30, show="*")
entry_senha.pack()

frame_dsn = tk.Frame(root)
frame_dsn.pack(anchor=tk.W, padx=10, pady=5)
tk.Label(frame_dsn, anchor=tk.W, width=15, text="DSN:").pack(side=tk.LEFT)
entry_dsn = tk.Entry(frame_dsn, width=30)
entry_dsn.pack()

btn_conectar = tk.Button(root, text="Conectar", width=41, command=conectar_banco)
btn_conectar.pack(padx=10, pady=10, anchor=tk.W,)

# Campos de seleção de diretórios
frame_entrada = tk.Frame(root)
frame_entrada.pack(anchor=tk.W, fill=tk.X, padx=10, pady=5)
tk.Label(frame_entrada, anchor=tk.W, width=20, text="Diretórios de Entrada:").pack(side=tk.LEFT)
entry_entrada = tk.Entry(frame_entrada, width=50)
entry_entrada.pack(side=tk.LEFT, fill=tk.X, expand=True)
btn_entrada = tk.Button(frame_entrada, text="Selecionar", command=selecionar_diretorios_entrada)
btn_entrada.pack(side=tk.LEFT, padx=10)

frame_saida = tk.Frame(root)
frame_saida.pack(anchor=tk.W, fill=tk.X, padx=10, pady=5)
tk.Label(frame_saida, anchor=tk.W, width=20, text="Diretórios de Saída:").pack(side=tk.LEFT)
entry_saida = tk.Entry(frame_saida, width=50)
entry_saida.pack(side=tk.LEFT, fill=tk.X, expand=True)
btn_entrada = tk.Button(frame_saida, text="Selecionar", command=selecionar_diretorio_saida)
btn_entrada.pack(side=tk.LEFT, padx=10)

# Radiobuttons para selecionar o modo de cópia
frame_radio = tk.Frame(root)
frame_radio.pack(pady=10)

radio_1 = tk.Radiobutton(frame_radio, text="Copiar para uma única pasta", variable=var, value=1, padx=10)
radio_2 = tk.Radiobutton(frame_radio, text="Manter a estrutura de pastas", variable=var, value=2, padx=10)

radio_1.pack(side=tk.LEFT, padx=10)
radio_2.pack(side=tk.LEFT, padx=10)

# Botão para iniciar a renomeação dos arquivos
frame_botoes = tk.Frame(root)
frame_botoes.pack(anchor=tk.W, fill=tk.X, pady=10)

btn_converter = tk.Button(frame_botoes, text="Mover arquivos", width=30, command=mover_arquivos)
btn_converter.pack(side=tk.LEFT, padx=10)

btn_converter = tk.Button(frame_botoes, text="Renomear arquivos", width=30, command=renomear_arquivos)
btn_converter.pack(side=tk.RIGHT, padx=10)


root.mainloop()

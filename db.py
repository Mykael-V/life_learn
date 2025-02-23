import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Conectar ao banco de dados
def conectar():
    return sqlite3.connect("life_learn.db")

# Criar tabelas
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        data TEXT,
        qtd_polichinelos INTEGER,
        tempo INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        data TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    """)

    conn.commit()
    conn.close()

# Verificar ou criar usuário
def verificar_usuario(nome):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM usuarios WHERE nome = ?", (nome,))
    usuario = cursor.fetchone()

    if usuario:
        usuario_id = usuario[0]
    else:
        cursor.execute("INSERT INTO usuarios (nome) VALUES (?)", (nome,))
        usuario_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return usuario_id

# Salvar progresso no histórico
def salvar_progresso(usuario_id, qtd_polichinelos, tempo):
    conn = conectar()
    cursor = conn.cursor()

    data_atual = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO historico (usuario_id, data, qtd_polichinelos, tempo)
    VALUES (?, ?, ?, ?)
    """, (usuario_id, data_atual, qtd_polichinelos, tempo))

    conn.commit()
    conn.close()

# Registrar login
def registrar_login(usuario_id):
    conn = conectar()
    cursor = conn.cursor()

    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO logins (usuario_id, data)
    VALUES (?, ?)
    """, (usuario_id, data_atual))

    conn.commit()
    conn.close()

# Mostrar histórico do usuário
def mostrar_historico(usuario_id):
    conn = conectar()
    df = pd.read_sql_query("""
    SELECT data, qtd_polichinelos, tempo FROM historico
    WHERE usuario_id = ?
    """, conn, params=(usuario_id,))

    conn.close()
    return df

# Mostrar gráfico de evolução
def mostrar_grafico(usuario_id):
    df = mostrar_historico(usuario_id)

    # Configurar estilo do gráfico (preto e amarelo)
    plt.style.use('dark_background')
    plt.rcParams['axes.facecolor'] = '#000000'
    plt.rcParams['axes.edgecolor'] = '#ffcc00'
    plt.rcParams['axes.labelcolor'] = '#ffcc00'
    plt.rcParams['text.color'] = '#ffcc00'
    plt.rcParams['xtick.color'] = '#ffcc00'
    plt.rcParams['ytick.color'] = '#ffcc00'

    if df.empty:
        print("Nenhum dado para exibir.")
        return

    # Converter datas e agrupar por dia
    df["data"] = pd.to_datetime(df["data"]).dt.date
    df_agrupado = df.groupby("data")["qtd_polichinelos"].max().reset_index()

    # Criar dias sequenciais (ex: até 7 dias)
    dias = [f"Dia {i+1}" for i in range(7)]
    valores = [df_agrupado[df_agrupado.index == i]["qtd_polichinelos"].values[0] 
               if i < len(df_agrupado) else 0 for i in range(7)]

    # Configurar o gráfico
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(dias, valores, color='#ffcc00', alpha=0.8)

    # Adicionar mensagem nos dias sem registro
    for i, bar in enumerate(bars):
        if valores[i] == 0:
            bar.set_color('#000000')  # Barras invisíveis
            ax.text(i, 1, "Continue jogando\npara evoluir!", 
                    ha='center', va='bottom', color='#ffcc00', fontsize=10)

    # Ajustes finais
    plt.title("Sua Evolução de Polichinelos", fontsize=16, pad=20)
    plt.xlabel("Dias", fontsize=12)
    plt.ylabel("Melhor Repetição", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Ranking pessoal
def ranking_pessoal(usuario_id):
    conn = conectar()
    cursor = conn.cursor()

    # Pegar a data atual (sem hora)
    data_atual = datetime.now().strftime("%Y-%m-%d")

    # Buscar a melhor repetição do dia atual
    cursor.execute("""
    SELECT MAX(qtd_polichinelos) as melhor_repeticao
    FROM historico
    WHERE usuario_id = ? AND DATE(data) = ?
    """, (usuario_id, data_atual))

    resultado = cursor.fetchone()
    conn.close()

    if resultado and resultado[0] is not None:
        return resultado[0]  # Retorna a melhor repetição do dia
    else:
        return None  # Nenhum registro no dia atual

# Ranking geral
def ranking_geral():
    conn = conectar()
    df = pd.read_sql_query("""
    SELECT u.nome, MAX(h.qtd_polichinelos) as melhor_repeticao
    FROM historico h
    JOIN usuarios u ON h.usuario_id = u.id
    GROUP BY u.nome
    ORDER BY melhor_repeticao DESC
    LIMIT 5
    """, conn)

    conn.close()
    return df

# Criar tabelas ao iniciar
criar_tabelas()
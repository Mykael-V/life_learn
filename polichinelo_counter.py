import cv2

import mediapipe as mp

import math

import time

import pandas as pd

import matplotlib.pyplot as plt

from db import salvar_progresso, ranking_pessoal, ranking_geral

import tkinter as tk

from tkinter import ttk



pose = mp.solutions.pose

Pose = pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5)

draw = mp.solutions.drawing_utils



def mostrar_grafico(usuario_id):

    from db import mostrar_historico  # Importação local para evitar dependência circular



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



def mostrar_ranking_pessoal(usuario_id):

    # Buscar a melhor repetição do dia atual

    melhor_repeticao = ranking_pessoal(usuario_id)



    # Criar uma janela para exibir o ranking pessoal

    ranking_window = tk.Tk()

    ranking_window.title("Ranking Pessoal")

    ranking_window.geometry("400x200")

    ranking_window.resizable(False, False)

    ranking_window.configure(bg="#000000")  # Fundo preto



    # Estilo para os botões e labels

    style = ttk.Style()

    style.configure("TButton", font=("Arial", 12), padding=10, background="#ffcc00", foreground="#000000")  # Botão amarelo

    style.configure("TLabel", font=("Arial", 12), background="#000000", foreground="#ffcc00")  # Texto amarelo



    # Adicionar conteúdo à janela

    if melhor_repeticao:

        label = ttk.Label(ranking_window, text=f"Melhor repetição hoje: {melhor_repeticao} polichinelos", style="TLabel")

        label.pack(pady=20)

    else:

        label = ttk.Label(ranking_window, text="Continue logando diariamente para continuar vendo sua evolução.", style="TLabel")

        label.pack(pady=20)



    # Botão para ver o ranking geral

    btn_ranking_geral = ttk.Button(ranking_window, text="Ver Ranking Geral", style="TButton", command=lambda: mostrar_ranking_geral(ranking_window))

    btn_ranking_geral.pack(pady=10)



    ranking_window.mainloop()



def mostrar_ranking_geral(janela_anterior):

    # Fechar a janela anterior

    janela_anterior.destroy()



    # Buscar o ranking geral (apenas os 5 melhores)

    df_geral = ranking_geral().head(5)



    # Criar uma nova janela para exibir o ranking geral

    ranking_geral_window = tk.Tk()

    ranking_geral_window.title("Ranking Geral")

    ranking_geral_window.geometry("400x300")

    ranking_geral_window.resizable(False, False)

    ranking_geral_window.configure(bg="#000000")  # Fundo preto



    # Estilo para os botões e labels

    style = ttk.Style()

    style.configure("TButton", font=("Arial", 12), padding=10, background="#ffcc00", foreground="#000000")  # Botão amarelo

    style.configure("TLabel", font=("Arial", 12), background="#000000", foreground="#ffcc00")  # Texto amarelo



    # Adicionar conteúdo à janela

    label_titulo = ttk.Label(ranking_geral_window, text="Ranking Geral", style="TLabel", font=("Arial", 16, "bold"))

    label_titulo.pack(pady=10)



    # Exibir o ranking geral

    texto_ranking = "\n".join([f"{i+1}. {row['nome']}: {row['melhor_repeticao']} polichinelos" for i, row in df_geral.iterrows()])

    label_ranking = ttk.Label(ranking_geral_window, text=texto_ranking, style="TLabel")

    label_ranking.pack(pady=10)



    # Botão para voltar à seleção de exercícios

    btn_voltar = ttk.Button(ranking_geral_window, text="Voltar", style="TButton", command=ranking_geral_window.destroy)

    btn_voltar.pack(pady=10)



    ranking_geral_window.mainloop()



def contar_polichinelos(usuario_id):  # Agora recebe o ID do usuário

    from telas.selecao_exercicios import abrir_tela_selecao



    print("Iniciando contagem de polichinelos...")

    video = cv2.VideoCapture(0)

    if not video.isOpened():

        print("Erro: A câmera não pôde ser acessada.")

        return



    contador = 0

    check = True

    start_time = None  # Cronômetro só começa quando as mãos estiverem rentes ao corpo

    contador_inicial = 3  # Contador de 3 segundos para iniciar o exercício



    while True:

        success, img = video.read()

        if not success:

            print("Erro na captura da câmera.")

            break



        videoRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = Pose.process(videoRGB)

        points = results.pose_landmarks

        draw.draw_landmarks(img, points, pose.POSE_CONNECTIONS)

        h, w, _ = img.shape



        if points:

            peDY = int(points.landmark[pose.PoseLandmark.RIGHT_FOOT_INDEX].y * h)

            peDX = int(points.landmark[pose.PoseLandmark.RIGHT_FOOT_INDEX].x * w)

            peEY = int(points.landmark[pose.PoseLandmark.LEFT_FOOT_INDEX].y * h)

            peEX = int(points.landmark[pose.PoseLandmark.LEFT_FOOT_INDEX].x * w)

            moDY = int(points.landmark[pose.PoseLandmark.RIGHT_INDEX].y * h)

            moDX = int(points.landmark[pose.PoseLandmark.RIGHT_INDEX].x * w)

            moEY = int(points.landmark[pose.PoseLandmark.LEFT_INDEX].y * h)

            moEX = int(points.landmark[pose.PoseLandmark.LEFT_INDEX].x * w)



            distMO = math.hypot(moDX - moEX, moDY - moEY)

            distPE = math.hypot(peDX - peEX, peDY - peEY)



            # Verificar se as mãos estão rentes ao corpo (posição inicial)

            if distMO <= 150 and distPE >= 150:

                if start_time is None:  # Iniciar o cronômetro

                    if contador_inicial > 0:

                        cv2.putText(img, f"Iniciando em: {contador_inicial}", (w - 200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                        contador_inicial -= 1

                        time.sleep(1)

                    else:

                        start_time = time.time()

                        print("Cronômetro iniciado!")



            if start_time is not None:  # Só contar se o cronômetro estiver ativo

                if check and distMO <= 150 and distPE >= 150:

                    contador += 1

                    check = False



                if distMO > 150 and distPE < 150:

                    check = True



                # Exibir contador e cronômetro no canto superior direito

                texto_contador = f'Polichinelos: {contador}'

                cv2.putText(img, texto_contador, (w - 250, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)



                elapsed_time = time.time() - start_time

                tempo_restante = int(30 - elapsed_time)  # Contador regressivo

                cv2.putText(img, f"Tempo: {tempo_restante}s", (w - 250, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)



                if elapsed_time >= 30:  # 30 segundos de exercício

                    break



        time.sleep(0.01)

        cv2.imshow('Contagem de Polichinelos', img)



        if cv2.waitKey(1) & 0xFF == ord("q"):

            break



    video.release()

    cv2.destroyAllWindows()



    # Salvar a melhor repetição do dia

    if start_time is not None:

        salvar_progresso(usuario_id, contador, 30)  # Usa o ID real do usuário



    # Exibir gráfico de melhor repetição por dia

    mostrar_grafico(usuario_id)  # Usa o ID real do usuário



    # Exibir ranking pessoal

    mostrar_ranking_pessoal(usuario_id)  # Usa o ID real do usuário



    # Voltar para a seleção de exercícios

    abrir_tela_selecao(usuario_id)  # Usa o ID real do usuário
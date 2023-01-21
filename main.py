import speech_recognition as sr
import sys
import os
import json
import webbrowser
import urllib.parse
import requests
from gtts import gTTS
from playsound import playsound
from moviepy.editor import *
import re
from playwright.sync_api import sync_playwright, expect
import datetime
# from random import randint, choice, random
import random
import geocoder
from pygame import mixer
from pytube import YouTube, Playlist
import wikipedia
# from bs4 import BeautifulSoup

# Funcao responsavel por ouvir e reconhecer a fala
frase = None
commands = open('jsons/commands.json', 'r', encoding='utf-8')
commands = dict(json.load(commands))
sounds = open('jsons/sounds.json', 'r', encoding='utf-8')
sounds = dict(json.load(sounds))
applications = open('jsons/applications.json', 'r', encoding='utf-8')
applications = dict(json.load(applications))
default_folder = open('jsons/default_folder.json', 'r', encoding='utf-8')
default_folder = dict(json.load(default_folder))
thanks = open('jsons/thanks.json', 'r', encoding='utf-8')
thanks = list(json.load(thanks))
mixer.init()

try:
    mozilla_path = applications['firefox']
    controller_web = webbrowser.Mozilla(mozilla_path)
except:
    controller_web = webbrowser.get()

def cria_audio(audio, falar = None, name_s = None, play_s=True):
    tts = gTTS(audio,lang='pt-br')
    if(falar == None):
        print("Estou aprendendo o que você disse...")
        name = re.sub(r'([^A-Za-z0-9])', '_', audio).lower()
        name = str(re.sub(r'(\_+)', '_', name).lower()).strip('_')
    elif(name_s != None):
        name = re.sub(r'([^A-Za-z0-9])', '_', name_s).lower()
        name = str(re.sub(r'(\_+)', '_', name).lower()).strip('_')
    else:
        name = re.sub(r'([^A-Za-z0-9])', '_', audio).lower()
        name = str(re.sub(r'(\_+)', '_', name).lower()).strip('_')
    
    path_sound = str("audios/" + name + ".mp3")
    if(os.path.isfile(path_sound)):
        os.remove(path_sound)
    #Salva o arquivo de audio
    tts.save(path_sound)
    if(falar == None):
        print("Estou aprendendo o que você disse...")

    if(play_s):
        #Da play ao audio
        playsound(path_sound)
    else:
        return path_sound

def ouvir_microfone():
    global frase
    frase = None
    # Habilita o microfone para ouvir o usuario
    microfone = sr.Recognizer()
    with sr.Microphone() as source:
        # Chama a funcao de reducao de ruido disponivel na speech_recognition
        microfone.adjust_for_ambient_noise(source)
        # Avisa ao usuario que esta pronto para ouvir
        print("\nDiga alguma coisa: ")
        # playsound(sounds['beep_mic'], block=False)
        # Armazena a informacao de audio na variavel
        audio = microfone.listen(source)
        
        try:
            # Passa o audio para o reconhecedor de padroes do speech_recognition
            frase = microfone.recognize_google(audio, language='pt-BR')
            frase = str(frase).lower()
            # Após alguns segundos, retorna a frase falada
            print("Você disse: " + frase)

            # Caso nao tenha reconhecido o padrao de fala, exibe esta mensagem
            # except sr.UnkownValueError:
            #     print("Não entendi")
        except:
            frase = None
            print("Não entendi")
        
            
        
    return frase

def climate(city = None):
    try:
        playwright_weather = sync_playwright().start()
        browser_weather = playwright_weather.chromium.launch()
        page_weather = browser_weather.new_page()
        # page_weather.set_default_timeout(60000)
        if(city == None):
            page_weather.goto("https://www.google.com/search?q=previs%C3%A3o+do+tempo+taia%C3%A7u&ie=UTF-8")
        else:
            city = urllib.parse.quote_plus(city)
            page_weather.goto("https://www.google.com/search?q=previs%C3%A3o+do+tempo+" + city + "&ie=UTF-8")
        infos = {
                "city": page_weather.locator('//*[@id="wob_loc"]').text_content(),
                "temperature": page_weather.locator('//*[@id="wob_tm"]').text_content() + ' graus',
                "rain_prob": page_weather.locator('//*[@id="wob_pp"]').text_content(),
                "humidity": page_weather.locator('//*[@id="wob_hm"]').text_content(),
                "wind": page_weather.locator('#wob_ws').text_content(),
                "date": {
                    "day": str(page_weather.locator('//*[@id="wob_dts"]').text_content()).split(',')[0].strip(),
                    "hour": str(page_weather.locator('//*[@id="wob_dts"]').text_content()).split(',')[1].strip()
                },
                "climate": page_weather.locator('//*[@id="wob_dc"]').text_content(),
                "date_search": datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            }
    except:
        infos = {}

    return infos

def convert_video(local_to):
    if(os.path.exists(local_to)):
        try:
            local_file = local_to
            name_ = os.path.basename(local_file)
            name_ = name_.split('.')
            name_[len(name_) - 1] = 'mp3'
            name_ = ".".join(name_)
            name_ = re.sub(r'([^A-Za-z0-9\.])', '_', name_).lower()
            name_ = "audios_converted/" + str(re.sub(r'(\_+)', '_', name_).lower()).strip('_')

            video_to_audio = VideoFileClip(local_file)
            video_to_audio.audio.write_audiofile(name_)

            local_to = name_
        except:
            local_to = None
    else:
        local_to = None
        playsound(sounds['arquivo_n_o_encontrado'])
    
    return local_to

def download_youtube_video(url, type_v, pl_sounds=True, name_def=None, other_path = None):
    success = None

    if(other_path != None):
        other_path = os.path.abspath(other_path)

    try:
        video_url = url
        yt = YouTube(video_url)
        print(("-"*(len(yt.title) + 5)) + "\n" + yt.title + "\n" + ("-"*(len(yt.title) + 5)))
        if(name_def == None):
            name_youtube = yt.title
            name_youtube = re.sub(r'([^A-Za-z0-9\.])', '_', name_youtube) + '.mp4'
            name_youtube = str(re.sub(r'(\_+)', '_', name_youtube)).strip('_')
        else:
            name_youtube = name_def + '.mp4'

        try:
            if(other_path == None):
                path_sound = os.path.abspath("youtube_audio_down/in_download/" + name_youtube)
                if(os.path.exists(path_sound) and os.path.isfile(path_sound)):
                    os.remove(path_sound)
                path_sound = os.path.abspath("youtube_video_down/" + name_youtube)
                if(os.path.exists(path_sound) and os.path.isfile(path_sound)):
                    os.remove(path_sound)
            else:
                path_sound = os.path.join(other_path, name_youtube)
                if(os.path.exists(path_sound) and os.path.isfile(path_sound)):
                    os.remove(path_sound)
        
        except:
            pass

        if(type_v == 0):
            if(pl_sounds):
                playsound(sounds['baixando_v_deo'])
            video = yt.streams.filter(progressive=True, file_extension='mp4', type='video')
            if(other_path == None):
                video.order_by('resolution').desc().first().download('youtube_video_down/', filename=name_youtube)
            else:
                video.order_by('resolution').desc().first().download(other_path, filename=name_youtube)

            local_file = name_youtube
        else:
            if(pl_sounds):
                playsound(sounds['baixando_udio'])
            audio = yt.streams.filter(progressive=True, file_extension='mp4', type='video')
            audio.order_by('resolution').desc().first().download('youtube_audio_down/in_download', filename=name_youtube)

            local_file = os.path.abspath(r"youtube_audio_down\in_download\\" + name_youtube)
            name_ = os.path.basename(local_file)
            name_ = name_.split('.')
            name_[len(name_) - 1] = 'mp3'
            name_ = ".".join(name_)
            name_ = "youtube_audio_down/" + name_

            path_sound = os.path.abspath(name_)
            if(os.path.exists(path_sound) and os.path.isfile(path_sound)):
                os.remove(path_sound)

            video_to_audio = VideoFileClip(local_file)
            video_to_audio.audio.write_audiofile(name_)

            local_file = name_
        
        success = local_file
    except:
        success = None

    return success

def play_music_youtube(to_query, to_search):
    clip2 = None
    if(to_search):
        music_name = to_query
        query_string = urllib.parse.urlencode({"search_query": music_name})
        formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)

        search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
        # clip = requests.get("https://www.youtube.com/watch?v=" + "{}".format(search_results[0]))
        clip2 = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])

        # inspect = BeautifulSoup(clip.content, "html.parser")
        # yt_title = inspect.find_all("meta", property="og:title")

        # for concatMusic1 in yt_title:
        #     pass

        # print(concatMusic1['content'])
    else:
        clip2 = to_query

    music_play = download_youtube_video(url=clip2, type_v=1, name_def='play_music_youtube')
    if(music_play != None):
        mixer.music.load(music_play)
        mixer.music.play()
    else:
        playsound(sounds['n_o_foi_poss_vel_reproduzir_a_m_sica'])



playsound(sounds['programa_iniciado'], block=False)
#cria_audio('Deseja determinar um tempo?', falar = True)
while(True):
    if(frase in commands['1']):
        playsound(sounds['trabalho_encerrado'])
        quit()
    elif(frase in commands['2']):
        os.startfile(applications['visual code'])
    elif(frase in commands['3']):
        cria_audio('Deseja determinar um tempo?', falar = True)
        choose = ouvir_microfone()
        if(choose in commands['negative']):
            cria_audio('Encerrando...', falar = True)
            os.system("shutdown /s")
        elif(choose in commands['positive']):
            veri = False
            while(veri == False):
                try:
                    time_s = int(ouvir_microfone())
                except:
                    cria_audio('Número não identificado', falar = True)
            os.system("shutdown /s /t " + time_s)
    elif(frase in commands['4']):
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif(frase in commands['5']):
        playsound(sounds['o_que_deseja_pesquisar_no_youtube'])
        to_search = ouvir_microfone()
        if(to_search != None):
            playsound(sounds['pesquisando'])
            print(to_search)
            to_search = urllib.parse.quote_plus(to_search)
            controller_web.open("http://www.youtube.com/results?search_query=" + to_search)
        else:
            cria_audio('Não foi possível realizar a pesquisa!', falar = True)
    elif(frase in commands['6']):
        playsound(sounds['o_que_deseja_pesquisar'])
        to_search = ouvir_microfone()
        playsound(sounds['pesquisando'])
        to_search = urllib.parse.quote_plus(to_search)

        response = requests.get("https://api.duckduckgo.com/?q=" + to_search + "&format=json&kl=br-pt")
        response.raise_for_status()
        data = dict(response.json())
        if(len(data['Abstract']) > 0):
            play_s = cria_audio(data['Abstract'], falar = True, name_s='pesquisa duck', play_s=False)
            mixer.music.load(play_s)
            print(data['Abstract'])

            try:
                if(os.path.isfile('audios/pesquisa_duck.mp3')):
                    os.remove('audios/pesquisa_duck.mp3')
            except:
                print('Não foi possível deletar o áudio')
        else:
            # print('Nada encontrado :(\nExperimente pesquisar por termos como: Homem-Aranha, 2ª Guerra Mundial, Motorola')
            playsound(sounds['nada_encontrado_duck'])
    elif(frase in commands['7']):
        playsound(sounds['o_que_deseja_pesquisar'])
        to_search = ouvir_microfone()
        playsound(sounds['pesquisando'])
        print(to_search)
        to_search = urllib.parse.quote_plus(to_search)
        controller_web.open("https://www.google.com/search?q=" + to_search)
    elif(frase in commands['8']):
        musics = open('jsons/musics.json', 'r', encoding='utf-8')
        musics = dict(json.load(musics))
        playsound(sounds['qual_m_sica_deseja_ouvir'])
        music = ouvir_microfone()

        if(music == 'youtube'):
            playsound(sounds['qual_m_sica_do_youtube'])
            music = str(ouvir_microfone())
            if(music in musics['youtube']):
                play_music_youtube(musics['youtube'][music], False)
            else:
                playsound(sounds['m_sica_n_o_encontrada'])
        elif(music in musics):
            print('musica')
        else:
            playsound(sounds['m_sica_n_o_encontrada'])
    elif(frase in commands['9']):
        playsound(sounds['qual_a_cidade'])
        cidade = ouvir_microfone()
        if(cidade in commands['my_loc']):
            g = geocoder.ip('me')
            cidade = g.city
            try:
                g = geocoder.ip('me')
                cidade = g.city
            except:
                cidade = None

        if(cidade != None):
            cria_audio('Pesquisando previsão do tempo para ' + cidade, falar = True, name_s='climate')
            clima = dict(climate(cidade))
            if(len(clima) > 0):
                cria_audio('A cidade pesquisada é: ' + clima['city'], falar = True, name_s='climate')
                cria_audio('Temperatura: ' + clima['temperature'], falar = True, name_s='climate')
                cria_audio('Umidade: ' + clima['humidity'], falar = True, name_s='climate')
                cria_audio('Probabilidade de Chuva: ' + clima['rain_prob'], falar = True, name_s='climate')
                cria_audio('Força do Vento: ' + clima['wind'], falar = True, name_s='climate')
                cria_audio('Clima: ' + clima['climate'], falar = True, name_s='climate')
            else:
                playsound(sounds['n_o_foi_poss_vel_buscar_o_clima_da_sua_cidade'])
        else:
            playsound(sounds['n_o_foi_poss_vel_buscar_o_clima_da_sua_cidade'])
        
        if(os.path.isfile('audios/climate.mp3')):
            os.remove('audios/climate.mp3')
    elif(frase in commands['10']):
        playsound(sounds['qual_aplicativo_deseja_abrir'])
        application = ouvir_microfone()
        if(application in applications):
            playsound(sounds['abrindo_aplicativo'])
            os.startfile(applications[application])
        else:
            playsound(sounds['aplicativo_n_o_encontrado'])
    elif(frase in commands['11']):
        playsound(sounds['insira_o_caminho_do_v_deo_a_ser_convertido'], block=False)
        local_to = str(input('Arquivo: '))
        local_to = convert_video(local_to)

        if(local_to != None):
            playsound(sounds['deseja_ouvir_o_udio'], block=False)
            choose = ouvir_microfone()
            if(choose in commands['positive']):
                # playsound(local_to, block=False)
                mixer.music.load(local_to)
                mixer.music.play()
            else:
                playsound(sounds['ok'])
        else:
            playsound(sounds['n_o_foi_poss_vel_extrair_o_udio_do_v_deo'])
    elif(frase in commands['12']):
        try:
            mixer.music.stop()
            mixer.music.unload()
            playsound(sounds['som_paralisado'])
        except:
            print('Som paralisado')

        try:
            path_sound = os.path.abspath("youtube_audio_down/play_music_youtube.mp3")
            if(os.path.exists(path_sound) and os.path.isfile(path_sound)):
                os.remove(path_sound)

            path_sound = os.path.abspath("youtube_audio_down/in_download/play_music_youtube.mp4")
            if(os.path.exists(path_sound) and os.path.isfile(path_sound)):
                os.remove(path_sound)
        except:
            True
    elif(frase in commands['13']):
        hour_act = datetime.datetime.now()
        if(frase in commands['hour']):
            hour_act = hour_act.strftime('%H:%M')
            cria_audio('Agora são ' + hour_act, falar = True, name_s="hour_act")
        elif(frase in commands['day']):
            day_txt = None
            if(hour_act.strftime('%a') == 'Sun'):
                day_txt = "Domingo"
            elif(hour_act.strftime('%a') == 'Mon'):
                day_txt = "Segunda-feira"
            elif(hour_act.strftime('%a') == 'Tue'):
                day_txt = "Terça-feira"
            elif(hour_act.strftime('%a') == 'Wed'):
                day_txt = "Quarta-feira"
            elif(hour_act.strftime('%a') == 'Thu'):
                day_txt = "Quinta-feira"
            elif(hour_act.strftime('%a') == 'Fri'):
                day_txt = "Sexta-feira"
            elif(hour_act.strftime('%a') == 'Sat'):
                day_txt = "Sábado"
            
            hour_act = str(int(hour_act.strftime('%d'))) + ", " + day_txt
            cria_audio('Hoje é dia ' + hour_act, falar = True, name_s="hour_act")
        elif(frase in commands['month']):
            month_txt = None
            if(hour_act.strftime('%b') == 'Jan'):
                month_txt = "Janeiro"
            elif(hour_act.strftime('%b') == 'Feb'):
                month_txt = "Fevereiro"
            elif(hour_act.strftime('%b') == 'Mar'):
                month_txt = "Março"
            elif(hour_act.strftime('%b') == 'Apr'):
                month_txt = "Abril"
            elif(hour_act.strftime('%b') == 'May'):
                month_txt = "Maio"
            elif(hour_act.strftime('%b') == 'Jun'):
                month_txt = "Junho"
            elif(hour_act.strftime('%b') == 'Jul'):
                month_txt = "Julho"
            elif(hour_act.strftime('%b') == 'Aug'):
                month_txt = "Agosto"
            elif(hour_act.strftime('%b') == 'Sep'):
                month_txt = "Setembro"
            elif(hour_act.strftime('%b') == 'Oct'):
                month_txt = "Outubro"
            elif(hour_act.strftime('%b') == 'Nov'):
                month_txt = "Novembro"
            elif(hour_act.strftime('%b') == 'Dec'):
                month_txt = "Dezembro"
            
            cria_audio('Estamos em ' + month_txt, falar = True, name_s="hour_act")
        elif(frase in commands['year']):
            cria_audio('Estamos em ' + hour_act.strftime('%Y'), falar = True, name_s="hour_act")
        elif(frase in commands['date_complete']):
            day_txt = None
            if(hour_act.strftime('%a') == 'Sun'):
                day_txt = "Domingo"
            elif(hour_act.strftime('%a') == 'Mon'):
                day_txt = "Segunda-feira"
            elif(hour_act.strftime('%a') == 'Tue'):
                day_txt = "Terça-feira"
            elif(hour_act.strftime('%a') == 'Wed'):
                day_txt = "Quarta-feira"
            elif(hour_act.strftime('%a') == 'Thu'):
                day_txt = "Quinta-feira"
            elif(hour_act.strftime('%a') == 'Fri'):
                day_txt = "Sexta-feira"
            elif(hour_act.strftime('%a') == 'Sat'):
                day_txt = "Sábado"

            month_txt = None
            if(hour_act.strftime('%b') == 'Jan'):
                month_txt = "Janeiro"
            elif(hour_act.strftime('%b') == 'Feb'):
                month_txt = "Fevereiro"
            elif(hour_act.strftime('%b') == 'Mar'):
                month_txt = "Março"
            elif(hour_act.strftime('%b') == 'Apr'):
                month_txt = "Abril"
            elif(hour_act.strftime('%b') == 'May'):
                month_txt = "Maio"
            elif(hour_act.strftime('%b') == 'Jun'):
                month_txt = "Junho"
            elif(hour_act.strftime('%b') == 'Jul'):
                month_txt = "Julho"
            elif(hour_act.strftime('%b') == 'Aug'):
                month_txt = "Agosto"
            elif(hour_act.strftime('%b') == 'Sep'):
                month_txt = "Setembro"
            elif(hour_act.strftime('%b') == 'Oct'):
                month_txt = "Outubro"
            elif(hour_act.strftime('%b') == 'Nov'):
                month_txt = "Novembro"
            elif(hour_act.strftime('%b') == 'Dec'):
                month_txt = "Dezembro"

            # .strftime('%Y-%m-%d %H:%M, %a, %b')
            hour_act = "Hoje é " + day_txt + ", dia " + str(int(hour_act.strftime('%d'))) + " de " + month_txt + " de " + hour_act.strftime('%Y')
            cria_audio(hour_act, falar = True, name_s="hour_act")
        else:
            cria_audio('Que tempo quer que eu informe?', falar = True)
            choose = ouvir_microfone()
            if(choose in commands['hour']):
                hour_act = hour_act.strftime('%H:%M')
                cria_audio('Agora são ' + hour_act, falar = True, name_s="hour_act")
            elif(choose in commands['day']):
                day_txt = None
                if(hour_act.strftime('%a') == 'Sun'):
                    day_txt = "Domingo"
                elif(hour_act.strftime('%a') == 'Mon'):
                    day_txt = "Segunda-feira"
                elif(hour_act.strftime('%a') == 'Tue'):
                    day_txt = "Terça-feira"
                elif(hour_act.strftime('%a') == 'Wed'):
                    day_txt = "Quarta-feira"
                elif(hour_act.strftime('%a') == 'Thu'):
                    day_txt = "Quinta-feira"
                elif(hour_act.strftime('%a') == 'Fri'):
                    day_txt = "Sexta-feira"
                elif(hour_act.strftime('%a') == 'Sat'):
                    day_txt = "Sábado"
                
                hour_act = str(int(hour_act.strftime('%d'))) + ", " + day_txt
                cria_audio('Hoje é dia ' + hour_act, falar = True, name_s="hour_act")
            elif(choose in commands['month']):
                month_txt = None
                if(hour_act.strftime('%b') == 'Jan'):
                    month_txt = "Janeiro"
                elif(hour_act.strftime('%b') == 'Feb'):
                    month_txt = "Fevereiro"
                elif(hour_act.strftime('%b') == 'Mar'):
                    month_txt = "Março"
                elif(hour_act.strftime('%b') == 'Apr'):
                    month_txt = "Abril"
                elif(hour_act.strftime('%b') == 'May'):
                    month_txt = "Maio"
                elif(hour_act.strftime('%b') == 'Jun'):
                    month_txt = "Junho"
                elif(hour_act.strftime('%b') == 'Jul'):
                    month_txt = "Julho"
                elif(hour_act.strftime('%b') == 'Aug'):
                    month_txt = "Agosto"
                elif(hour_act.strftime('%b') == 'Sep'):
                    month_txt = "Setembro"
                elif(hour_act.strftime('%b') == 'Oct'):
                    month_txt = "Outubro"
                elif(hour_act.strftime('%b') == 'Nov'):
                    month_txt = "Novembro"
                elif(hour_act.strftime('%b') == 'Dec'):
                    month_txt = "Dezembro"
                
                cria_audio('Estamos em ' + month_txt, falar = True, name_s="hour_act")
            elif(choose in commands['year']):
                cria_audio('Estamos em ' + hour_act.strftime('%Y'), falar = True, name_s="hour_act")
            elif(choose in commands['date_complete']):
                day_txt = None
                if(hour_act.strftime('%a') == 'Sun'):
                    day_txt = "Domingo"
                elif(hour_act.strftime('%a') == 'Mon'):
                    day_txt = "Segunda-feira"
                elif(hour_act.strftime('%a') == 'Tue'):
                    day_txt = "Terça-feira"
                elif(hour_act.strftime('%a') == 'Wed'):
                    day_txt = "Quarta-feira"
                elif(hour_act.strftime('%a') == 'Thu'):
                    day_txt = "Quinta-feira"
                elif(hour_act.strftime('%a') == 'Fri'):
                    day_txt = "Sexta-feira"
                elif(hour_act.strftime('%a') == 'Sat'):
                    day_txt = "Sábado"

                month_txt = None
                if(hour_act.strftime('%b') == 'Jan'):
                    month_txt = "Janeiro"
                elif(hour_act.strftime('%b') == 'Feb'):
                    month_txt = "Fevereiro"
                elif(hour_act.strftime('%b') == 'Mar'):
                    month_txt = "Março"
                elif(hour_act.strftime('%b') == 'Apr'):
                    month_txt = "Abril"
                elif(hour_act.strftime('%b') == 'May'):
                    month_txt = "Maio"
                elif(hour_act.strftime('%b') == 'Jun'):
                    month_txt = "Junho"
                elif(hour_act.strftime('%b') == 'Jul'):
                    month_txt = "Julho"
                elif(hour_act.strftime('%b') == 'Aug'):
                    month_txt = "Agosto"
                elif(hour_act.strftime('%b') == 'Sep'):
                    month_txt = "Setembro"
                elif(hour_act.strftime('%b') == 'Oct'):
                    month_txt = "Outubro"
                elif(hour_act.strftime('%b') == 'Nov'):
                    month_txt = "Novembro"
                elif(hour_act.strftime('%b') == 'Dec'):
                    month_txt = "Dezembro"

                # .strftime('%Y-%m-%d %H:%M, %a, %b')
                hour_act = "Hoje é " + day_txt + ", dia " + str(int(hour_act.strftime('%d'))) + " de " + month_txt + " de " + hour_act.strftime('%Y')
                cria_audio(hour_act, falar = True, name_s="hour_act")
    elif(frase in commands['14']):
        playsound(sounds['insira_o_url_do_v_deo'], block=False)
        url_video_youtube = str(input('URL: '))
        playsound(sounds['qual_o_tipo_de_m_dia_udio_ou_v_deo'])
        choose = ouvir_microfone()
        if(choose in commands['video_youtube']):
            format_video = list([0, 'vídeo', 'v_ideo'])
        elif(choose in commands['audio_youtube']):
            format_video = list([1, 'áudio', 'udio'])
        else:
            format_video= None
        
        if(format_video != None):
            success = download_youtube_video(url_video_youtube, format_video[0])
            if(success != None):
                if(format_video[0] == 0):
                    playsound(sounds['v_deo_baixado_com_sucesso'])
                else:
                    playsound(sounds['udio_baixado_com_sucesso_deseja_ouvir'])
                    choose = ouvir_microfone()
                    if(choose in commands['positive']):
                        mixer.music.load(success)
                        mixer.music.play()
                    else:
                        playsound(sounds['ok'])
            else:
                playsound(sounds['erro_ao_baixar_' + format_video[2] + '_do_youtube'])
        else:
            playsound(sounds['n_o_entendi_o_formato_a_ser_baixado'])
    elif(frase in commands['15']):
        playsound(sounds['deseja_limpar_uma_pasta_padr_o'])
        choose = ouvir_microfone()
        if(choose in commands['positive']):
            playsound(sounds['qual_pasta'])
            choose = ouvir_microfone()
            if(choose in default_folder):
                local_clear = os.path.abspath(default_folder[choose])
            else:
                local_clear = None
        else:
            playsound(sounds['ok_insira_o_caminho_do_local'])
            local_clear = os.path.abspath(input('Local: '))

        if(local_clear != None and os.path.exists(local_clear)):
            local_clear_list = list(os.listdir(local_clear))
            playsound(sounds['tentando_limpar_o_local'])
            try:
                for x in local_clear_list:
                    x = os.path.join(local_clear, x)
                    if(os.path.isfile(x)):
                        os.remove(x)
                    elif(os.path.isdir(x)):
                        os.removedirs(x)
                playsound(sounds['local_limpo'])
            except:
                playsound(sounds['n_o_foi_poss_vel_limpar_o_local'])
        else:
            cria_audio('Não foi possível encontrar o local', falar = True)
    elif(frase in commands['16']):
        playsound(sounds['qual_m_sica_deseja_ouvir_no_youtube'])
        music_to_tube = ouvir_microfone()
        play_music_youtube(music_to_tube, True)
    elif(frase in commands['17']):
        playsound(sounds['o_que_deseja_pesquisar'])
        to_search = ouvir_microfone()
        playsound(sounds['pesquisando'])
        wikipedia.set_lang("pt")
        search = wikipedia.summary(to_search)
        play_sound = cria_audio(search, falar = True, name_s='pesquisa wiki', play_s=False)
        mixer.music.load(play_sound)
        mixer.music.play()
        print(search)
    elif(frase in commands['thanks']):
        cria_audio(random.choice(thanks), falar = True, name_s="thanks")
    elif(frase in commands['pause_sound']):
        try:
            mixer.music.pause()
            playsound(sounds['som_pausado'])
        except:
            playsound(sounds['erro_ao_pausar_som'])
    elif(frase in commands['unpause_sound']):
        try:
            playsound(sounds['som_despausado'])
            mixer.music.unpause()
        except:
            playsound(sounds['erro_ao_despausar_som'])
    elif(frase in commands['rewind_sound']):
        mixer.music.set_endevent(0)
        try:
            playsound(sounds['repetindo_som'])
            mixer.music.rewind()
            mixer.music.unpause()
        except:
            playsound(sounds['erro_ao_repetir_som'])
    elif(frase != None):
        playsound(sounds['comando_n_o_encontrado'])
        
    frase = None
    ouvir_microfone()
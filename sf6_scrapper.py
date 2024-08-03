# Librerias
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
import math
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree
import time
import os
from dotenv import load_dotenv, dotenv_values

# Loading environment varaibles
load_dotenv()
USER_DATA_DIR = os.getenv("USER_DATA_DIR")


def buckler_scrap(continente):
    print(f"USER DATA DIR USED : {USER_DATA_DIR}")
    homefilter = 1
    if continente == 0:
        homefilter = 1
    else:
        homefilter = 2
    # I. Parametros y opciones del webdriver
    service = Service(executable_path="C:/chromedriver_win32/chromedriver.exe")
    opts = webdriver.ChromeOptions()
    opts.add_argument("--disable-extensions")
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--start-maximized")
    opts.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64)" + "AppleWebKit/537.36 (KHTML, like Gecko)" + "Chrome/51.0.2704.103 Safari/537.36")
    opts.add_argument("--enable-javascript")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("detach",True)
    opts.add_argument(f"user-data-dir={USER_DATA_DIR}") # Usamos las cookies y perfiles de nuestro chrome, asi ya estamos logeados.



    # Obteniendo página con selenium, al parecer CAPCOM no quiere scrappers :(
    driver = webdriver.Chrome(options=opts)
    scrap_url = f"https://www.streetfighter.com/6/buckler/es-es/ranking/master?character_filter=1&character_id=luke&platform=1&home_filter={homefilter}&home_category_id={continente}&home_id=1&page=1"
    driver.get(scrap_url)
    time.sleep(5)
    item_scrap_soup = BeautifulSoup(driver.page_source,"lxml")
    # Cantidad de paginas. Cada pagina muestra 20 resultados.
    ## Nota, uso modulo, ya que si modulo es entre 1 y 19, significa que necesitamos una pagina adicional, si modulo es 0, necesitamos el resultado solo dividido por 20.
    sobrantes = (int(item_scrap_soup.find('span',class_='ranking_ranking_now__last__oqSXS').text.replace('/ ','')))%20
    paginas_pre = int(item_scrap_soup.find('span',class_='ranking_ranking_now__last__oqSXS').text.replace('/ ',''))/20 # Calculamos, nos da un float
    paginas_totales =  math.floor(paginas_pre) # Redondea hacia abajo
    if 1 <= sobrantes <= 19:
        paginas_totales = paginas_totales + 1
    print(f"La cantidad de páginas a scrapear son : {paginas_totales} páginas!")

    # Preparamos DataFrame a llenar junto al archivo
    df = pd.DataFrame(columns=["jugador","cfn_id","personaje","pais","mr","continente"])
    df.to_csv("./db_sf6_mr.csv",index=False,header=True)

    # Iteramos sobre todas las paginas para obtener todo
    for i in range(1,paginas_totales):
        pagina_actual = i
        print(f"Scrapeando página número {i} !!")
        print(f"-----------------------------------")
        scrap_url = f"https://www.streetfighter.com/6/buckler/es-es/ranking/master?character_filter=1&character_id=luke&platform=1&home_filter={homefilter}&home_category_id={continente}&home_id=1&page="+str(i)
        driver.get(scrap_url)
        time.sleep(5)
        item_scrap_soup = BeautifulSoup(driver.page_source,"lxml")
        # I. Info jugador

        ## I.a Nombre
        jugadores = []
        jugadores_raw = item_scrap_soup.find_all('span',class_='ranking_name__El29_')
        for i in range(1,len(jugadores_raw)):
            jugadores.append(jugadores_raw[i].text)

        ## I.b MR
        master_points = []
        master_points_raw = item_scrap_soup.find_all('div',class_='ranking_time__teMP4')
        for i in  range(1,len(master_points_raw))  :
            mr_final = master_points_raw[i].find('dd').text.replace(' PM','')
            master_points.append(mr_final)

        ## I.c Personaje
        personajes = []
        personajes_raw = item_scrap_soup.find_all('div',class_='ranking_character__WoGAX')
        for i in range(1,len(personajes_raw)):
            personaje_final = personajes_raw[i].find('img',alt=True)['alt']
            personajes.append(personaje_final)
        

        ## I.d Pais
        paises = []
        paises_raw = item_scrap_soup.find_all('span',class_='ranking_frag__D7XnG')
        for i in range(1,len(paises_raw)):
            pais_final = paises_raw[i].find_all('img',alt=True)[1]['alt']
            paises.append(pais_final)
        
        ## I.e ID CFN (Por si cambian nombre)
        cfn_list = []
        cfn_raw = driver.find_elements(By.CLASS_NAME, 'ranking_ranking_list__szajj')
        cfn_test = cfn_raw[1].find_elements(By.TAG_NAME,'a')
        for i in cfn_test:
            cfn_list.append(i.get_attribute("href").replace('https://www.streetfighter.com/6/buckler/es-es/profile/',''))

        
        # II. Escribimos en el DF
        df['jugador'] = jugadores
        df['cfn_id'] = cfn_list
        df['personaje'] = personajes
        df['pais'] = paises
        df['mr'] = master_points
        df['continente'] = continente
        
        print(f'Resultados para la pagina {pagina_actual}')
        for i in range(0,len(jugadores)):
            print(f'Nombre : {jugadores[i]} ,cfn_id : {cfn_list[i]}, Personaje : {personajes[i]}, Pais : {paises[i]} , MR : {master_points[i]}')

        # III. Apendamos al DF
        df.to_csv("./db_sf6_sudamerica_mr.csv",index=False,header=False,mode="a")
        ## III.a Limpiamos el dataframe!
        df = df[0:0]
        time.sleep(2)
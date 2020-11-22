from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import jogoajogo


class Init:
    driver = webdriver.Chrome(executable_path = "D:\Desktop\Projects\Python\SeleniumTestingFutebol\chromedriver.exe")


class Driver:
    def __init__(self, url):
        self.__driver = Init.driver
        self.__driver.get(url)
        self.__ids = []
        self.__jogo = None
        self.__obj_tempo = []
        self.__time_casa = None
        self.__time_fora = None
        self.__obj_acontecimentos = None
        self.discrepancias = []
        self.__gols_casa = []
        self.__gols_fora = []


        while True:
            try:
                mais_jogos = self.__driver.find_element_by_link_text('Mostrar mais jogos')
                self.__driver.execute_script("arguments[0].click();", mais_jogos)
                time.sleep(2)
            except:
                break

    def gerar_todos_cods_camp(self):
        all_games = self.__driver.find_element_by_xpath("//*[@class='sportName soccer']")
        tagname = all_games.find_elements_by_tag_name('div')
        for i in tagname:
            self.__ids.append(i.get_attribute('id')[4:])
        self.__ids = list(filter(None, self.__ids))
        return



    def gerar_dados_partidas(self):
        ids_faltantes = jogoajogo.checar_ids_banco(self.__ids)
        for cod_jogo in ids_faltantes:
            self.__driver.get('https://www.flashscore.com.br/jogo/' + cod_jogo + '/#resumo-de-jogo')
            time.sleep(2)
            self.__time_casa = self.__driver.find_element_by_xpath("//*[@class='team-text tname-home']").text
            self.__time_fora = self.__driver.find_element_by_xpath("//*[@class='team-text tname-away']").text
            gols = self.__driver.find_elements_by_xpath("//*[@class='scoreboard']")
            gol_casa = int(gols[0].text)
            gol_fora = int(gols[1].text)
            if gol_casa - gol_fora > 0:
                resultado_vencedor = 'C'
            elif gol_casa - gol_fora < 0:
                resultado_vencedor = 'F'
            else:
                resultado_vencedor = 'E'
            descricao_rodada = self.__driver.find_element_by_class_name('description__country').find_element_by_tag_name('a').text
            rodada = descricao_rodada[descricao_rodada.find('Rodada')+7:]
            self.__jogo = jogoajogo.Jogo(cod_jogo, self.__time_casa, self.__time_fora, resultado_vencedor, rodada)

            self.gerar_minutos_gols()

            self.gerar_estatisticas_tempo(cod_jogo)


    def gerar_minutos_gols(self):
        "Gerar minutos dos gols de cada time, pois devemos comparar com os gols no momentos dos acontecimentos."
        fatos_casa = self.__driver.find_elements_by_xpath(
            "//*[starts-with(@class, 'detailMS__incidentRow incidentRow--home')]")
        fatos_fora = self.__driver.find_elements_by_xpath(
            "//*[starts-with(@class, 'detailMS__incidentRow incidentRow--away')]")
        for fatos in fatos_casa:
            try:
                fatos.find_element_by_xpath(
                    ".//div[@class = 'icon-box soccer-ball-own'] | "
                    ".//div[@class = 'icon-box soccer-ball'] ").get_attribute('class')
                element_clock = fatos.find_element_by_xpath(
                    ".//div[@class = 'time-box'] | .//div[@class = 'time-box-wide']").text
                self.__gols_casa.append(element_clock)
            except:
                pass

        for fatos in fatos_fora:
            try:
                fatos.find_element_by_xpath(
                    ".//div[@class = 'icon-box soccer-ball-own'] | "
                    ".//div[@class = 'icon-box soccer-ball'] ").get_attribute('class')
                element_clock = fatos.find_element_by_xpath(
                    ".//div[@class = 'time-box'] | .//div[@class = 'time-box-wide']").text
                self.__gols_fora.append(element_clock)
            except:
                pass
        print(self.__gols_casa, self.__gols_fora)


    def gerar_estatisticas_tempo(self, cod_jogo):
        for tempo in range(1, 3):
            self.__driver.get(f'https://www.flashscore.com.br/jogo/{cod_jogo}/#estatisticas-de-jogo;{tempo}')
            time.sleep(1.4)
            estatistica = self.__driver.find_element_by_xpath("//*[@id='tab-statistics-"+str(tempo)+"-statistic']")
            game = [estatistica.find_elements_by_xpath("//*[@class='statText statText--titleValue']"),
                    estatistica.find_elements_by_xpath("//*[@class='statText statText--homeValue']"),
                    estatistica.find_elements_by_xpath("//*[@class='statText statText--awayValue']")]
            dados_estatistica = self.transformar_texto(game)

            self.__driver.get(f'https://www.flashscore.com.br/jogo/{cod_jogo}/#resumo-de-jogo')
            time.sleep(0.5)
            gols_casa = self.__driver.find_element_by_xpath(f"//*[@class='p{tempo}_home']").text
            gols_fora = self.__driver.find_element_by_xpath(f"//*[@class='p{tempo}_away']").text
            dados_tempo = jogoajogo.Tempo(cod_jogo, tempo, gols_casa, gols_fora, dados_estatistica)
            self.__obj_tempo.append(dados_tempo)
        self.gerar_acontecimentos(cod_jogo)




    def transformar_texto(self, game):
        dados = []
        for i in game:
            dados_temp = []
            for j in i:
                dados_temp.append(j.text)
            dados.append(list(filter(None, dados_temp)))
        return dados


    def gerar_acontecimentos(self, cod_jogo):
        self.__driver.get(f'https://www.flashscore.com.br/jogo/{cod_jogo}/#comentarios-ao-vivo;0')
        time.sleep(1.2)
        lista_driver = self.__driver.find_element_by_xpath("//*[@id='parts']")
        lista_driver = lista_driver.find_element_by_xpath("//table[@id='parts']/tbody")
        odd_even = lista_driver.find_elements_by_tag_name('tr')
        lista_acontecimentos = []
        gols_temp_casa = []
        gols_temp_fora = []
        for pos, element in enumerate(odd_even):

            try:
                minutagem = 0
                texto = element.find_element_by_xpath(
                    ".//*[@style='border-left: 1px solid var(--color-border-1);border-top: 0px;']").text
                team = texto[texto.find('(') + 1:texto.find(')')]
                element_clock = element.find_element_by_xpath(".//*[@class='time-box time-box-sec']").text

                try:
                    icon = element.find_element_by_xpath(".//div[@class='icon-phrase']/span")
                    icon = icon.get_attribute('class')[5:]
                except:
                    icon = 'No icon'


                if icon not in ['No icon', 'substitution', 'injury', 'time', 'attendance', 'funfact']:
                    if icon == 'soccer-ball-own':
                        icon = 'soccer-ball'
                    if icon == 'soccer-ball':
                        if element_clock in self.__gols_casa and element_clock not in gols_temp_casa:
                            team = 'C'
                            gols_temp_casa.append(element_clock)
                        elif element_clock in self.__gols_fora and element_clock not in gols_temp_fora:
                            team = 'F'
                            gols_temp_fora.append(element_clock)
                        else:
                            continue
                    elif icon == 'corner':
                        pos_time_casa = texto.find(self.__time_casa)
                        pos_time_fora = texto.find(self.__time_fora)
                        if pos_time_casa == -1 and pos_time_fora != -1:
                            team = 'F'
                        elif pos_time_fora == -1 and pos_time_casa != -1:
                            team = 'C'
                        elif pos_time_casa > pos_time_fora:
                            team = 'F'
                        elif pos_time_fora > pos_time_casa:
                            team = 'C'
                        else:
                            team = 'N'

                    elif team == self.__time_casa:
                        team = 'C'
                    elif team == self.__time_fora:
                        team = 'F'
                    elif team != self.__time_casa and team != self.__time_fora:
                        pos_time_casa = texto.find(self.__time_casa)
                        pos_time_fora = texto.find(self.__time_fora)
                        if pos_time_casa == -1 and pos_time_fora != -1:
                            team = 'F'
                        elif pos_time_fora == -1 and pos_time_casa != -1:
                            team = 'C'
                        elif pos_time_casa > pos_time_fora:
                            team = 'F'
                        elif pos_time_fora > pos_time_casa:
                            team = 'C'
                        else:
                            team = 'N'

                    clock = element_clock.replace("'", "")
                    clock = clock.split('+')
                    for i in clock:
                        minutagem += int(i)
                    minutagem -= 1

                    lista_acontecimentos.append([minutagem, icon, team, texto])

            except:
                pass
        gols_temp_casa.clear()
        gols_temp_fora.clear()
        self.__gols_casa.clear()
        self.__gols_fora.clear()
        self.__obj_acontecimentos = jogoajogo.Acontecimentos(cod_jogo, lista_acontecimentos)
        self.gerar_inserts()



    def gerar_inserts(self):
        self.__jogo.insert_jogo()
        for tempo in self.__obj_tempo:
            tempo.insert_tempo()
        self.__obj_tempo = []
        self.__obj_acontecimentos.insert_acontecimento()
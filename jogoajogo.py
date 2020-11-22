from database import CursorFromConnectionFromPool


def checar_ids_banco(ids):
    ids_faltantes = []
    for i in ids:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select 1 from jogos where cod_jogo = %s limit 1', (i,))
            busca = cursor.fetchone()
            if busca is None:
                ids_faltantes.append(i)
    return ids_faltantes


class Jogo:
    def __init__(self, cod_jogo, time_casa, time_fora, resultado_vencedor, rodada):
        self.cod_jogo = cod_jogo
        self.time_casa = time_casa
        self.time_fora = time_fora
        self.resultado_vencedor = resultado_vencedor
        self.rodada = rodada
        self.temporada = '2019/2020'

    def insert_jogo(self):
        with CursorFromConnectionFromPool() as cursor:
            try:
                print(f'Inserindo Jogo: {self.cod_jogo}')
                cursor.execute('INSERT INTO jogos(cod_jogo, time_casa, time_fora, resultado_vencedor, rodada, temporada) '
                               'VALUES(%s, %s, %s, %s, %s, %s)',
                               (self.cod_jogo, self.time_casa, self.time_fora, self.resultado_vencedor, self.rodada, self.temporada))
            except:
                print(f'Nao foi possível inserir {self.cod_jogo}.')


class Tempo:
    def __init__(self, cod_jogo, tempo, gols_casa, gols_fora, dados_estatistica):
        self.lista_estatistica = self.gerar_estatisticas(dados_estatistica)
        self.cod_jogo = str(cod_jogo)
        self.tempo = int(tempo)
        self.gols_casa = int(gols_casa)
        self.gols_fora = int(gols_fora)
        self.posse_casa = round(float(self.lista_estatistica[0]['Posse de bola'].replace('%',''))/100, 3)
        self.posse_fora = round(float(self.lista_estatistica[1]['Posse de bola'].replace('%',''))/100, 3)
        self.chutes_gol_casa = int(self.lista_estatistica[0]['Finalizações'])
        self.chutes_gol_fora = int(self.lista_estatistica[1]['Finalizações'])
        self.chutes_errados_casa = int(self.lista_estatistica[0]['Chutes fora'])
        self.chutes_errados_fora = int(self.lista_estatistica[1]['Chutes fora'])
        self.chutes_bloqueados_casa = int(self.lista_estatistica[0]['Chutes bloqueados'])
        self.chutes_bloqueados_fora = int(self.lista_estatistica[1]['Chutes bloqueados'])
        self.escanteios_casa = int(self.lista_estatistica[0]['Escanteios'])
        self.escanteios_fora = int(self.lista_estatistica[1]['Escanteios'])
        self.impedimentos_casa = int(self.lista_estatistica[0]['Impedimentos'])
        self.impedimentos_fora = int(self.lista_estatistica[1]['Impedimentos'])
        self.cartoes_amarelos_casa = None
        self.cartoes_amarelos_fora = None
        self.total_passes_casa = None
        self.total_passes_fora = None
        self.ataques_perigosos_casa = int(self.lista_estatistica[0]['Ataques Perigosos'])
        self.ataques_perigosos_fora = int(self.lista_estatistica[1]['Ataques Perigosos'])

        try:
            self.cartoes_amarelos_casa = int(self.lista_estatistica[0]['Cartões amarelos'])
        except:
            self.cartoes_amarelos_casa = 0

        try:
            self.cartoes_amarelos_fora = int(self.lista_estatistica[1]['Cartões amarelos'])
        except:
            self.cartoes_amarelos_fora = 0
        try:
            self.total_passes_casa = int(self.lista_estatistica[0]['Total de passes'])
        except:
            self.total_passes_casa = None
            pass
        try:
            self.total_passes_fora = int(self.lista_estatistica[1]['Total de passes'])
        except:
            self.total_passes_fora = None
            pass

    def insert_tempo(self):
        with CursorFromConnectionFromPool() as cursor:
            try:
                cursor.execute(
                    'INSERT INTO tempos(cod_jogo, tempo, gols_casa, gols_fora, posse_casa, posse_fora, '
                    'chutes_gol_casa, '
                    'chutes_gol_fora, chutes_errados_casa, chutes_errados_fora, chutes_bloqueados_casa, '
                    'chutes_bloqueados_fora, '
                    'escanteios_casa, escanteios_fora, impedimentos_casa, impedimentos_fora, '
                    'cartoes_amarelos_casa, '
                    'cartoes_amarelos_fora, total_passes_casa, total_passes_fora,ataques_perigosos_casa, '
                    'ataques_perigosos_fora)'
                    'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (self.cod_jogo, self.tempo, self.gols_casa, self.gols_fora, self.posse_casa, self.posse_fora,
                     self.chutes_gol_casa, self.chutes_gol_fora, self.chutes_errados_casa, self.chutes_errados_fora,
                     self.chutes_bloqueados_casa, self.chutes_bloqueados_fora, self.escanteios_casa,
                     self.escanteios_fora,
                     self.impedimentos_casa, self.impedimentos_fora, self.cartoes_amarelos_casa,
                     self.cartoes_amarelos_fora,
                     self.total_passes_casa, self.total_passes_fora, self.ataques_perigosos_casa,
                     self.ataques_perigosos_fora))

            except:
                print(f'nao foi possivel insert no jogo {self.cod_jogo} + {self.tempo}')
                pass

    def gerar_estatisticas(self, dados_estatistica):
        lista_dict = []
        for tempo in range(1,3):
            dicionario = {}
            for pos,tipo in enumerate(dados_estatistica[0]):
                dicionario[f'{tipo}'] = dados_estatistica[tempo][pos]
            lista_dict.append(dicionario)
        return lista_dict


class Acontecimentos:
    def __init__(self, cod_jogo, lista_acontecimentos):
        self.cod_jogo = cod_jogo
        self.lista_acontecimentos = lista_acontecimentos
        self.tempo = int(1)
        self.contador_tempo = float(0)
        self.resultado_parcial = int(0)


    def insert_acontecimento(self):
        with CursorFromConnectionFromPool() as cursor:
            for parcial in reversed(self.lista_acontecimentos):
                if parcial[1] == 'whistle':
                    self.contador_tempo += 0.5
                    if self.contador_tempo >= 1.5:
                        self.tempo = 2
                if parcial[1] == 'soccer-ball':
                    if parcial[2] == 'C':
                        self.resultado_parcial += 1
                    else:
                        self.resultado_parcial -= 1
                try:
                    cursor.execute(
                        'INSERT INTO acontecimentos(cod_jogo, tempo, icon, minuto, team, resultado_parcial, texto) '
                        'VALUES(%s, %s, %s, %s, %s, %s, %s)',
                        (self.cod_jogo, self.tempo, parcial[1], parcial[0], parcial[2], self.resultado_parcial, parcial[3]))

                except:
                    print(f'nao foi possivel insert no jogo {self.cod_jogo} + {parcial[0]}')


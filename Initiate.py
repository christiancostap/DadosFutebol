from selDriver import Driver, Init
import time
from database import Database

Database.initialise(user='postgres', password='root',
                    database='projetofutebol',
                    host='localhost')

driverobj = Driver('https://www.flashscore.com.br/futebol/inglaterra/campeonato-ingles/resultados/')
driverobj.gerar_todos_cods_camp()
driverobj.gerar_dados_partidas()
print(driverobj.discrepancias)
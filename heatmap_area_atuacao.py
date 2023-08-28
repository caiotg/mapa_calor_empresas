import os
import time
import folium
import googlemaps
import pandas as pd
from pprint import pprint
from dotenv import load_dotenv
from folium.plugins import HeatMap


class HeatMapAreaAtuacao():

    def __init__(self, caminhoDados, filtroPopulacao, keyWord, setor, nomeLoja):

        os.chdir(caminhoDados)
        load_dotenv()

        apiKey = os.getenv('API_KEY')

        self.nomeLoja = nomeLoja
        self.keyWord = keyWord
        self.setor = setor
        self.filtroPopulacao = filtroPopulacao
        self.cliente = googlemaps.Client(apiKey)

    def filtrando_municipios(self):

        municipios = pd.read_excel('Base_MUNIC_2021.xlsx', sheet_name= 'Recursos humanos', usecols= ['CodMun', 'UF', 'Cod UF', 'Mun', 'Pop'])

        self.municipios = municipios[municipios['Pop'] > self.filtroPopulacao]

    def pegando_coordenadas(self):

        listaCoordenadas = []

        for index in self.municipios.index:

            cidade = self.municipios['Mun'][index]
            estado = self.municipios['UF'][index]

            endereco = f'{cidade}, {estado}'

            print(endereco)

            response = self.cliente.geocode(endereco)

            if response != []:

                latitude = response[0]['geometry']['location']['lat']
                longitude = response[0]['geometry']['location']['lng']

                coordenada = (latitude, longitude)

                listaCoordenadas.append(coordenada) 

        self.listaCoordenadas = listaCoordenadas

    def fazendo_heatmap(self):

        listaDfs = []

        for coordenada in self.listaCoordenadas:

            results = self.cliente.places_nearby(location= coordenada, keyword= self.keyWord , radius= 50000)

            if results != []:

                print(coordenada)

                while True:

                    time.sleep(2)

                    for store in results['results']:

                        df = pd.DataFrame({
                            'nome': store['name'],
                            'endereco': store['vicinity'],
                            'latitude': store['geometry']['location']['lat'],
                            'longitude': store['geometry']['location']['lng']
                        }, index=[0])

                        listaDfs.append(df)

                    if 'next_page_token' in results:
                        nextPageToken = results['next_page_token']
                        results = self.cliente.places_nearby(location= coordenada, keyword= self.keyWord , radius= 50000, page_token= nextPageToken)

                    else:
                        break

      
        lojas = pd.concat(listaDfs, ignore_index= True)

        lojasFiltradas = lojas[(lojas['nome'] == self.keyWord) | (lojas['nome'].str.contains(self.setor))]
        lojasFiltradas = lojasFiltradas.drop_duplicates(subset= 'endereco')

        self.coordenadasLojas = lojasFiltradas[['latitude', 'longitude']].values

        mapa = folium.Map(location = [-15.7801, -47.9292], zoom_start = 5)
        HeatMap(self.coordenadasLojas, radius= 40).add_to(mapa)

        mapa.save(f'heatmap_{self.nomeLoja}.html')
    
if __name__ == '__main__':
    
    # localiza = HeatMapAreaAtuacao(caminhoDados= r'C:\Users\Caio\Documents\dev\github\heatmap_area_atuacao_localiza_movida', filtroPopulacao= 65000, keyWord= 'Localiza Aluguel de Carros', setor= 'Locadora', nomeLoja= 'localiza')

    # localiza.filtrando_municipios()
    # localiza.pegando_coordenadas()
    # localiza.fazendo_heatmap()

    movida = HeatMapAreaAtuacao(caminhoDados= r'C:\Users\Caio\Documents\dev\github\mapa_calor_empresas', filtroPopulacao= 65000, keyWord= 'Movida Aluguel de Carros', setor= 'Locadora', nomeLoja= 'movida')

    movida.filtrando_municipios()
    movida.pegando_coordenadas()
    movida.fazendo_heatmap()

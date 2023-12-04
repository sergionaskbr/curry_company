# Libraries
import pandas as pd
from haversine import haversine, Unit
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from PIL import Image # PIL: biblioteca boa para manipular imagens.
import folium
from streamlit_folium import folium_static
st.set_page_config(page_title='Visão Entregadores', page_icon='🏍️', layout='wide')

# --------------
# Funções
# --------------

def clean_code(df1):
    """ Essa função tem a responsabilidade de limpar o dataframe.
    
    Tipos de limpeza:
    1. Remoção dos dados NaN
    2. Mudanças dos tipos de dados de colunas
    3. Remoção dos espaços das variáveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo - (remoção do texto da variável numérica).

    Input: Dataframe
    Output: Dataframe
    """

    #1. Convertendo a coluna Age de texto para número:
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    #2. Tirando o 'NaN ' de Road_traffic_density:
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    #3. Tirando o 'NaN ' de City:
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    #4. Convertendo a coluna Ratings de texto para número decimal (float):
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    #5. Convertendo a coluna Order_Date de texto para data:
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    #6. Convertendo multiple_deliveries de texto para número inteiro (int):
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    #7. Removendo os espaços de strings/texto/object - 2º jeito:
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    #8. Limpando a coluna time_taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    #9. Criando a coluna week_of_year
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df1['week_of_year'] = df1['week_of_year'].astype(int)

    return df1


# Essa função vai servir para dois cálculos da página - com o parâmetro top_asc, posso chamar o ascending True ou False usando essa mesma função.
def top_delivers(df1, top_asc):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
           .groupby(['City', 'Delivery_person_ID']).mean()
           .sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df3

#---------- Início da estrutura lógica do código -----------

# -----------------
# Import Dataset
# -----------------
df = pd.read_csv('dashboards/train.csv')


# -----------------
# Limpando os dados
# -----------------
df1 = clean_code(df)

# =================
# Barra Lateral (Sidebar) do Streamlit
# =================
st.header('Marketplace - Visão Entregadores')

# image_path = 'img/1.png' # O caminho para puxar a imagem do meu computador também vira uma variável.
image = Image.open('1.png') # Image é uma função da biblioteca PIL, open uma função (livro) dela, que abre fotos do meu computador.
st.sidebar.image(image, width=120) 

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')
st.sidebar.markdown("""---""")
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default='Low') # Default: valores que já aparecem automaticamente na caixa de seleção.
st.sidebar.markdown("""---""")
weather_options = st.sidebar.multiselect(
    'Quais as condições climáticas',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default='conditions Sunny') # Default: valor que aparecerá na caixa de seleção quando o usuário não selecionar nada.
st.sidebar.markdown("""---""")
st.sidebar.markdown("### Powered by Comunidade DS")

# Fazendo um DRILL DOWN nos dados - ele mostra todos os gráficos do Streamlit do início até a data que selecionarmos na barra do sidebar (date_slider).
# A técnica do drill down consiste em dissecar um problema, dividindo-o em partes cada vez menores, até identificarmos a causa.

# Filtro de data:
linhas_selecionadas = df1['Order_Date'] < date_slider # Se a pessoa coloca uma data, ele filtra do início até aquela data.
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito:
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options) # Road_traffic_density está em >>> filtro traffic_options.
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de clima:
linhas_selecionadas = df1['Weatherconditions'].isin(weather_options) # Weatherconditions estão em >>> filtro weather_options.
df1 = df1.loc[linhas_selecionadas, :]

# =================
# Layout da Página Principal do Streamlit - OS COMENTÁRIOS SÃO MUITO IMPORTANTES PARA ORGANIZARMOS NOSSO CÓDIGO!
# =================

with st.container():
    st.title('Overall Metrics')
    col1, col2, col3, col4 = st.columns(4, gap='large')
    with col1:
        maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
        col1.metric('Maior idade', maior_idade)

    with col2:
        menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
        col2.metric('Menor idade', menor_idade)

    with col3:
        melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
        col3.metric('Melhor condição', melhor_condicao)
        
    with col4:
        pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
        col4.metric('Pior condição', pior_condicao)

with st.container():
    st.markdown("""---""")
    st.title('Avaliações')
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('##### Avaliação média por entregador')
        df_avg_rating_per_deliver = (df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                     .groupby(['Delivery_person_ID'])
                                     .mean()
                                     .reset_index())
        st.dataframe(df_avg_rating_per_deliver)
    with col2:
        st.markdown('##### Avaliação média por trânsito')
        df_avg_std_rating_per_traffic = (df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                                         .groupby(['Road_traffic_density'])
                                         .agg({'Delivery_person_Ratings':['mean', 'std']}))
        df_avg_std_rating_per_traffic.columns = ['delivery_mean', 'delivery_std']
        df_avg_std_rating_per_traffic.reset_index()
        st.dataframe(df_avg_std_rating_per_traffic)
        
        st.markdown('##### Avaliação média por clima')
        df_avg_std_rating_per_weather = (df1.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']]
                                     .groupby(['Weatherconditions'])
                                     .agg({'Delivery_person_Ratings':['mean', 'std']}))
        # Mudança de nome e organização das colunas
        df_avg_std_rating_per_weather.columns = ['delivery_mean', 'delivery_std']
        
        # Reset_index()
        df_avg_std_rating_per_weather = df_avg_std_rating_per_weather.reset_index()
        st.dataframe(df_avg_std_rating_per_weather)


with st.container():
    st.markdown("""---""")
    st.title('Velocidade de entrega')
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('##### Top entregadores mais rápidos')
        df3 = top_delivers(df1, top_asc=True)
        st.dataframe(df3)

    with col2:
        st.markdown('##### Top entregadores mais lentos')
        df3 = top_delivers(df1, top_asc=False)
        st.dataframe(df3)

    






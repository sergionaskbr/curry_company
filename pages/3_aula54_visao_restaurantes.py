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
import numpy as np
st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

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

def distance(df1, fig):     
    if fig == False:
        cols = ["Restaurant_latitude", "Restaurant_longitude", "Delivery_location_latitude", "Delivery_location_longitude"]
        df1['distance'] = (df1.loc[:, cols].apply(lambda x: # ATENÇÃO AO PARÊNTESES PRA FECHAR ESSE CÓDIGO!!!
                     haversine(
                         (x['Restaurant_latitude'], x['Restaurant_longitude']),
                         (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
        avg_distance = np.round(df1['distance'].mean(), 2) # np.round = função da biblioteca numpy para reduzir números após a vírgula.
        return avg_distance

    else:
        cols = ["Restaurant_latitude", "Restaurant_longitude", "Delivery_location_latitude", "Delivery_location_longitude"]
        df1['distance'] = (df1.loc[:, cols].apply(lambda x:
                                                 haversine(
                                                     (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                     (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])]) 
        return fig
        

def avg_std_time_delivery(df1, festival, op):
    """
    Esta função calcula o tempo e o desvio padrão do tempo de entrega.
    Parâmetros:
        Inputs: 
            - df: Dataframe com os dados necessários para o cálculo.
            - op: Tipo de operação que precisa ser calculada.
                'avg_time': Calcula o tempo médio.
                'std_time': Calcula o desvio padrão do tempo.
        Output:
            - df: Dataframe com 2 colunas e 1 linha.
    """
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2) 
    return df_aux

def avg_std_time_graph(df1):
    df_aux = df1.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']}) 
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'],
                         error_y=dict(type='data', array=df_aux['std_time']))) 
    fig.update_layout(barmode='group', width=300, height=400)
    return fig

def avg_std_time_on_traffic(df1):
    df_aux = (df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']]
              .groupby(['City', 'Road_traffic_density'])
              .agg({'Time_taken(min)': ['mean', 'std']})) 
    df_aux.columns = ['avg_time', 'std_time'] 
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
    # Path: a ordem dos elementos(colunas) na lista define do círculo + interno ao + externo do sunburst.
    # Values: correponderão à largura de cada elemento nos círculos.
                      color='std_time', color_continuous_scale='RdBu',
    # Color: cor de cada parte dos círculos (no caso, atribuídas pelo desvio padrão). 
    # Color_continuous_scale: gradiente de cores. No caso: red e blue.
                      color_continuous_midpoint=np.average(df_aux['std_time']))
    # Color_continuous_midpoint: ponto a partir do qual a cor muda (de red para blue). No caso, é a média do desvio padrão. 
    return fig


#---------- Início da estrutura lógica do código -----------

# -----------------
# Import Dataset
# -----------------
df = pd.read_csv('dashboards/train.csv')


# -----------------
# Limpando os dados
# -----------------
df1 = clean_code(df)

# VISÃO RESTAURANTES

# =================
# Barra Lateral (Sidebar) do Streamlit
# =================
st.header('Marketplace - Visão Restaurantes')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', delivery_unique)
            
        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric('Distância média das entregas', avg_distance)
            
        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('Tempo médio de entrega c/ Festival', df_aux)
            
        with col4:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col4.metric('Desvio padrão de entrega c/ Festival', df_aux)
            
        with col5:
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric('Tempo médio de entrega s/ Festival', df_aux)
            
        with col6:
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
            col6.metric('Desvio padrão de entrega s/ Festival', df_aux)
            
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Média e desvio padrão do tempo de entrega por cidade (em mins)')
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)        

        with col2:
            st.markdown('##### Média e desvio padrão do tempo de entrega por cidade e tipo de pedido (em mins)')
            df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']}) 
            df_aux.columns = ['avg_time', 'std_time'] 
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
            
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição da distância e do tempo das entregas com desvio padrão (em mins)')
        col1, col2 = st.columns(2)
        
        with col1:              
            fig = distance(df1, fig=True)
            st.plotly_chart(fig, use_container_width=True)
       
        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)                              
            

     



































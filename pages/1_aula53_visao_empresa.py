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
st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide') 

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

def order_metric(df1):
    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID') 
    return fig
            
def traffic_order_share(df1):
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index() 
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :] 
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum() 
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
    return fig

def traffic_order_city(df1):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index() 
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City') 
    return fig

def order_by_week(df1):
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')
    return fig

def order_share_by_week(df1):
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig

def country_maps(df1):
    df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
          .groupby(['City', 'Road_traffic_density']).median().reset_index()) 
    map = folium.Map()
    for index, location_info in df_aux.iterrows(): 
        folium.Marker([location_info['Delivery_location_latitude'], 
                       location_info['Delivery_location_longitude']], 
                      popup=location_info[['City', 'Road_traffic_density']]).add_to(map) 
    folium_static(map, width=1024, height=600) # Erro de ter vários mapas: o folium_static estava identado dentro do laço for!


#---------- Início da estrutura lógica do código -----------

# -----------------
# Import Dataset
# -----------------
df = pd.read_csv('dashboards/train.csv')


# -----------------
# Cleaning Dataset
# -----------------
df1 = clean_code(df)


# =================
# Barra Lateral (Sidebar) do Streamlit
# =================

st.header('Marketplace - Visão Cliente')

# image_path = 'img/1.png' # O caminho para puxar a imagem do meu computador também vira uma variável.
image = Image.open('1.png') # Image é uma função da biblioteca PIL, open uma função (livro) dela, que abre fotos do meu computador.
st.sidebar.image(image, width=120) 

st.sidebar.markdown('# Cury Company')
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
st.sidebar.markdown("### Powered by Comunidade DS")

# Fazendo um DRILL DOWN nos dados - ele mostra todos os gráficos do Streamlit do início até a data que selecionarmos na barra do sidebar (date_slider).
# A técnica do drill down consiste em dissecar um problema, dividindo-o em partes cada vez menores, até identificarmos a causa.

# Filtro de data:
linhas_selecionadas = df1['Order_Date'] < date_slider # Se a pessoa coloca uma data, ele filtra do início até aquela data.
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de trânsito:
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options) # Road_traffic_density está em >>> filtro traffic_options.
df1 = df1.loc[linhas_selecionadas, :]

# =================
# Layout da Página Principal do Streamlit - OS COMENTÁRIOS SÃO MUITO IMPORTANTES PARA ORGANIZARMOS NOSSO CÓDIGO!
# =================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1: # O que estiver identado dentro do with ficará em cada uma das abas da página principal Streamlit.  
    with st.container():
        st.markdown('# Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)        

    with st.container(): # Na verdade, consegui dividir as colunas sem precisar do st.container()
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)                

with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
    
    

    
    
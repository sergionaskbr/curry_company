import streamlit as st
from PIL import Image

st.set_page_config( # Junta as páginas.
    page_title='Home',
    page_icon='🎲',
)

# image_path = 'C:/Users/sergi/repos/4_ftc_analise_dados_python/img/'
image = Image.open('1.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento da empresa Curry Company.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa: 
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanhamento de indicadores semanais de crescimento.
    - Visão Restaurantes: 
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
    - Time de Data Science do Discord: 
        - @sergionask
    Dados extraídos de Food Delivery Dataset (Kaggle) - https://www.kaggle.com/datasets/gauravmalik26/food-delivery-dataset/
        
""")

import streamlit as st
import pandas as pd
import random
import statistics as stat
import numpy as np

st.set_page_config(page_title='Calculadora de retiro - BDI Consultora de inversiones')

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.title('Calculadora de retiro')
st.write("Creado por [BDI Consultora de inversiones](https://www.bdiconsultora.com)")

## Sidebar

st.sidebar.image('https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bbbc94f3-618e-47a5-80a4-92a60e08da90/marcab.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210906%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210906T053149Z&X-Amz-Expires=86400&X-Amz-Signature=88b5526dcb49f7d825cd286247ff0b9f4de7f3ad2c8f167cfd4a2baddfca5b46&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D"marcab.png"', use_column_width='auto')
st.sidebar.markdown('---')

years = st.sidebar.slider('Edad actual / Edad de retiro', value=[30,65], min_value=20, max_value=100)
initialInvestment = st.sidebar.number_input('Capital inicial (USD)', step=100, min_value=100, value=10000)
monthlyInvestment = st.sidebar.number_input('Ahorros a invertir mensualmente',value=200,step=100, help='Este calculo utiliza inversion anual, pero tene en cuenta que al ahorrar e invertir mensualmente los retornos van a ser mayores debido al interés compuesto.')
st.sidebar.info('Inversión anual: ' + str(int(monthlyInvestment*12)) + 'USD')

st.sidebar.markdown('---')
choice = st.sidebar.radio(
    "Usar retornos:",
    ('Fijos', 'Aleatorios'))

if choice == 'Fijos':
    anualReturn = st.sidebar.number_input('Retorno anual esperado', step=0.1,value=8.0,help='8% Es el retorno promedio del SP500')
    year0Return = initialInvestment * anualReturn/100

if choice == 'Aleatorios':
    rango = st.sidebar.slider('Rango de aletoriedad', value=[-2,10], max_value=25, min_value=-10)
    largo = years[1] - years[0]
    anualReturn = [round(random.randrange(rango[0],rango[1])+random.uniform(0,1),2) for i in range(largo)]
    st.sidebar.info('Retorno promedio: ' + str(round(stat.fmean(anualReturn),2)) + '%')
    st.sidebar.button('Actualizar retornos')
    year0Return = initialInvestment * anualReturn[0]/100

## Math
yearsRange = range(years[0],years[1])

## Main
tablaDatos = pd.DataFrame()
tablaDatos['Edad'] = yearsRange
tablaDatos['Retorno (%)'] = anualReturn
tablaDatos['Inversión'] = int(monthlyInvestment*12)
tablaDatos['Inversión Acumulada'] = initialInvestment + tablaDatos['Inversión'].cumsum()
tablaDatos['Intereses'] = tablaDatos['Inversión Acumulada']*anualReturn/100
tablaDatos['Intereses Acumulados'] = tablaDatos['Intereses'].cumsum()
tablaDatos['Balance'] = initialInvestment + tablaDatos['Inversión Acumulada'] + tablaDatos['Intereses Acumulados']

tablaInicial = pd.DataFrame()
tablaInicial['Edad'] = [0]
tablaInicial['Retorno (%)'] = [0]
tablaInicial['Inversión'] = [0]
tablaInicial['Inversión Acumulada'] = [initialInvestment]
tablaInicial['Intereses'] = [0]
tablaInicial['Intereses Acumulados'] = [0]
tablaInicial['Balance'] = [initialInvestment]

tabla = pd.concat([tablaInicial,tablaDatos])
tabla.reset_index(drop=True,inplace=True)
for i in range(len(tabla)):
    tabla.loc[i,'Intereses'] = (0 if i == 0 else tabla.loc[i-1,'Balance']*tabla.loc[i,'Retorno (%)']/100)
    tabla.loc[i,'Intereses Acumulados'] = (0 if i == 0 else tabla.loc[i-1,'Intereses Acumulados'] + tabla.loc[i,'Intereses'])
    tabla.loc[i,'Balance'] = (10000 if i == 0 else tabla.loc[i,'Inversión Acumulada'] + tabla.loc[i,'Intereses Acumulados'])

tabla.loc[0,'Edad'] = np.nan
tabla.loc[0,'Retorno (%)'] = np.nan
tabla.loc[0,'Inversión'] = np.nan
tabla.loc[0,'Intereses'] = np.nan
tabla.loc[0,'Intereses Acumulados'] = np.nan

final = round(tabla['Balance'].to_list()[-1],2)

st.markdown('---')
col1,col2 = st.columns(2)
col1.metric('Capital final', str('{0:,}'.format(int(final)))+' USD')
col2.metric('Jubilación mensual', str('{0:,}'.format(int(final*0.04/12))) + ' USD')

st.table(tabla.style.format({"Edad": "{:.0f}","Retorno (%)": "{:.2f}","Inversión": "{:.2f}","Inversión Acumulada": "{:.2f}","Intereses": "{:.2f}","Intereses Acumulados": "{:.2f}","Balance": "{:.2f}"}))

grafico = tabla.filter(['Inversión Acumulada','Balance'])
st.line_chart(grafico)

st.markdown('---')
st.subheader('Preguntas frecuentes:')
col1,col2 = st.columns(2)
with col1:
    with st.expander('¿Por qué se calcula en dolares y no en pesos?'):
        st.write('Lamentablemente el paso cada vez cumple menos requisitos de una moneda. Por su falta de estabilidad, no puede utilizarse para proyectar a largo plazo y cumplir un objetivo de inversión')

    with st.expander('¿Puedo descargar esta pagina como pdf?'):
        st.write('¡Si claro! Es una herramienta de planificacion financiera para que cumplas tus objetivos y te retires lo más joven posible')

with col2:
    with st.expander('¿Cómo puedo iniciar a invertir mis ahorros?'):
        st.write('Desde BDI Consultora brindamos educación financiera sin costo y membresias con asesoramiento personalizado para que tus ahorros no pierdan valor. ¡Hablemos! Hacé click [acá](https://api.whatsapp.com/send/?phone=5491127163322&text&app_absent=0)')

    with st.expander('¿Por qué es importante planificar mi retiro?'):
        st.write('Hoy en dia pensar en una jubilacion de 2000USD mensuales, pasado a pesos, esta muy por encima de la media en Argentina, cuando en el resto del mundo no tanto. Esto refleja la debilidad de nuestra moneda y la importancia de planificar y ahorrar en monedas estables.')

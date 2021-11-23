from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import json
from datetime import timedelta


# configuraçoes da pagina
st.set_page_config(
    page_title="Calendar",
    layout="wide",
)


# definiçoes par acesso a conta google 
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
service_account_info = json.loads(st.secrets["textkey"])
credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)


# funçao para leitura de css
def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


def main():

    # carrega css para estilo
    local_css("style.css")

    service = build('calendar', 'v3', credentials=credentials)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    now_date = datetime.datetime.utcnow()
    events_result = service.events().list(calendarId='ambev.eng01@gmail.com', timeMin=now,
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    # constantes para formatacao da data    
    Diasemana = ('Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado','Domingo')
    Meses = ('janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro')
    
    # formatacao da data para gerar o titulo
    mes = (now_date.month-1)
    diadasemana = now_date.weekday()
    titulo = Diasemana[int(diadasemana)] + ', ' + now_date.strftime("%d") + ' de ' + Meses[int(mes)] + ' de ' + now_date.strftime("%Y")
    atualizacao_h = now_date - timedelta(hours=3, minutes=0)
    atualizacao = atualizacao_h.strftime("%H:%M:%S")
    
    # titulo e ultima atualizacao
    tit, update = st.columns([8,2])
    tit.title(titulo)    
    update.write('Última atualização: ' + atualizacao)    

    # difine um estado inicial para as telas (os dias da semana, essa variável define que dia aparece na parte semanal)
    if 'key' not in st.session_state:
        st.session_state['key'] = 1
    
    # organizacao dos dados
    st.subheader('O que está rolando hoje ' + ":alarm_clock:" )

    # mensagem para avisar que nao ha eventos
    if not events:
        st.info('Não há mais eventos hoje.')
    
    # colunas evento do dia
    ev0, ev1, ev2, ev3, ev4, ev5, ev6, ev7 = st.columns(8)
    
    # colunas eventos da fixos e da semana
    fixo, semana = st.columns([3.4, 4.6])
    d1, d2, d3, s1, s2, s3 = st.columns([1,2.3,0.1,1,3.5,0.1])

    # dia atual da semana
    dia_atual_semana = now_date.today().weekday()
    
    # dias restantes da semana
    restante = 7 - dia_atual_semana
    
    # Lista com as datas restantes excluindo o dia atual
    date_generated = [(now_date + datetime.timedelta(days=x)).strftime("%d/%m/%Y") for x in range(1, restante)]
    
    # define a data baseado no estado atual        
    data_sel = date_generated[(st.session_state.key - 1)]
    semana.subheader('Eventos da semana ' + '(' + data_sel + ')' + ' :spiral_calendar_pad:' )
    index_semana = 0

    #####################
    # EVENTOS DA SEMANA #
    #####################

    for event in events:

        # formato da data
        formater = "%Y-%m-%dT%H:%M:%S"
        formater2 = "%d/%m/%Y"
        
        # formata data inicial
        start_time = event['start'].get('dateTime', event['start'].get('date'))

        if len(start_time) == 10:
            start_time = start_time + 'T00:00:00-03:00'
            t_start = datetime.datetime.strptime(start_time.replace('-03:00',''), formater)
        else:
            t_start = datetime.datetime.strptime(start_time.replace('-03:00',''), formater)

        # formata data final
        end_time = event['end'].get('dateTime', event['end'].get('date'))
        t_end = datetime.datetime.strptime(end_time.replace('-03:00',''), formater)

        # data selecionada
        if data_sel is not None:
            data_selecionada = datetime.datetime.strptime(data_sel, formater2)
            
            if t_start.strftime("%d/%m/%Y") == data_selecionada.strftime("%d/%m/%Y"):
                try:    
                    valor = t_start.strftime('%H:%M') + ' - ' + t_end.strftime('%H:%M')
                    s1.markdown('<div class="highlight3"><h2 class="fonte3">{}</h2></div>'.format(valor), unsafe_allow_html=True)
                    s2.markdown('<div class="highlight3"><h2 class="fonte3">{}</h2></div>'.format(event['summary']), unsafe_allow_html=True)
                except:
                    s1.error('Evento sem informacao')

        index_semana += 1

    #################
    # EVENTOS FIXOS #
    #################

    fixo.subheader('Eventos fixos :lower_left_ballpoint_pen:')

    d1.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('08:30 - 08:45'), unsafe_allow_html=True)
    d2.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('Reunião diária do PAF'), unsafe_allow_html=True)

    d1.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('08:40 - 09:00'), unsafe_allow_html=True)
    d2.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('Reunião diária engenharia'), unsafe_allow_html=True)

    d1.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('09:00 - 09:40'), unsafe_allow_html=True)
    d2.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('Reunião de produtividade'), unsafe_allow_html=True)

    d1.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('09:40 - 10:20'), unsafe_allow_html=True)
    d2.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('Reunião da L751'), unsafe_allow_html=True)

    d1.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('10:00 - 10:30'), unsafe_allow_html=True)
    d2.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('Reunião matinal logística'), unsafe_allow_html=True)

    d1.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('10:20 - 11:00'), unsafe_allow_html=True)
    d2.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('Reunião da L752'), unsafe_allow_html=True)

    d1.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('11:00 - 11:30'), unsafe_allow_html=True)
    d2.markdown('<div class="highlight2"><h2 class="fonte2">{}</h2></div>'.format('Reunião de planejamento'), unsafe_allow_html=True)
        
    ##################
    # EVENTOS DO DIA #
    ##################
    
    # index das colunas
    index = 0

    for event in events:

        # formato da data
        formater = "%Y-%m-%dT%H:%M:%S"

        # formata data inicial
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        t_start = datetime.datetime.strptime(start_time.replace('-03:00',''), formater)

        # formata data final
        end_time = event['end'].get('dateTime', event['end'].get('date'))
        t_end = datetime.datetime.strptime(end_time.replace('-03:00',''), formater)    
        
        # maximo de 8 eventos simultaneos
        if t_start.strftime("%d/%m/%Y") == now_date.strftime("%d/%m/%Y"):
            
            if index == 0:
                try:    
                    valor = t_start.strftime('%H:%M') + ' - ' + t_end.strftime('%H:%M')
                    ev0.markdown('<div class="highlight0"><h2 class="fonte1">{}</h2></div>'.format(valor), unsafe_allow_html=True)
                    ev0.markdown('<div class="highlight1"><h2 class="fonte1">{}</h2></div>'.format(event['summary']), unsafe_allow_html=True)

                except:
                    ev0.error('Evento sem informacao')

            if index == 1:
                try:    
                    valor = t_start.strftime('%H:%M') + ' - ' + t_end.strftime('%H:%M')
                    ev1.markdown('<div class="highlight0"><h2 class="fonte1">{}</h2></div>'.format(valor), unsafe_allow_html=True)
                    ev1.markdown('<div class="highlight1"><h2 class="fonte1">{}</h2></div>'.format(event['summary']), unsafe_allow_html=True)

                except:
                    ev1.error('Evento sem informacao')

            if index == 2:
                try:    
                    valor = t_start.strftime('%H:%M') + ' - ' + t_end.strftime('%H:%M')
                    ev2.markdown('<div class="highlight0"><h2 class="fonte1">{}</h2></div>'.format(valor), unsafe_allow_html=True)
                    ev2.markdown('<div class="highlight1"><h2 class="fonte1">{}</h2></div>'.format(event['summary']), unsafe_allow_html=True)

                except:
                    ev2.error('Evento sem informacao')

            if index == 3:
                try:    
                    valor = t_start.strftime('%H:%M') + ' - ' + t_end.strftime('%H:%M')
                    ev3.markdown('<div class="highlight0"><h2 class="fonte1">{}</h2></div>'.format(valor), unsafe_allow_html=True)
                    ev3.markdown('<div class="highlight1"><h2 class="fonte1">{}</h2></div>'.format(event['summary']), unsafe_allow_html=True)

                except:
                    ev3.error('Evento sem informacao')

            if index == 4:
                try:    
                    valor = t_start.strftime('%H:%M') + ' - ' + t_end.strftime('%H:%M')
                    ev4.markdown('<div class="highlight0"><h2 class="fonte1">{}</h2></div>'.format(valor), unsafe_allow_html=True)
                    ev4.markdown('<div class="highlight1"><h2 class="fonte1">{}</h2></div>'.format(event['summary']), unsafe_allow_html=True)

                except:
                    ev4.error('Evento sem informacao')

            if index == 5:
                try:    
                    valor = t_start.strftime('%H:%M') + ' - ' + t_end.strftime('%H:%M')
                    ev5.markdown('<div class="highlight0"><h2 class="fonte1">{}</h2></div>'.format(valor), unsafe_allow_html=True)
                    ev5.markdown('<div class="highlight1"><h2 class="fonte1">{}</h2></div>'.format(event['summary']), unsafe_allow_html=True)

                except:
                    ev5.error('Evento sem informacao')

            if index == 6:
                try:    
                    valor = t_start.strftime('%H:%M') + ' - ' + t_end.strftime('%H:%M')
                    ev6.markdown('<div class="highlight0"><h2 class="fonte1">{}</h2></div>'.format(valor), unsafe_allow_html=True)
                    ev6.markdown('<div class="highlight1"><h2 class="fonte1">{}</h2></div>'.format(event['summary']), unsafe_allow_html=True)

                except:
                    ev6.error('Evento sem informacao')

            if index == 7:
                try:    
                    valor = t_start.strftime('%H:%M') + ' - ' + t_end.strftime('%H:%M')
                    ev7.markdown('<div class="highlight0"><h2 class="fonte1">{}</h2></div>'.format(valor), unsafe_allow_html=True)
                    ev7.markdown('<div class="highlight1"><h2 class="fonte1">{}</h2></div>'.format(event['summary']), unsafe_allow_html=True)

                except:
                    ev7.error('Evento sem informacao')

            index += 1    
            
    # soma mais um ao dia da semana
    st.session_state.key += 1      
      
    if (st.session_state.key - 1) > (restante - 2):
        st.session_state.key = 1
        
    # atualiza a cada 30 segundos
    st_autorefresh(interval=0.5 * 60 * 1000, key="dataframerefresh")

    
if __name__ == '__main__':
    main()

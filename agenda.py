from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import time
import json
from datetime import timedelta


st.set_page_config(
	page_title="Calendar",
	layout="wide",
)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
	"""Shows basic usage of the Google Calendar API.
	st.writes the start and name of the next 10 events on the user's calendar.
	"""

	creds = Credentials.from_authorized_user_file('token.json', SCOPES)

	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)

	service = build('calendar', 'v3', credentials=creds)

	# Call the Calendar API
	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	now_date = datetime.datetime.utcnow()
	events_result = service.events().list(calendarId='primary', timeMin=now,
										maxResults=100, singleEvents=True,
										orderBy='startTime').execute()
	events = events_result.get('items', [])

	# constantes para formatacao da data	
	Diasemana = ('Segundasfeira','Terca-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sabado','Domingo')
	Meses = ('Janeiro','Fevereiro','Marco','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro')
	
	# formatacao da data para gerar o titulo
	mes = (now_date.month-1)
	diadasemana = now_date.weekday()
	titulo = Diasemana[int(diadasemana)] + ', ' + now_date.strftime("%d") + ' de ' + Meses[int(mes)] + ' de ' + now_date.strftime("%Y")
	atualizacao_h = now_date - timedelta(hours=3, minutes=0)
	atualizacao = atualizacao_h.strftime("%H:%M:%S")
	
	tit, update = st.columns([8,2])
	
	tit.title(titulo)	
	update.write('Última atualização: ' + atualizacao)
	
	# organizacao do sidebar
	
	telas = ['Todos os eventos', 'Eventos do dia', 'Eventos da semana', 'Eventos fixos']
	tela = st.sidebar.radio('Selecione os eventos que deseja visualizar', telas)
	
	automatico = st.sidebar.radio('Alteracao automatica de tela', ['Sim', 'Nao'])
	if automatico == 'Nao':
		#agenda = st.sidebar.radio('Agenda', telas)
		
		#if agenda == 'Diaria':
		#	st.session_state['key'] = 1
		#elif agenda == 'Semanal':
		#	st.session_state['key'] = 2
		pass
	else:
		minutos = st.sidebar.number_input('Intervalo de refresh em minutos', min_value=1, max_value=10, value=5)
	
	# difine um estado inicial para as telas
	if 'key' not in st.session_state:
		st.session_state['key'] = 1
	
	# mensagem para avisar que nao ha eventos
	if not events:
		st.write('No upcoming events found.')
	
	# eventos do dia
	if (tela == 'Todos os eventos') or (tela == 'Eventos do dia'):
		# organizacao dos dados
		st.markdown('O que esta rolando hoje ' + ":alarm_clock:" )
		ev0, ev1, ev2, ev3, ev4, ev5, ev6, ev7 = st.columns(8)
		ev0_, ev1_, ev2_, ev3_, ev4_, ev5_, ev6_, ev7_ = st.columns(8)
		#dia, semana = st.columns([2, 6])
		
	# eventos da semana
	if (tela == 'Todos os eventos') or (tela == 'Eventos fixos'):
		st.subheader('Eventos fixos :lower_left_ballpoint_pen:')

		# eventos fixos
		st.warning('** :clock2: 08:30 - 08:45 **')
		st.warning(':grey_exclamation: ' + '** Reunião diária do PAF    **')
		with st.expander('Detalhes do evento'):
			st.warning('Definir detalhes')

		st.warning('** :clock2: 08:40 - 09:00 **')
		st.warning(':grey_exclamation: ' + '** Reunião diária engenharia**')
		with st.expander('Detalhes do evento'):
			st.warning('Definir detalhes')

		st.warning('** :clock2: 09:00 - 09:40 **')
		st.warning(':grey_exclamation: ' + '** Reunião de produtividade **')
		with st.expander('Detalhes do evento'):
			st.warning('Definir detalhes')

		st.warning('** :clock2: 09:40 - 10:20 **')
		st.warning(':grey_exclamation: ' + '** Reunião da L751          **')
		with st.expander('Detalhes do evento'):
			st.warning('Definir detalhes')

		st.warning('** :clock2: 10:30 - 10:30 **')
		st.warning(':grey_exclamation: ' + '** Reunião matinal logística**')
		with st.expander('Detalhes do evento'):
			st.warning('Definir detalhes')

		st.warning('** :clock2: 10:20 - 11:00 **')
		st.warning(':grey_exclamation: ' + '** Reunião da L752          **')
		with st.expander('Detalhes do evento'):
			st.warning('Definir detalhes')

		st.warning('** :clock2: 11:00 - 11:30 **')
		st.warning(':grey_exclamation: ' + '** Reunião de planejamento  **')	
		with st.expander('Detalhes do evento'):
			st.warning('Definir detalhes')

	# dia atual da semana
	dia_atual_semana = now_date.today().weekday()
	
	# dias restantes da semana
	restante = 7 - dia_atual_semana
	
	# Lista com as datas restantes excluindo o dia atual
	date_generated = [now_date + datetime.timedelta(days=x) for x in range(1, restante)]
	
	if (tela == 'Todos os eventos') or (tela == 'Eventos da semana'):
		st.subheader('Eventos da semana :spiral_calendar_pad:')
		date = st.sidebar.selectbox('Dia da semana', date_generated)
		
		for event in events:
			# formato da data
			formater = "%Y-%m-%dT%H:%M:%S"
			
			# dia para mostrar na tela
			#date = date_generated[(6 - dia_atual_semana + st.session_state.key - 3)]
			
			# formata data inicial
			start_time = event['start'].get('dateTime', event['start'].get('date'))
			t_start = datetime.datetime.strptime(start_time.replace('-03:00',''), formater)

			# formata data final
			end_time = event['end'].get('dateTime', event['end'].get('date'))
			t_end = datetime.datetime.strptime(end_time.replace('-03:00',''), formater)
					
			if t_start.day == date.day:
				try:	
					st.success(t_start.strftime(":clock2:" + '** %H:%M **') + ' - ' + t_end.strftime('** %H:%M **'))
					st.success(':grey_exclamation: ' + '**' + event['summary'] + '**')

				except:
					st.error('Evento sem informacao')

				with st.expander('Detalhes do evento'):
					# organizador
					dados = '**Organizador: \n **' + event['organizer'].get('email').split('@')[0] + '\n\n'

					# pessoas
					attendees = event['attendees']
					dados += '**Pessoas: \n **'
					for people in attendees:
						dados += '\n' + people['email'].split('@')[0]
					st.success(dados)

	# index das colunas
	index = 0
	if (tela == 'Todos os eventos') or (tela == 'Eventos do dia'):
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
			if t_start.day == now_date.day:
				if index == 0:
					try:	
						#ev0.markdown()
						ev0.info(t_start.strftime(":clock2:" + '** %H:%M **') + ' - ' + t_end.strftime('** %H:%M **'))
						ev0.info(':grey_exclamation: ' + '**' + event['summary'] + '**')

					except:
						ev0.error('Evento sem informacao')

					with ev0:
						with st.expander('Detalhes do evento'):
							# organizador
							dados = '**Organizador: \n **' + event['organizer'].get('email').split('@')[0] + '\n\n'

							# pessoas
							attendees = event['attendees']
							dados += '**Pessoas: \n **'
							for people in attendees:
								dados += '\n' + people['email'].split('@')[0]
							st.info(dados)

				if index == 1:
					try:	
						#ev1.markdown()
						ev1.info(t_start.strftime(":clock2:" + '** %H:%M **') + ' - ' + t_end.strftime('** %H:%M **'))
						ev1.info(':grey_exclamation: ' + '**' + event['summary'] + '**')

					except:
						ev1.error('Evento sem informacao')

					with ev1:
						with st.expander('Detalhes do evento'):
							# organizador
							dados = '**Organizador: \n **' + event['organizer'].get('email').split('@')[0] + '\n\n'

							# pessoas
							attendees = event['attendees']
							dados += '**Pessoas: \n **'
							for people in attendees:
								dados += '\n' + people['email'].split('@')[0]
							st.info(dados)


				if index == 2:
					try:	
						#ev2.markdown()
						ev2.info(t_start.strftime(":clock2:" + '** %H:%M **') + ' - ' + t_end.strftime('** %H:%M **'))
						ev2.info(':grey_exclamation: ' + '**' + event['summary'] + '**')

					except:
						ev2.error('Evento sem informacao')

					with ev2:
						with st.expander('Detalhes do evento'):
							# organizador
							dados = '**Organizador: \n **' + event['organizer'].get('email').split('@')[0] + '\n\n'

							# pessoas
							attendees = event['attendees']
							dados += '**Pessoas: \n **'
							for people in attendees:
								dados += '\n' + people['email'].split('@')[0]
							st.info(dados)


				if index == 3:
					try:	
						#ev3.markdown()
						ev3.info(t_start.strftime(":clock3:" + '** %H:%M **') + ' - ' + t_end.strftime('** %H:%M **'))
						ev3.info(':grey_exclamation: ' + '**' + event['summary'] + '**')

					except:
						ev3.error('Evento sem informacao')

					with ev3:
						with st.expander('Detalhes do evento'):
							# organizador
							dados = '**Organizador: \n **' + event['organizer'].get('email').split('@')[0] + '\n\n'

							# pessoas
							attendees = event['attendees']
							dados += '**Pessoas: \n **'
							for people in attendees:
								dados += '\n' + people['email'].split('@')[0]
							st.info(dados)

				if index == 4:
					try:	
						#ev4.markdown()
						ev4.info(t_start.strftime(":clock4:" + '** %H:%M **') + ' - ' + t_end.strftime('** %H:%M **'))
						ev4.info(':grey_exclamation: ' + '**' + event['summary'] + '**')

					except:
						ev4.error('Evento sem informacao')

					with ev4:
						with st.expander('Detalhes do evento'):
							# organizador
							dados = '**Organizador: \n **' + event['organizer'].get('email').split('@')[0] + '\n\n'

							# pessoas
							attendees = event['attendees']
							dados += '**Pessoas: \n **'
							for people in attendees:
								dados += '\n' + people['email'].split('@')[0]
							st.info(dados)

				if index == 5:
					try:	
						#ev5.markdown()
						ev5.info(t_start.strftime(":clock5:" + '** %H:%M **') + ' - ' + t_end.strftime('** %H:%M **'))
						ev5.info(':grey_exclamation: ' + '**' + event['summary'] + '**')

					except:
						ev5.error('Evento sem informacao')

					with ev5:
						with st.expander('Detalhes do evento'):
							# organizador
							dados = '**Organizador: \n **' + event['organizer'].get('email').split('@')[0] + '\n\n'

							# pessoas
							attendees = event['attendees']
							dados += '**Pessoas: \n **'
							for people in attendees:
								dados += '\n' + people['email'].split('@')[0]
							st.info(dados)


				if index == 6:
					try:	
						#ev6.markdown()
						ev6.info(t_start.strftime(":clock6:" + '** %H:%M **') + ' - ' + t_end.strftime('** %H:%M **'))
						ev6.info(':grey_exclamation: ' + '**' + event['summary'] + '**')

					except:
						ev6.error('Evento sem informacao')

					with ev6:
						with st.expander('Detalhes do evento'):
							# organizador
							dados = '**Organizador: \n **' + event['organizer'].get('email').split('@')[0] + '\n\n'

							# pessoas
							attendees = event['attendees']
							dados += '**Pessoas: \n **'
							for people in attendees:
								dados += '\n' + people['email'].split('@')[0]
							st.info(dados)

				if index == 7:
					try:	
						#ev7.markdown()
						ev7.error(t_start.strftime(":clock7:" + '** %H:%M **') + ' - ' + t_end.strftime('** %H:%M **'))
						ev7.error(':grey_exclamation: ' + '**' + event['summary'] + '**')

					except:
						ev7.error('Evento sem informacao')

					with ev7:
						with st.expander('Detalhes do evento'):
							# organizador
							dados = '**Organizador: \n **' + event['organizer'].get('email').split('@')[0] + '\n\n'

							# pessoas
							attendees = event['attendees']
							dados += '**Pessoas: \n **'
							for people in attendees:
								dados += '\n' + people['email'].split('@')[0]
							st.error(dados)

				index += 1	
								
		# eventos do dia que nao estao acontecendo agora
		#if t_start > now_date and t_start.day == now_date.day:
			
			#dia.info('Evento')
			
		#	try:
		#		dia.write('Evento: ' + event['summary'] + ' Inicio: ' + t_start.strftime('%H:%M') + ' Fim: ' + t_end.strftime('%H:%M'))
		#	except:
		#		dia.error('Evento sem informacao')			
		
		# demais eventos da semana
		#if t_start.day > now_date.day:
	
			#semana.info('Evento')
			
		#	try:
		#		semana.write('Evento: ' + event['summary'])
		#	except:
		#		semana.error('Evento sem informacao')
		
		##	semana.write('Inicio: ' + t_start.strftime('%d-%m-%Y Hora: %H:%M'))
		#	semana.write('Fim: ' + t_end.strftime('%d-%m-%Y Hora: %H:%M'))
				
	if automatico == 'Sim':	
		st.session_state.key += 1
		
	if automatico == 'Sim' and st.session_state.key > (restante - 1):
		st.session_state.key = 1
		
	# update every  mins
	st_autorefresh(interval=minutos * 60 * 1000, key="dataframerefresh")
			
	
if __name__ == '__main__':
	
	main()
	
	# update every  mins
	
	
	# carrega pagina html
	#htmlfile = open('card1.html', 'r', encoding='utf-8')
	#source = htmlfile.read()
	
	#components.html(source)
	



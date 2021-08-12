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
import pyrebase
import jwt

st.set_page_config(
	page_title="Calendar",
	layout="wide",
)

from google.cloud import storage

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def main():
	"""Shows basic usage of the Google Calendar API.
	st.writes the start and name of the next 10 events on the user's calendar.
	"""
	
	#download_blob('lid-rastr-55a66.appspot.com', 'credentials.json', 'credentials.json')
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
		
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.json', 'w') as token:
			token.write(creds.to_json())

	service = build('calendar', 'v3', credentials=creds)

	# Call the Calendar API
	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	now_date = datetime.datetime.utcnow()
	events_result = service.events().list(calendarId='primary', timeMin=now,
										maxResults=10, singleEvents=True,
										orderBy='startTime').execute()
	events = events_result.get('items', [])

	# constantes para formatacao da data	
	Diasemana = ('Segundasfeira','Terca-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sabado','Domingo')
	Meses = ('Janeiro','Fevereiro','Marco','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro')
	
	# formatacao da data para gerar o titulo
	mes = (now_date.month-1)
	diadasemana = now_date.weekday()
	titulo = Diasemana[int(diadasemana)] + ', ' + now_date.strftime("%d") + ' de ' + Meses[int(mes)] + ' de ' + now_date.strftime("%Y")
	st.title(titulo)	
	
	# organizacao do sidebar
	automatico = st.sidebar.radio('Alteracao automatica de tela', ['Sim', 'Nao'])
	telas = ['Diaria', 'Semanal']
	
	if automatico == 'Nao':
		agenda = st.sidebar.radio('Agenda', telas)
		
		if agenda == 'Diaria':
			st.session_state['key'] = 1
		elif agenda == 'Semanal':
			st.session_state['key'] = 2
	
	# difine um estado inicial para as telas
	if 'key' not in st.session_state:
		st.session_state['key'] = 1
	
	# mensagem para avisar que nao ha eventos
	if not events:
		st.write('No upcoming events found.')
		
	# organizacao dos dados
	st.markdown('O que esta rolando hoje ' + ":alarm_clock:" )
	ev0, ev1, ev2, ev3, ev4, ev5, ev6, ev7 = st.columns(8)
	ev0_, ev1_, ev2_, ev3_, ev4_, ev5_, ev6_, ev7_ = st.columns(8)
	dia, semana = st.columns(2)	
	dia.subheader('Eventos fixos :lower_left_ballpoint_pen:')
	semana.subheader('Eventos da semana :spiral_calendar_pad:')

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
		if t_start.day == now_date.day:
			if index == 0:
				try:	
					#ev0.markdown()
					ev0.info(t_start.strftime(":clock2:" + '** %H:%M **') + ' - ' + t_end.strftime('** %H:%M **'))
					ev0.info(':grey_exclamation: ' + '**' + event['summary'] + '**')
					
				except:
					ev0.error('Evento sem informacao')
					
				with ev0_:
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
					
				with ev1_:
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
					
				with ev2_:
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
					
				with ev3_:
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
					
				with ev4_:
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
					
				with ev5_:
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
					
				with ev6_:
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
					
				with ev7_:
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
		if t_start > now_date and t_start.day == now_date.day:
			
			#dia.info('Evento')
			
			try:
				dia.write('Evento: ' + event['summary'] + ' Inicio: ' + t_start.strftime('%H:%M') + ' Fim: ' + t_end.strftime('%H:%M'))
			except:
				dia.error('Evento sem informacao')			
		
		# demais eventos da semana
		if t_start.day > now_date.day:
	
			#semana.info('Evento')
			
			try:
				semana.write('Evento: ' + event['summary'])
			except:
				semana.error('Evento sem informacao')
		
			semana.write('Inicio: ' + t_start.strftime('%d-%m-%Y Hora: %H:%M'))
			semana.write('Fim: ' + t_end.strftime('%d-%m-%Y Hora: %H:%M'))
				
	if automatico == 'Sim':	
		st.session_state.key += 1
		
	if automatico == 'Sim' and st.session_state.key > 3:
			st.session_state.key = 1
			
			
	
if __name__ == '__main__':
	minutos = st.sidebar.number_input('Intervalo de refresh em minutos', min_value=1, max_value=10, value=5)
	main()
	
	# update every  mins
	st_autorefresh(interval=minutos * 60 * 1000, key="dataframerefresh")
	
	# carrega pagina html
	#htmlfile = open('card1.html', 'r', encoding='utf-8')
	#source = htmlfile.read()
	
	#components.html(source)
	



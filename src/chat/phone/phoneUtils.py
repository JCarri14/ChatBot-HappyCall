from twilio.rest import Client
import smtplib #IMPORTANT: Not installed

SERVER_EMAIL = 'eltelefonodelaalegria@gmail.com'
SERVER_PASSW = 'perniamola'

def notify_emergency_services(text_to_send, email_receiver):
    mensajeAEnviar = 'Hola, una de nuestros clientes esta entrando en pánico, por favor contacten con el lo mas rapido posible. Condemor, pecadores!!!!'
    asunto = 'URGENTE: Persona en peligro'
    servidor = smtplib.SMTP('smtp.gmail.com', 587)
    servidor.starttls()
    servidor.login(SERVER_EMAIL, SERVER_PASSW)
    email = 'Subject: {}\n\n{}'.format(asunto, mensajeAEnviar).encode('utf-8')
    servidor.sendmail(SERVER_EMAIL, email_receiver, email)
    servidor.quit()

def call_emergency_services():
    # Llamamos a alguien
    account_sid = "AC53d652a3d4fb636c19416147f8d913bc"
    auth_token = "3df095e2ac672b591bb006405db18be7"
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        to="+34699904428",
        from_="+14059286138",
        url="http://127.0.0.1/imagine.xml"
        )
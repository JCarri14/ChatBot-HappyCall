from twilio.rest import Client

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
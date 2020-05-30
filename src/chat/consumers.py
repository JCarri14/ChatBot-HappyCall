# chat/consumers.py
import json, os
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.protocols.protocolController import ProtocolController
from chat.ddbb.MongoODMManager import MongoODMManager


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        user_input = text_data_json['message']
        project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
        session_id = self.room_group_name
        
        message = ProtocolController(project_id, session_id).handle_input(user_input) 
        
        response = [
            {
            'sender': "user-mssg",
            'text': user_input
            },
            {
            'sender': "bot-mssg",
            'text': message
            },
        ]
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': response
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))


class DashboardConsumer(WebsocketConsumer):
    def connect(self):
        #self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'control'
        self.accept()

    def disconnect(self, close_code):
        print("Control Socker closing with code: " + str(close_code))

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['request']
        
        if "update" in message:
            dbManager = MongoODMManager("localhost", "27017", "happy_call")
            c = list(dbManager.get_conversations())
            if c and len(c) > 0:
                c = [c[i].name for i in range(len(c)) if c[i].name]
            for cId in c:
                self.send_message("conversation", cId)  

    # Receive message from room group
    def chat_message(self, event):
        print()

    def send_message(self, sender, text):
        self.send(text_data=json.dumps({
            'sender': sender,
            'text': text
        }))

    def send_message_to_all(self, sender, text):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'sender': sender,
                'message': text
            }
        )

class ReadOnlyChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
    
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['request']
        
        #if "update" in message:
            #print()
            #TODO: get chats information
            
    # Receive message from room group
    def chat_message(self, event):
        # Send message to WebSocket
        print(event['message'])
        for m in event['message']:
            self.send(text_data=json.dumps({
                'message': m
            }))

    def send_message(self, sender, text):
        response = {
            'sender': sender,
            'text': text
        }
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': text
        }))

    def send_message_to_all(self, sender, text):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'sender': sender,
                'message': text
            }
        )

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

        # Send message to room group
        self.send_message_to_all([{'sender': "user-mssg", 'text': user_input}])
        
        project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
        session_id = self.room_group_name
        message = ProtocolController(project_id, session_id).handle_input(user_input) 
        
        # Send message to room group
        self.send_message_to_all([{'sender': "bot-mssg", 'text': message}])        

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
    
    def send_message_to_all(self, text):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': "chat_message",
                'message': text
            }
        )

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
        self.dbManager = MongoODMManager("localhost", "27017", "happy_call")
    
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
        conversation = []
        data = {}
        conversation = self.dbManager.get_conversation_by_name(self.room_group_name)
        data = self.treat_information(conversation)
        
        for m in event['message']:
            self.send(text_data=json.dumps({
                'message': m,
                'data': data
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

    def treat_information(self, conversation):
        response = {
            "conversation":{},
            "witness":{},
            "witness_sentiments":{},
            "emergency":{},
            "victim":{},
            "aggressor": {}
        }
        response["conversation"]["name"] = conversation.name
        response["conversation"]["date"] = conversation.created_at.isoformat()
               
        if conversation.witness:
            person = conversation.witness
            response["witness"]["name"] = person.name    
            response["witness"]["role"] = person.role       
            response["witness"]["description"] = person.description  
            response["witness"]["preferences"] = person.preferences
            response["witness"]["dislikes"] = person.dislikes
            response["witness"]["aggressions"] = person.healthContext.aggressions  
            response["witness"]["injuries"] = person.healthContext.injuries         
            response["witness_sentiments"] = person.sentimentCoefficients

        if conversation.curr_emergency:
            emergency = conversation.curr_emergency
            response["emergency"]["type"] = emergency.etype
            response["emergency"]["location"] = emergency.location 
            response["emergency"]["pers_involved"] = emergency.num_involved 
            response["emergency"]["active"] = emergency.is_active
        
            if emergency.pers_involved:
                for person in emergency.pers_involved:
                    if person.role == "Victim":
                        response["victim"]["name"] = person.name
                        response["victim"]["status"] = person.healthContext.status
                        response["victim"]["description"] = person.description
                        response["victim"]["aggressions"] = person.healthContext.aggressions  
                        response["victim"]["injuries"] = person.healthContext.injuries 

                    elif person.role == "Aggressor":
                        response["aggressor"]["name"] = person.name
                        response["aggressor"]["description"] = person.description
        return response
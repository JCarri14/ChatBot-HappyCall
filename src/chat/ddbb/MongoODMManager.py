from pymodm.connection import connect
from chat.models import *

class MongoODMManager:

    __base_url = "mongodb://"
    __host = "localhost"
    __port = "27017"
    __database = "happy_call"

    def __init__(self, host, port, database):
            connect(self.__base_url + self.__host + ":" 
                    + self.__port + "/" + self.__database, alias="default")
    
    def insert_conversation(self, conversation):
        conversation.save()
    
    def get_conversations(self, name):
        return Conversation.objects.all()

    def get_conversation_by_name(self, conversation_name):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        return c
    
    def get_conversation_messages(self, conversation_name):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        return c.messages
    
    def add_message(self, conversation_name, message):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        c.messages.append(message)
        Conversation.objects.raw({'name': conversation_name}).update(
            {'$set': {'messages': c.messages}})

    def insert_emergency(self, conversation_name, emergency):
        e = emergency.save()
        Conversation.objects.raw({'name': conversation_name}).update(
            {'$set': {'emergency': e._id}})
    
    def get_emergencies(self):
        res = Emergency.objects.all()
        return res
    
    def update_emergencies_persons(self, type, persons):
        Emergency.objects.raw({'etype': type}).update(
            {'$set': {'pers_involved': persons}})

    def get_emergencies_by_type(self, type):
        res = Emergency.objects.raw({'etype': type})
        return res
    
    def get_person_moods(self, conversation_name):
        c = Conversation.object.raw({'name': conversation_name})
        eID = c.emergency
        e = Emergency.object.raw({"_id": eID})
        res = e.pers_involved[0].healthContext.disorders
        return res
    
    def update_person_moods(self, conversation_name, moods):
        c = Conversation.object.raw({'name': conversation_name})
        eID = c.emergency
        e = Emergency.object.raw({"_id": eID})
        res = e.pers_involved[0].healthContext.disorders
        
    
    def get_person_coefficients(self, conversation_name):
        c = Conversation.object.raw({'name': conversation_name})
        eID = c.emergency
        e = Emergency.object.raw({"_id": eID})
        res = e.pers_involved[0].sentimentCoefficients
        return res
    
    def update_person_coefficients(self, conversation_name, coefficients):
        c = Conversation.object.raw({'name': conversation_name})
        eID = c.emergency
        e = Emergency.object.raw({"_id": eID})
        res = e.pers_involved[0].sentimentCoefficients
        




    

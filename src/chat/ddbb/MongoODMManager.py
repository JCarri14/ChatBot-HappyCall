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

    def insert_emergency(self, emergency):
        e = emergency.save()
        return e._id
    
    def link_emergency_to_conversation(self, conversation_name, eId):
        Conversation.objects.raw({'name': conversation_name}).update(
            {'$set': {'emergency': eId}})
    
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
        # .raw returns a queryset, as it's assured each conversation has its unique name we can do the following
        c = Conversation.objects.raw({'name': conversation_name})[0]
        return c.emergency.pers_involved[0].healthContext.disorders
    
    def insert_person(self, person):
        p = person.save()
        return p._id

    def link_person_to_emergency(self, conversation_name, pId):
        e = Conversation.objects.raw({'name': conversation_name})[0].emergency
        e.pers_involved = [] 
        e.pers_involved.append(pId) 
        e.num_involved += 1
        Emergency.objects.raw({'_id': e._id}).update(
            {'$set': {'pers_involved': e.pers_involved, 'num_involved': e.num_involved}})

    def update_person_moods(self, conversation_name, moods):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        p = c.emergency.pers_involved[0]
        p.healthContext.disorders = moods
        Person.objects.raw({"_id": p._id}).update(
            {'$set': {'healthContext.disorders': moods}})       
    
    def get_person_coefficients(self, conversation_name):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        return c.emergency.pers_involved[0].sentimentCoefficients
        
    def update_person_coefficients(self, conversation_name, coefficients):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = c.emergency 
        e.pers_involved[0].sentimentCoefficients = coefficients
        Emergency.objects.raw({"_id": e._id}).update(
            {'$set': {'pers_involved': e.pers_involved}})         

    

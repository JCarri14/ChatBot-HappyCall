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
    
    ########################## INSERTIONS ##########################

    def insert_conversation(self, conversation):
        c = conversation.save()
        return c.name
    
    def insert_emergency(self, emergency):
        e = emergency.save()
        return e._id
    
    def insert_person(self, person):
        p = person.save()
        return p._id
    
    def add_message(self, conversation_name, sender, text):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        Conversation.objects.raw({'name': conversation_name}).update(
            {'$push': {'messages': { '$each': [ {"text": text, "sender": sender} ]}}})
    
    def add_location(self, conversation_name, emergency_id, location):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        Emergency.objects.raw({'_id': emergency_id}).update(
            {'$push': {'location': { '$each': [ location ]}}})

    ########################## LINKERS ##########################

    def link_person_to_conversation(self, conversation_name, pId):
        Conversation.objects.raw({'name': conversation_name}).update(
            {'$set': {'witness': pId}})

    def link_emergency_to_conversation(self, conversation_name, eId):
        Conversation.objects.raw({'name': conversation_name}).update(
            {'$set': {'emergency': eId}})

    def link_person_to_emergency(self, conversation_name, pId):
        e = Conversation.objects.raw({'name': conversation_name})[0].emergency
        e.pers_involved = [] 
        e.pers_involved.append(pId) 
        e.num_involved += 1
        Emergency.objects.raw({'_id': emergency_id}).update(
            {'$set': {'pers_involved': e.pers_involved, 
                    'num_involved': e.num_involved}})

    ########################## GETTERS ##########################
    # .raw returns a queryset, as it's assured each conversation has its unique name we can do the following

    def get_conversations(self):
        return Conversation.objects.all()

    def get_conversation_by_name(self, conversation_name):
        c = list(Conversation.objects.raw({'name': conversation_name}))[0]
        return c
    
    def get_conversation_messages(self, conversation_name):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        return c.messages
    
    def get_conversation_witness(self, conversation_name):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        return c.witness
    
    def get_witness(self, conversation_name):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        return c.witness

    def get_witness_moods(self, conversation_name):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        return c.witness.healthContext.disorders
    
    def get_witness_coefficients(self, conversation_name):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        return c.witness.sentimentCoefficients
    
    def get_emergencies(self):
        res = Emergency.objects.all()
        return res

    def get_emergencies_by_type(self, type):
        res = Emergency.objects.raw({'etype': type})
        return res
    
    def get_victims(self, conversation_name, emergency_id):
        e = Emergency.objects.raw({'etype': type})[0]
        return e.pers_involved

    def get_person_moods(self, conversation_name, emergency_id, role):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        p = self.get_person_from_emergency(e.pers_involved, role)
        return p.healthContext.disorders
    
    def get_person_coefficients(self, conversation_name, emergency_id, role):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        p = self.get_person_from_emergency(e.pers_involved, role)
        return p.sentimentCoefficients
    
    def get_emergency_from_conversation(self, emergencies, search_type):
        for e in emergencies:
            if e.etype == search_type:
                return e
        return None

    def get_person_from_emergency(self, persons, role):
        for p in persons:
            if p.role == role:
                return p
        return None
        
    ########################## UPDATES ##########################

    def update_witness_name(self, conversation_name, name):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        p = c.witness
        Person.objects.raw({"_id": p._id}).update(
            {'$set': {'name': name}})

    def update_witness_moods(self, conversation_name, moods):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        p = c.witness
        Person.objects.raw({"_id": p._id}).update(
            {'$set': {'healthContext.disorders': moods}})
    
    def update_witness_coefficients(self, conversation_name, coefficients):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        p = c.witness
        Person.objects.raw({"_id": p._id}).update(
            {'$set': {'sentimentCoefficients': coefficients}})  
    
    def update_witness_description(self, conversation_name, descriptions):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        p = c.witness
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'description': { '$each': descriptions}}})
    
    def update_witness_diseases(self, conversation_name, diseases):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        p = c.witness
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'diseases': { '$each': diseases}}})
    
    def update_witness_injuries(self, conversation_name, injuries):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        p = c.witness
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'injuries': { '$each': injuries}}})

    def update_witness_preferences(self, conversation_name, preferences):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        p = c.witness
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'preferences': { '$each': preferences}}})
    
    def update_witness_dislikes(self, conversation_name, dislikes):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        p = c.witness
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'dislikes': { '$each': dislikes}}})
    
    def update_witness_aggressions(self, conversation_name, aggressions):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        p = c.witness
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'healthContext.aggressions': { '$each': aggressions}}})

    def update_emergency_type(self, conversation_name, new_type):
        #c = Conversation.objects.raw({'name': conversation_name})[0]
        #e = self.get_emergency_from_conversation(c.emergencies, EmergencyTypes.Normal.value)
        Emergency.objects.raw({'_id': emergency_id}).update(
            {'$set': {'etype': new_type}})

    def update_emergency_type(self, conversation_name, emergency_id, new_type):
        #c = Conversation.objects.raw({'name': conversation_name})[0]
        #e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        Emergency.objects.raw({'_id': emergency_id}).update(
            {'$set': {'etype': new_type}})

    def update_emergency_persons(self, conversation_name, emergency_id, persons_ids):
        #c = Conversation.objects.raw({'name': conversation_name})[0]
        #e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        Emergency.objects.raw({'_id': emergency_id}).update(
            {'$push': {'pers_involved': { '$each': persons_ids}}})
    
    def update_emergency_num_persons(self, conversation_name, emergency_id, num):
        e = Emergency.objects.raw({"_id": emergency_id})[0]
        if not e.num_involved:
            e.num_involved = 0
        e.num_involved += num
        Emergency.objects.raw({"_id": e._id}).update(
                    {'$set': {'num_involved': e.num_involved}}) 

    def update_person_moods(self, conversation_name, emergency_id, role, moods):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        p = self.get_person_from_emergency(e.pers_involved, role)
        Person.objects.raw({"_id": p._id}).update(
            {'$set': {'healthContext.disorders': moods}})       
    
    def update_person_coefficients(self, conversation_name, emergency_id, role, coefficients):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        p = self.get_person_from_emergency(e.pers_involved, role)
        Person.objects.raw({"_id": p._id}).update(
            {'$set': {'sentimentCoefficients': coefficients}})  

    def update_person_description(self, conversation_name, emergency_id, role, descriptions):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        p = self.get_person_from_emergency(e.pers_involved, role)
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'description': { '$each': descriptions}}})
    
    def update_person_preferences(self, conversation_name, emergency_id, role, preferences):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        p = self.get_person_from_emergency(e.pers_involved, role)
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'preferences': { '$each': preferences}}})
    
    def update_person_dislikes(self, conversation_name, emergency_id, role, dislikes):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        p = self.get_person_from_emergency(e.pers_involved, role)
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'dislikes': { '$each': dislikes}}})
    
    def update_person_aggressions(self, conversation_name, emergency_id, role, aggressions):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        p = self.get_person_from_emergency(e.pers_involved, role)
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'healthContext.aggressions': { '$each': aggressions}}}) 

    def update_person_disorders(self, conversation_name, emergency_id, role, disorders):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        p = self.get_person_from_emergency(e.pers_involved, role)
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'healthContext.disorders': { '$each': disorders}}})

    def update_person_injuries(self, conversation_name, emergency_id, role, injuries):
        c = Conversation.objects.raw({'name': conversation_name})[0]
        e = self.get_emergency_from_conversation(c.emergencies, emergency_id)
        p = self.get_person_from_emergency(e.pers_involved, role)
        Person.objects.raw({'_id': p._id}).update(
            {'$push': {'healthContext.injuries': { '$each': injuries}}})        

    

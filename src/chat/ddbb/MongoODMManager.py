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
        return {"id": e._id, "type": e.etype, "quantity_found": False}
    
    def insert_person(self, person):
        p = person.save()
        return p._id
    
    def add_message(self, conversation_name, sender, text):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            Conversation.objects.raw({'name': conversation_name}).update(
                {'$push': {'messages': { '$each': [ {"text": text, "sender": sender} ]}}})
        except:
            print("Exception: Could not find Conversation [Add message]")
    
    def add_location(self, emergency_id, location):
        try:
            Emergency.objects.raw({'_id': emergency_id}).update(
                {'$push': {'location': { '$each': [ location ]}}})
        except:
            print("Exception: Could not update Emergency [Add location]")

    def add_emergency(self, conversation_name, emergency_id):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            Conversation.objects.raw({'name': conversation_name}).update(
                {'$addToSet': {'emergencies': emergency_id}})
        except:
            print("Exception: Could not update Conversation [Add Emergency]")

    ########################## LINKERS ##########################

    def link_person_to_conversation(self, conversation_name, pId):
        try:
            Conversation.objects.raw({'name': conversation_name}).update(
                {'$set': {'witness': pId}})
        except:
            print("Exception: Could not update Conversation [Link Person]")

    def link_emergency_to_conversation(self, conversation_name, eId):
        try:
            Conversation.objects.raw({'name': conversation_name}).update(
                {'$set': {'emergency': eId}})
        except:
            print("Exception: Could not update Conversation [Link Emergency]")

    def link_person_to_emergency(self, conversation_name, pId):
        try:
            e = Conversation.objects.raw({'name': conversation_name})[0].curr_emergency
            e.pers_involved = [] 
            e.pers_involved.append(pId) 
            e.num_involved += 1
            Emergency.objects.raw({'_id': emergency_id}).update(
                {'$set': {'pers_involved': e.pers_involved, 
                        'num_involved': e.num_involved}})
        except:
            print("Exception: Could not update Emergency [Link Person]")

    ########################## GETTERS ##########################
    # .raw returns a queryset, as it's assured each conversation has its unique name we can do the following

    def get_conversations(self):
        try:
            return Conversation.objects.all()
        except:
            print("Exception: Could not find conversations")
            return []

    def get_conversation_by_name(self, conversation_name):
        try:
            c = list(Conversation.objects.raw({'name': conversation_name}))[0]
            return c
        except:
            print("Exception: Could not find conversation")
            return None
    
    def get_conversation_messages(self, conversation_name):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            return c.messages
        except:
            print("Exception: Could not find conversation [messages]")
    
    def get_conversation_witness(self, conversation_name):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            return c.witness
        except:
            print("Exception: Could not find conversation [witness]")
            return None
    
    def get_witness(self, conversation_name):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            return c.witness
        except:
            print("Exception: Could not find witness")
            return None

    def get_witness_moods(self, conversation_name):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            return c.witness.healthContext.disorders
        except:
            print("Exception: Could not find witness [moods]")
            return []
    
    def get_witness_coefficients(self, conversation_name):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            return c.witness.sentimentCoefficients
        except:
            print("Exception: Could not find witness [coefficients]")
            return []
    
    def get_emergencies(self):
        try:
            res = Emergency.objects.all()
            return res
        except:
            print("Exception: Could not find emergencies")
            return []

    def get_emergencies_by_type(self, type):
        try:
            res = Emergency.objects.raw({'etype': type})
            return res
        except:
            print("Exception: Could not find emergency by type")
            return None

    def get_victims(self, emergency_id):
        try:
            e = Emergency.objects.raw({'_id': emergency_id})[0]
            return e.pers_involved
        except:
            print("Exception: Could not find emergency [victims]")
            return []

    def get_person_moods(self, conversation_name, role):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            e = c.curr_emergency
            p = self.get_person_from_emergency(e.pers_involved, role)
            return p.healthContext.disorders
        except:
            print("Exception: Could not find conversation [person moods]")
    
    def get_person_coefficients(self, conversation_name, role):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            e = c.curr_emergency
            p = self.get_person_from_emergency(e.pers_involved, role)
            return p.sentimentCoefficients
        except:
            print("Exception: Could not find conversation [person coefficients]")
    
    def get_emergency_from_conversation(self, emergencies, search_type):
        try:
            for e in emergencies:
                if e.etype == search_type:
                    return e
            return None
        except:
            print("Exception: Could not find emergencies")
            return None

    def get_person_from_emergency(self, persons, role):
        try:
            for p in persons:
                if p.role == role:
                    return p
            return None
        except:
            print("Exception: Could not find persons")
            return None
        
    ########################## UPDATES ##########################

    def update_current_emergency(self, conversation_name, emergency_id):
        try:
            Conversation.objects.raw({'name': conversation_name}).update(
                {'$set': {'curr_emergency': emergency_id}})
        except:
            print("Exception: Could not update conversation [curr_emergency]")

    def update_witness_name(self, conversation_name, name):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            p = c.witness
            Person.objects.raw({"_id": p._id}).update(
                {'$set': {'name': name}})
        except:
            print("Exception: Could not update witness [name]")
    
    def update_witness_role(self, conversation_name, role):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            p = c.witness
            Person.objects.raw({"_id": p._id}).update(
                {'$set': {'role': role}})
        except:
            print("Exception: Could not update witness [role]")

    def update_witness_moods(self, conversation_name, moods):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            p = c.witness
            Person.objects.raw({"_id": p._id}).update(
                {'$set': {'healthContext.disorders': moods}})
        except:
            print("Exception: Could not update witness [moods]")
    
    def update_witness_coefficients(self, conversation_name, coefficients):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            p = c.witness
            Person.objects.raw({"_id": p._id}).update(
                {'$set': {'sentimentCoefficients': coefficients}})
        except:
            print("Exception: Could not update witness [coefficients]")
    
    def update_witness_description(self, conversation_name, descriptions):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            p = c.witness
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'description': { '$each': descriptions}}})
        except:
            print("Exception: Could not update witness [description]")
    
    def update_witness_diseases(self, conversation_name, diseases):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            p = c.witness
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'diseases': { '$each': diseases}}})
        except:
            print("Exception: Could not update witness [diseases]")
    
    def update_witness_injuries(self, conversation_name, injuries):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            p = c.witness
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'injuries': { '$each': injuries}}})
        except:
            print("Exception: Could not update witness [injuries]")

    def update_witness_preferences(self, conversation_name, preferences):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            p = c.witness
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'preferences': { '$each': preferences}}})
        except:
            print("Exception: Could not update witness [preferences]")
    
    def update_witness_dislikes(self, conversation_name, dislikes):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            p = c.witness
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'dislikes': { '$each': dislikes}}})
        except:
            print("Exception: Could not update witness [dislikes]")
    
    def update_witness_aggressions(self, conversation_name, aggressions):
        try:
            c = Conversation.objects.raw({'name': conversation_name})[0]
            p = c.witness
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'healthContext.aggressions': { '$each': aggressions}}})
        except:
            print("Exception: Could not update witness [aggressions]")

    def update_emergency_type(self, emergency_id, new_type):
        try:
            Emergency.objects.raw({'_id': emergency_id}).update(
                {'$set': {'etype': new_type}})
        except:
            print("Exception: Could not update emergency [type]")

    def update_emergency_persons(self, emergency_id, persons_ids):
        try:
            Emergency.objects.raw({'_id': emergency_id}).update(
                {'$push': {'pers_involved': { '$each': persons_ids}}})
        except:
            print("Exception: Could not update emergency [persons]")
    
    def update_emergency_num_persons(self, emergency_id, num):
        try:
            e = Emergency.objects.raw({"_id": emergency_id})[0]
            if not e.num_involved:
                e.num_involved = 0
            e.num_involved += num
            Emergency.objects.raw({"_id": e._id}).update(
                        {'$set': {'num_involved': e.num_involved}}) 
        except:
            print("Exception: Could not update emergency [num_involved]")

    def update_person_moods(self, emergency_id, role, moods):
        try:
            e = Emergency.objects.raw({"_id": emergency_id})[0]
            p = self.get_person_from_emergency(e.pers_involved, role)
            Person.objects.raw({"_id": p._id}).update(
                {'$set': {'healthContext.disorders': moods}})
        except:
            print("Exception: Could not update person [moods]")       
    
    def update_person_coefficients(self, emergency_id, role, coefficients):
        try:
            e = Emergency.objects.raw({"_id": emergency_id})[0]
            p = self.get_person_from_emergency(e.pers_involved, role)
            Person.objects.raw({"_id": p._id}).update(
                {'$set': {'sentimentCoefficients': coefficients}})
        except:
            print("Exception: Could not update person [coefficients]")  

    def update_person_description(self, emergency_id, role, descriptions):
        try:
            e = Emergency.objects.raw({"_id": emergency_id})[0]
            p = self.get_person_from_emergency(e.pers_involved, role)
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'description': { '$each': descriptions}}})
        except:
            print("Exception: Could not update person [description]")
    
    def update_person_preferences(self, emergency_id, role, preferences):
        try:
            e = Emergency.objects.raw({"_id": emergency_id})[0]
            p = self.get_person_from_emergency(e.pers_involved, role)
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'preferences': { '$each': preferences}}})
        except:
            print("Exception: Could not update person [preferences]")
    
    def update_person_dislikes(self, emergency_id, role, dislikes):
        try:
            e = Emergency.objects.raw({"_id": emergency_id})[0]
            p = self.get_person_from_emergency(e.pers_involved, role)
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'dislikes': { '$each': dislikes}}})
        except:
            print("Exception: Could not update person [dislikes]")
    
    def update_person_aggressions(self, emergency_id, role, aggressions):
        try:
            e = Emergency.objects.raw({"_id": emergency_id})[0]
            p = self.get_person_from_emergency(e.pers_involved, role)
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'healthContext.aggressions': { '$each': aggressions}}})
        except:
            print("Exception: Could not update person [aggressions]") 

    def update_person_disorders(self, emergency_id, role, disorders):
        try:
            e = Emergency.objects.raw({"_id": emergency_id})[0]
            p = self.get_person_from_emergency(e.pers_involved, role)
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'healthContext.disorders': { '$each': disorders}}})
        except:
            print("Exception: Could not update person [disorders]")

    def update_person_injuries(self, emergency_id, role, injuries):
        try:
            e = Emergency.objects.raw({"_id": emergency_id})[0]
            p = self.get_person_from_emergency(e.pers_involved, role)
            Person.objects.raw({'_id': p._id}).update(
                {'$push': {'healthContext.injuries': { '$each': injuries}}})
        except:
            print("Exception: Could not update person [injuries]")        

    

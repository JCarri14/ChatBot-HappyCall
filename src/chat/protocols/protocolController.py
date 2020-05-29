from chat.dialogflow_api.dfManager import DialogflowManager
from chat.ddbb.MongoODMManager import MongoODMManager
from chat.nlp.sentenceTokenizer import *
from chat.models import *
from .protocolsUtils import *
import datetime

class ProtocolController:
    
    __instance = None
    __lang = "es"
    
    class __Manager:
        
        def __init__(self, project_id, session_id):
            self.dfManager =  DialogflowManager(project_id, session_id, "es")
            self.dbManager = MongoODMManager("localhost", "27017", "happy_call")
            self.conversation = Conversation(name=session_id)
            self.emergency = Emergency(etype=EmergencyTypes.Normal)
            self.emergency.num_involved = 1
            self.emergency.pers_involved.append(Person(role=Roles.Transmitter))
            #self.dbManager.insert_emergency(self.conversation.name, self.emergency)
    
    instance = None

    def __init__(self, project_id, session_id):
        if not ProtocolController.instance:
            ProtocolController.instance = ProtocolController.__Manager(project_id, session_id)
    
    def handle_input(self, text):
        if text == "END_CONVERSATION":
            #dbManager = MongoODMManager("localhost", "27017", "happy_call")
            self.instance.conversation.finished_at = datetime.datetime.utcnow
            self.instance.dbManager.insert_conversation(self.instance.conversation)
            return ""
        else:
            info = self.instance.dfManager.request_fulfillment_text(text)   
            res = self.handle_intent(text, info)
            return info['text']
    
    def handle_intent(self, text, info):
        if info['intent'] == "ProtocolAgressionWithVictim":
            return self.agressionWithVictim(info['text'], info['params'], text)

        elif info['intent'] == "ProtocolAgressionWithoutVictim":
            return self.agressionWithoutVictim(info['text'], info['params'], text)

        elif info['intent'] == "ProtocolAgressionIdentification":
            return self.agressionIdentification(info['text'], info['params'], text)

        elif info['intent'] == "Default Welcome Intent":
            return self.welcome(info['text'], info['params'], text)

        elif info['intent'] == "FrasesMood":
            return self.moodSentences(info['text'], info['params'], text)

        elif info['intent'] == "ProtocolSuicideAttempt":
            return self.suicideAttempt(info['text'], info['params'], text)

        elif info['intent'] == "ProtocolVictimIdentification":
            return self.victimIdentification(info['text'], info['params'], text)

        elif info['intent'] == "GetPreferences":
            return self.preferences(info['text'], info['params'], text)

        elif info['intent'] == "DangerSuicide":
            return self.dangerSuicide(info['text'], info['params'], text)

        elif info['intent'] == "DangerOthers":
            return self.dangerOthers(info['text'], info['params'], text)
        return text
    
    def agressionWithVictim(self, input, params, result):
    
        numPersons = checkPersonsQuantity(params)
        p_name = checkPersonName(params)
        p = Person(name=p_name)
        self.instance.emergency.pers_involved.append(p)
        #self.instance.dbManager.update_emergencies_persons(self.instance.emergency.etype,self.instance.emergency.pers_involved)
        return result

    def agressionWithoutVictim(self, input, params, result):
        return result

    def agressionIdentification(self, input, params, result):
        return result

    def welcome(self, input, params, result):
        person_name = checkPersonName(params)
        self.instance.emergency.pers_involved[0].name = person_name
        #dbManager = MongoODMManager("localhost", "27017", "happy_call")
        #self.instance.dbManager.update_emergencies_persons(self.instance.emergency.etype,
                                                #self.instance.emergency.pers_involved)
        return result

    def moodSentences(self, input, params, result):
        return result

    def victimIdentification(self, input, params, result):
        return result

    def suicideAttempt(self, input, params, result):
        return result

    def preferences(self, input, params, result):
        return result

    def dangerSuicide(self, input, params, result):
        return result

    def dangerOthers(self, input, params, result):
        return result
    
    
        





            


        
    
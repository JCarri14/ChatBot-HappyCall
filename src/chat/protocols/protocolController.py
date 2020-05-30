from chat.dialogflow_api.dfManager import DialogflowManager
from chat.ddbb.MongoODMManager import MongoODMManager
from chat.nlp.sentenceTokenizer import *
from chat.nlp.sentimentAnalyser import calculateSentiment
from chat.models import *
from .protocolsUtils import *
import datetime, re

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
            #self.emergency.pers_involved = []

            self.dbManager.insert_conversation(self.conversation)
            pId = self.dbManager.insert_person(defaultPerson())
            self.emergency.pers_involved.append(pId)
            eId = self.dbManager.insert_emergency(self.emergency)
            self.dbManager.link_emergency_to_conversation(self.conversation.name, eId)
    
    instance = None

    def __init__(self, project_id, session_id):
        if not ProtocolController.instance:
            ProtocolController.instance = ProtocolController.__Manager(project_id, session_id)
    
    def handle_input(self, text):
        if text == "END_CONVERSATION":
            self.instance.conversation.finished_at = datetime.datetime.utcnow
            return ""
        else:
            info = self.instance.dfManager.request_fulfillment_text(text)
            res, flag = self.checkMoodInfo(info['params'])
            if flag == 1:
                self.instance.dbManager.update_person_moods(self.instance.conversation.name, res)
                calculateSentiment(self.instance.dbManager, self.instance.conversation.name, res, "")
            res = self.handle_intent(text, info)
            return info['text']

    def checkMoodInfo(self, params):
        moods = self.instance.dbManager.get_person_moods(self.instance.conversation.name)
        flag = 0
        word = re.compile('mood_') 
        point = re.compile(".")

        for param in params:
            if params.get(param) and word.search(param) and "." not in param:
                m = param.split("_")[1]
                moods[m] += 1
                moods['counter'] += 1
                flag = 1
        return moods,flag
    
    def handle_intent(self, text, info):
        switcher = {
            "ProtocolAgressionWithVictim":self.agressionWithVictim(text, info['params'], info['text']),
            "ProtocolAgressionWithoutVictim":self.agressionWithoutVictim(text, info['params'], info['text']),
            "ProtocolAgressionIdentification (Without Context)":self.agressionIdentificationWithout(text, info['params'], info['text']),
            "ProtocolAgressionIdentification (With Context)":self.agressionIdentificationWith(text, info['params'], info['text']),
            "Default Welcome Intent":self.welcome(text, info['params'], info['text']),
            "ProtocolBleedingBase":self.bleedingBase(text, info['params'], info['text']),
            "ProtocolCriticalHealth":self.criticalHealth(text, info['params'], info['text']),
            "ProtocolFaintingBase":self.faintingBase(text, info['params'], info['text']),
            "ProtocolWoundBase":self.woundBase(text, info['params'], info['text']),
            "FrasesMood":self.moodSentences(text, info['params'], info['text']),
            "GetPreferences":self.getPreferences(text, info['params'], info['text']),
            "ProtocolSuicideAttempt":self.suicideAttempt(text, info['params'], info['text']),
            "ProtocolVictimIdentification":self.victimIdentification(text, info['params'], info['text']),
            "GetPreferences":self.preferences(text, info['params'], info['text']),
            "DangerSuicide":self.dangerSuicide(text, info['params'], info['text']),
            "DangerOthers":self.dangerOthers(text, info['params'], info['text'])
        }
        func = switcher.get(info['intent'], "Invalid intent" )
        if func != "Invalid intent":
            return func
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

    def agressionIdentificationWithout(self, input, params, result):
        return result
    
    def agressionIdentificationWith(self, input, params, result):
        return result

    def welcome(self, input, params, result):
        person_name = checkPersonName(params)
        self.instance.emergency.pers_involved[0].name = person_name
        #dbManager = MongoODMManager("localhost", "27017", "happy_call")
        #self.instance.dbManager.update_emergencies_persons(self.instance.emergency.etype,
                                                #self.instance.emergency.pers_involved)
        return result

    def bleedingBase(self, input, params, result):
        return result
    
    def criticalHealth(self, input, params, result):
        return result
    
    def faintingBase(self, input, params, result):
        return result
    
    def woundBase(self, input, params, result):
        return result

    def moodSentences(self, input, params, result):
        return result
    
    def getPreferences(self, input, params, result):
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
    
    
        





            


        
    
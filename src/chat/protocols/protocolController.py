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
            self.contexts = []
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
            text_response = self.handle_intent(text, info)
            return text_response

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
            "ProtocolAgressionWithVictim":self.agressionWithVictim,
            "ProtocolAgressionWithoutVictim":self.agressionWithoutVictim,
            "ProtocolAgressionIdentification (Without Context)":self.agressionIdentificationWithout,
            "ProtocolAgressionIdentification (With Context)":self.agressionIdentificationWith,
            "Default Welcome Intent":self.welcome,
            "ProtocolBleedingBase":self.bleedingBase,
            "ProtocolCriticalHealth":self.criticalHealth,
            "ProtocolFaintingBase":self.faintingBase,
            "ProtocolWoundBase":self.woundBase,
            "FrasesMood":self.moodSentences,
            "GetPreferences":self.getPreferences,
            "ProtocolSuicideAttempt":self.suicideAttempt,
            "ProtocolVictimIdentification":self.victimIdentification,
            "GetPreferences":self.preferences,
            "DangerSuicide":self.dangerSuicide,
            "DangerOthers":self.dangerOthers
        }
        func = switcher.get(info['intent'], "Invalid intent" )
        #print(list(self.instance.contexts))
        if func != "Invalid intent":
            text = func(text, info['params'], info['text'])
        self.instance.contexts = list(self.instance.dfManager.get_contexts())
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
        print("Holaa")
        return result
    
    def criticalHealth(self, input, params, result):
        return result
    
    def faintingBase(self, input, params, result):
        return result
    
    def woundBase(self, input, params, result):
        return result

    def moodSentences(self, input, params, result):
    
        words = [re.compile('healthCompleted') ,
                re.compile('protocolCompleted'),
                re.compile('followup'),
                re.compile('dialog_context')]
        flags = [0,0,0,0]
        for c in self.instance.contexts:
            print(c.name)
            for i in range(len(words)):
                if words[i].search(c.name):
                    flags[i] = 1
        self.instance.dfManager.set_contexts(self.instance.contexts)
        print(flags)
        if flags[3] == 1 or flags[2] == 1 or (flags[0] == 1 and flags[1] == 0) or (flags[0] == 0 and flags[1] == 1):
            return result + ". Pero ahora centremonos en la pregunta anterior, por favor." 
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
    
    
        





            


        
    
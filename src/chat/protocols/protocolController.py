from chat.dialogflow_api.dfManager import DialogflowManager
from chat.ddbb.MongoODMManager import MongoODMManager
from chat.nlp.sentenceTokenizer import *
from chat.nlp.sentimentAnalyser import calculateSentiment
from chat.models import *
from .protocolsUtils import *
import datetime, re

emergency_types = ["ProtocolAgressionWithVictim", "ProtocolAgressionWithoutVictim",
                "ProtocolMurder", "ProtocolBleedingBase", "ProtocolCriticalHealth"
                "ProtocolFaintingBase", "ProtocolWoundBase", "ProtocolCovid19",
                "ProtocolSuicideAttempt", "DangerSuicide", "DangerOthers" ]

class ProtocolController:
    
    __instance = None
    __lang = "es"

    class __Manager:
        
        def __init__(self, project_id, session_id):
            self.dfManager =  DialogflowManager(project_id, session_id, "es")
            self.dbManager = MongoODMManager("localhost", "27017", "happy_call")
            self.session_id = session_id
            self.session = {
                "conversation": 0,
                "emergencies": [],
                "witness": 0,
                "curr_emergency": {},
            }
            self.save_initial_session_values()
            self.contexts = list(self.dfManager.get_contexts())
        
        def save_initial_session_values(self):
            conversation = Conversation(name=self.session_id)
            self.session['witness'] = self.dbManager.insert_person(defaultPerson())
            self.session['curr_emergency'] = self.dbManager.insert_emergency(defaultEmergency())
            conversation.witness = self.session['witness']
            conversation.emergencies.append(self.session['curr_emergency']["id"])
            conversation.curr_emergency = self.session['curr_emergency']["id"]
            self.session['conversation'] = self.dbManager.insert_conversation(conversation)
            self.session['emergencies'].append(self.session['curr_emergency'])

    instance = None

    def __init__(self, project_id, session_id):
        if not ProtocolController.instance:
            ProtocolController.instance = ProtocolController.__Manager(project_id, session_id)       

    def handle_input(self, text):
        if text == "END_CONVERSATION":
            #self.instance.session['conversation'].finished_at = datetime.datetime.utcnow
            return ""
        else:
            #Saving input message into de ddbb
            self.instance.dbManager.add_message(self.instance.session['conversation'], "user-mssg", text)
            # Asking for Dialogflow response
            info = self.instance.dfManager.request_fulfillment_text(text)
            # Checking for any mood information given by Dialogflow response
            res, flag = self.checkMoodInfo(info['params'])
            if flag == 1:
                self.instance.dbManager.update_witness_moods(self.instance.session['conversation'], res)
                calculateSentiment(self.instance.dbManager, self.instance.session['conversation'], res, "")
            # Regarding the intent we're currently dealing with, we need to check for wanted parameters
            text_response = self.handle_intent(text, info)
            #Saving response message into de ddbb
            self.instance.dbManager.add_message(self.instance.session['conversation'], "bot-mssg", text_response)
            return text_response

    def checkMoodInfo(self, params):
        moods = self.instance.dbManager.get_witness_moods(self.instance.session['conversation'])
        flag = 0
        word = re.compile('mood_') 

        for param in params:
            if params.get(param) and word.search(param) and "." not in param:
                m = param.split("_")[1]
                moods[m] += 1
                moods['counter'] += 1
                flag = 1
        return moods,flag
    
    def checkEmergencyChange(self, intent):
        if self.instance.session['curr_emergency']['type'] != intent or self.instance.session['curr_emergency']['type'] == "Normal":
            values = [e['type'] for e in self.instance.session['emergencies']]
            expr = re.compile("|".join(values))
            if expr.search(intent):
                self.instance.session['curr_emergency'] = next(x for x in self.instance.session['emergencies'] if x["type"] == intent )
                self.instance.dbManager.update_current_emergency(
                    self.instance.session['conversation'], 
                    self.instance.session['curr_emergency']['id']
                )
            else:
                # Only creating new Emergency if in the allowed types list
                em = re.compile("|".join(emergency_types))
                if em.search(intent):
                    self.instance.session['curr_emergency'] = None
                    self.instance.session['curr_emergency'] = self.instance.dbManager.insert_emergency(defaultEmergency(etype=intent))
                    self.instance.session['emergencies'].append(self.instance.session['curr_emergency'])
                    self.instance.dbManager.add_emergency(
                        self.instance.session['conversation'], 
                        self.instance.session['curr_emergency']['id']
                    )
                    self.instance.dbManager.update_current_emergency(
                        self.instance.session['conversation'], 
                        self.instance.session['curr_emergency']['id']
                    )
        
    def handle_intent(self, text, info):
        switcher = {
            "ProtocolAgressionWithVictim":self.agressionWithVictim,
            "ProtocolAgressionWithoutVictim":self.agressionWithoutVictim,
            "ProtocolAgressionIdentification (Without Context)":self.agressionIdentificationWithout,
            "ProtocolAgressionIdentification (With Context)":self.agressionIdentificationWith,
            "ProtocolMurder":self.murder,
            "Default Welcome Intent":self.welcome,
            "ProtocolBleedingBase":self.bleedingBase,
            "ProtocolCriticalHealth":self.criticalHealth,
            "ProtocolFaintingBase":self.faintingBase,
            "ProtocolWoundBase":self.woundBase,
            "ProtocolCovid19":self.coronavirus,
            "FrasesMood":self.moodSentences,
            "GetPreferences":self.getPreferences,
            "GetNoPreferences":self.getNoPreferences,
            "GetNombre":self.getNombre,
            "ProtocolSuicideAttempt":self.suicideAttempt,
            "ProtocolVictimIdentification":self.victimIdentification,
            "DangerSuicide":self.dangerSuicide,
            "DangerOthers":self.dangerOthers
        }
        func = switcher.get(info['intent'], "Invalid intent" )
        response = info['text']
        if func != "Invalid intent":
            self.checkEmergencyChange(info['intent'])
            print("Intent: ", info['intent'])
            response = func(text, info['params'], info['text'])
        self.instance.contexts = list(self.instance.dfManager.get_contexts())
        return response
    
    # Intent Handling functions

    def agressionWithVictim(self, user_input, params, result):
        #Checking for number of victims
        num = 0
        if not self.instance.session['curr_emergency']['quantity_found']:
            numPersons = checkPersonsQuantity(params)
            numPersons2 = checkPersonsQuantity2(params)
            if numPersons:
                num = numPersons[0]
                self.instance.session['curr_emergency']['quantity_found'] = True
                self.instance.dbManager.update_emergency_num_victims(
                    self.instance.session['curr_emergency']['id'],
                    num
                )
            if numPersons2:
                num = numPersons2[0]
                self.instance.session['curr_emergency']['quantity_found'] = True
                self.instance.dbManager.update_emergency_num_aggressors(
                    self.instance.session['curr_emergency']['id'],
                    num
            )    
        #Checking for victim name/identification
        names = checkPersonName(params) 
        names2 = checkPersonName2(params) 
        if names:
            db_victims = self.instance.dbManager.get_victims(                    
                    self.instance.session['curr_emergency']['id']
                )
            persons = []
            for name in names:
                if name not in db_victims and name != "una persona":
                    persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Victim.value)))
            self.instance.dbManager.update_emergency_persons(
                self.instance.session['curr_emergency']['id'],
                persons
            )
            self.instance.dbManager.update_emergency_num_victims(
                self.instance.session['curr_emergency']['id'],
                len(persons)
            )
        if names2:
            db_agg = self.instance.dbManager.get_aggressors(                    
                    self.instance.session['curr_emergency']['id']
                )
            persons = []
            for name in names2:
                if name not in db_agg and name != "una persona":
                    persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Aggressor.value)))
            self.instance.dbManager.update_emergency_persons(
                self.instance.session['curr_emergency']['id'],
                persons
            ) 
            self.instance.dbManager.update_emergency_num_aggressors(
                self.instance.session['curr_emergency']['id'],
                len(persons)
            )
        #Checking for aggressions type
        aggressions = checkAggressionType(params)
        if aggressions:
            self.instance.dbManager.update_person_aggressions(
                    self.instance.session['curr_emergency']['id'],
                    Roles.Victim.value,
                    aggressions
                    )  
        self.restoreProtocolContext()
        return result

    def agressionWithoutVictim(self, user_input, params, result):
        #Updating witness role as Victim
        self.instance.dbManager.update_witness_role(
            self.instance.session['conversation'],
            Roles.Victim.value
        )
        #Checking for number of aggressors
        if not self.instance.session['curr_emergency']['quantity_found']:
            numPersons = checkPersonsQuantity(params)
            if numPersons:
                num = numPersons[0]
                self.instance.session['curr_emergency']['quantity_found'] = True
                self.instance.dbManager.update_emergency_num_aggressors(
                    self.instance.session['curr_emergency']['id'],
                    num
                )
        #Checking for aggressors name/identification
        names = checkPersonName(params) 
        if names:
            print("Names: ", names)
            persons = []
            for name in names:
                persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Aggressor.value)))
            self.instance.dbManager.update_emergency_persons(
                self.instance.session['curr_emergency']['id'],
                persons
            )
            self.instance.dbManager.update_emergency_num_aggressors(
                self.instance.session['curr_emergency']['id'],
                len(persons)
            )
        #Checking for emergency location
        locations = checkEmergencyLocationNoNumber(params)
        if locations:
            try:
                loclist = list(locations[0].items())
            except:
                loclist = locations[0]
            for loc in loclist:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                    )
        #Checking for aggressions type
        aggressions = checkAggressionType(params)
        if aggressions:
            self.instance.dbManager.update_witness_aggressions(
                    self.instance.session['conversation'],
                    aggressions
                    )
        self.restoreProtocolContext()
        return result

    def agressionIdentificationWithout(self, user_input, params, result):
        #Checking for victim name/identification
        names = checkPersonName(params) 
        if names:
            db_agg = self.instance.dbManager.get_aggressors(                    
                    self.instance.session['curr_emergency']['id']
                )
            persons = []
            for name in names:
                if name not in db_agg and name != "una persona":
                    persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Aggressor.value)))
            self.instance.dbManager.update_emergency_persons(
                self.instance.session['curr_emergency']['id'],
                persons
            )
        #Checking for emergency location
        locations = checkEmergencyLocationNoNumber(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                )
        #Checking for aggressors description
        descriptions = checkPersonDescription(params)
        if descriptions:
            self.instance.dbManager.update_person_description(
                self.instance.session['curr_emergency']['id'],
                Roles.Aggressor.value,
                descriptions
            )
        return result
    
    def agressionIdentificationWith(self, user_input, params, result):
        #Checking for victim name/identification
        names = checkPersonName(params) 
        if names:
            db_agg = self.instance.dbManager.get_aggressors(                    
                    self.instance.session['curr_emergency']['id']
                )
            persons = []
            for name in names:
                if name not in db_agg and name != "Una persona":
                    persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Aggressor.value)))
            self.instance.dbManager.update_emergency_persons(
                self.instance.session['curr_emergency']['id'],
                persons
            )
            self.instance.dbManager.update_emergency_num_aggressors(
                self.instance.session['curr_emergency']['id'],
                len(persons)
            )
        #Checking for emergency location
        locations = checkEmergencyLocationNoNumber(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                )
        #Checking for emergency location
        descriptions = checkPersonDescription(params)
        if descriptions:
            self.instance.dbManager.update_person_description(
                self.instance.session['curr_emergency']['id'],
                Roles.Aggressor.value,
                descriptions
            )
        return result

    def coronavirus(self, user_input, params, result):
        #Updating witness role as Victim
        self.instance.dbManager.update_witness_role(
            self.instance.session['conversation'],
            Roles.Victim.value
        )
        #Checking for emergency location
        locations = checkEmergencyLocation(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                )
        #Checking for healthProblem
        health = checkHealthProblem(params)
        if health:
            self.instance.dbManager.update_witness_diseases(
                self.instance.session['conversation'],
                health
            ) 
        self.restoreProtocolContext()
        return result

    def murder(self, user_input, params, result):
        #Checking for victim name/identification
        names = checkPersonName(params) 
        names2 = checkPersonName2(params) 
        if names:
            db_victims = self.instance.dbManager.get_victims(                    
                    self.instance.session['curr_emergency']['id']
                )
            persons = []
            for name in names:
                if name not in db_victims and name != "una persona":
                    persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Victim.value)))
            self.instance.dbManager.update_emergency_persons(
                self.instance.session['curr_emergency']['id'],
                persons
            )
            self.instance.dbManager.update_emergency_num_victims(
                self.instance.session['curr_emergency']['id'],
                len(persons)
            )
        if names2:
            db_agg = self.instance.dbManager.get_aggressors(                    
                    self.instance.session['curr_emergency']['id']
                )
            persons = []
            for name in names2:
                if name not in db_agg and name != "una persona":
                    persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Aggressor.value)))
            self.instance.dbManager.update_emergency_persons(
                self.instance.session['curr_emergency']['id'],
                persons
            )
            self.instance.dbManager.update_emergency_num_aggressors(
                self.instance.session['curr_emergency']['id'],
                len(persons)
            ) 
        #Checking for emergency location
        locations = checkEmergencyLocationNoNumber(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                    )
        self.restoreProtocolContext()
        return result
    
    def welcome(self, user_input, params, result):
        #Checking for transmitter name
        name = checkPersonName(params)
        if name:
            self.instance.dbManager.update_witness_name(
                self.instance.session['conversation'],
                name[0]
                )
        return result

    def bleedingBase(self, user_input, params, result):
        is_witness = checkIfWitnessProblem(user_input)
        if not is_witness:
            #Checking for number of victims
            if not self.instance.session['curr_emergency']['quantity_found']:
                numPersons = checkPersonsQuantity(params)
                if numPersons:
                    num = numPersons[0]
                    self.instance.session['curr_emergency']['quantity_found'] = True
                    self.instance.dbManager.update_emergency_num_victims(
                        self.instance.session['curr_emergency']['id'],
                        num
                    )
        #Checking for victims name/identification
        names = checkPersonName(params) 
        if names:
            if is_witness:
                self.instance.dbManager.update_witness_name(
                    self.instance.session['conversation'],
                    names[0]
                )
            else:
                db_victims = self.instance.dbManager.get_victims(                    
                    self.instance.session['curr_emergency']['id']
                )
                persons = []
                for name in names:
                    if name not in db_victims:
                        persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Victim.value)))
                self.instance.dbManager.update_emergency_persons(
                    self.instance.session['curr_emergency']['id'],
                    persons
                )
                self.instance.dbManager.update_emergency_num_victims(
                    self.instance.session['curr_emergency']['id'],
                    len(persons)
                )
        #Checking for emergency location
        locations = checkEmergencyLocationNoNumber(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                    )
        #Checking for healthProblem
        health = checkHealthProblem(params)
        if health:
            if is_witness:
                self.instance.dbManager.update_witness_injuries(
                    self.instance.session['conversation'],
                    health
                )
            else:
                self.instance.dbManager.update_person_injuries(
                    self.instance.session['curr_emergency']['id'],
                    Roles.Victim.value,
                    health
                )
        self.restoreHealthContext()
        return result
    
    def criticalHealth(self, user_input, params, result):
        is_witness = checkIfWitnessProblem(user_input)
        if is_witness:
                #Updating witness role as Victim
                self.instance.dbManager.update_witness_role(
                    self.instance.session['conversation'],
                    Roles.Victim.value
                )
        #Checking for healthProblem
        health = checkHealthProblem(params)
        if health:
            if is_witness:
                self.instance.dbManager.update_witness_injuries(
                    self.instance.session['conversation'],
                    health
                )
            else:
                self.instance.dbManager.update_person_injuries(
                    self.instance.session['curr_emergency']['id'],
                    Roles.Victim.value,
                    health
                ) 
        return result
    
    def faintingBase(self, user_input, params, result):
        is_witness = checkIfWitnessProblem(user_input)
        if is_witness:
            #Updating witness role as Victim
            self.instance.dbManager.update_witness_role(
                self.instance.session['conversation'],
                Roles.Victim.value
            )
        #Checking for victims name/identification
        names = checkPersonName(params) 
        if names:
            if is_witness:
                self.instance.dbManager.update_witness_name(
                    self.instance.session['conversation'],
                    names[0]
                )
            else:
                db_victims = self.instance.dbManager.get_victims(                    
                    self.instance.session['curr_emergency']['id']
                )
                persons = []
                for name in names:
                    if name not in db_victims:
                        persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Victim.value)))
                self.instance.dbManager.update_emergency_persons(
                    self.instance.session['curr_emergency']['id'],
                    persons
                )
                self.instance.dbManager.update_emergency_num_victims(
                    self.instance.session['curr_emergency']['id'],
                    len(persons)
                )
        #Checking for emergency location
        locations = checkEmergencyLocationNoNumber(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                    )
        #Checking for healthProblem
        health = checkHealthProblem(params)
        if health:
            if is_witness:
                self.instance.dbManager.update_witness_injuries(
                    self.instance.session['conversation'],
                    health
                )
            else:
                self.instance.dbManager.update_person_injuries(
                    self.instance.session['curr_emergency']['id'],
                    Roles.Victim.value,
                    health
                ) 
        self.restoreHealthContext()
        return result
    
    def woundBase(self, user_input, params, result):
        is_witness = checkIfWitnessProblem(user_input)
        if is_witness:
            #Updating witness role as Victim
            self.instance.dbManager.update_witness_role(
                self.instance.session['conversation'],
                Roles.Victim.value
            )
        #Checking for victims names/identification
        names = checkPersonName(params) 
        if is_witness:
            self.instance.dbManager.update_witness_name(
                self.instance.session['conversation'],
                names[0]
            )
        else:
            if names:
                db_victims = self.instance.dbManager.get_victims(                    
                    self.instance.session['curr_emergency']['id']
                )
                persons = []
                for name in names:
                    if name == "yo":
                        self.instance.dbManager.update_witness_name(
                            self.instance.session['conversation'],
                            names[0]
                        )
                        break
                    else:
                        if name not in db_victims:
                            persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Victim.value)))
                    self.instance.dbManager.update_emergency_persons(
                        self.instance.session['curr_emergency']['id'],
                        persons
                    )
                    self.instance.dbManager.update_emergency_num_victims(
                        self.instance.session['curr_emergency']['id'],
                        len(persons)
                    )
        #Checking for emergency location
        locations = checkEmergencyLocation(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                    )
        #Checking for healthProblem
        health = checkHealthProblem(params)
        if health:
            if is_witness:
                self.instance.dbManager.update_witness_injuries(
                    self.instance.session['conversation'],
                    health
                )
            else:
                self.instance.dbManager.update_person_injuries(
                    self.instance.session['curr_emergency']['id'],
                    Roles.Victim.value,
                    health
                )         
        self.restoreHealthContext()
        return result

    def moodSentences(self, user_input, params, result):
        is_witness = checkIfWitnessProblem(user_input)      
        #Checking for victim's name
        names = checkPersonName(params) 
        if names:
            if is_witness:
                self.instance.dbManager.update_witness_name(
                    self.instance.session['conversation'],
                    names[0]
                )
            else: 
                db_victims = self.instance.dbManager.get_victims(                    
                    self.instance.session['curr_emergency']['id']
                )
                persons = []
                for name in names:
                    if name not in db_victims:
                        persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Victim.value)))
                self.instance.dbManager.update_emergency_persons(
                    self.instance.session['curr_emergency']['id'],
                    persons
                )
        #Checking for emergency location
        locations = checkEmergencyLocation(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                )
        
        result = self.handle_multiple_contexts(result)
        return result
    
    def getPreferences(self, user_input, params, result):
        prefs = checkPersonPreferences(params)
        if (prefs):
            self.instance.dbManager.update_witness_preferences(
                self.instance.session['conversation'],
                prefs
                )
        result = self.handle_multiple_contexts(result)
        return result
    
    def getNoPreferences(self, user_input, params, result):
        prefs = checkPersonPreferences(params)
        if (prefs):
            self.instance.dbManager.update_witness_dislikes(
                self.instance.session['conversation'],
                prefs
                )
        result = self.handle_multiple_contexts(result)
        return result
   
    def getNombre(self, user_input, params, result):
        #Checking for transmitter name
        name = checkPersonName(params)
        if name:
            self.instance.dbManager.update_witness_name(
                self.instance.session['conversation'],
                name[0]
                )
        is_witness = checkIfWitnessProblem(user_input)      
        #Checking for emergency location
        locations = checkEmergencyLocation(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                )
        
        result = self.handle_multiple_contexts(result)
        return result

    def victimIdentification(self, user_input, params, result):  
        #Checking for victim's name
        names = checkPersonName(params) 
        if names:
            db_victims = self.instance.dbManager.get_victims(                    
                self.instance.session['curr_emergency']['id']
            )
            persons = []
            for name in names:
                if name not in db_victims:
                    persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Victim.value)))
            self.instance.dbManager.update_emergency_persons(
                self.instance.session['curr_emergency']['id'],
                persons
            )
        #Checking for victim description
        descriptions = checkPersonDescription(params)
        if descriptions:
            self.instance.dbManager.update_person_description(
                self.instance.session['curr_emergency']['id'],
                Roles.Victim.value,
                descriptions
            ) 
        return result

    def suicideAttempt(self, user_input, params, result):
        #Checking for victims name/identification
        names = checkPersonName(params) 
        if names:
            if is_witness:
                self.instance.dbManager.update_witness_name(
                    self.instance.session['conversation'],
                    names[0]
                )
            else:
                db_victims = self.instance.dbManager.get_victims(                    
                    self.instance.session['curr_emergency']['id']
                )
                persons = []
                for name in names:
                    persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Victim.value)))
                self.instance.dbManager.update_emergency_persons(
                    self.instance.session['curr_emergency']['id'],
                    persons
                )
        #Checking for emergency location
        locations = checkEmergencyLocationNoNumber(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                )
        return result

    def dangerSuicide(self, user_input, params, result):
        #Checking for emergency location
        locations = checkEmergencyLocation(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                )
        return result

    def dangerOthers(self, user_input, params, result):
        is_witness = checkIfWitnessProblem(user_input)      
        #Checking for victim's name
        names = checkPersonName(params) 
        if names:
            if is_witness:
                self.instance.dbManager.update_witness_name(
                    self.instance.session['conversation'],
                    names[0]
                )
            else: 
                db_victims = self.instance.dbManager.get_victims(                    
                    self.instance.session['curr_emergency']['id']
                )
                persons = []
                for name in names:
                    if name not in db_victims:
                        persons.append(self.instance.dbManager.insert_person(defaultPerson(name=name, role=Roles.Victim.value)))
                self.instance.dbManager.update_emergency_persons(
                    self.instance.session['curr_emergency']['id'],
                    persons
                )
        #Checking for emergency location
        locations = checkEmergencyLocation(params)
        if locations:
            for loc in locations:
                self.instance.dbManager.add_location(
                    self.instance.session['curr_emergency']['id'],
                    loc
                )
        return result 

    # Protocol Contexts functions

    def handle_multiple_contexts(self, result):
        words = [re.compile('healthCompleted') ,
                re.compile('protocolCompleted'),
                re.compile('followup'),
                re.compile('dialog_context')]
        flags = [0,0,0,0]
        for c in self.instance.contexts:
            for i in range(len(words)):
                if words[i].search(c.name):
                    flags[i] = 1
        self.instance.dfManager.set_contexts(self.instance.contexts)

        if flags[3] == 1 or flags[2] == 1 or (flags[0] == 1 and flags[1] == 0) or (flags[0] == 0 and flags[1] == 1):
            return result + ". Pero ahora centremonos en la pregunta anterior, por favor."
        return result
    
    def restoreProtocolContext(self):
        wordProtocol = re.compile('protocolCompleted')
        wordHealth = re.compile('healthCompleted')
        flagProtocol = 0
        flagHealth = None

        for context in self.instance.contexts:
            if wordProtocol.search(context.name):
                self.instance.dfManager.delete_context(context)
                flagProtocol = 1
            if wordHealth.search(context.name):
                flagHealth = context
        
        if flagProtocol == 1 and flagHealth != None:
            self.instance.dfManager.delete_context(flagHealth)
                
    def restoreHealthContext(self):
        wordProtocol = re.compile('protocolCompleted')
        wordHealth = re.compile('healthCompleted')
        flagProtocol = None
        flagHealth = 0

        for context in self.instance.contexts:
            if wordProtocol.search(context.name):
                flagProtocol = context
            if wordHealth.search(context.name):
                self.instance.dfManager.delete_context(context)
                flagHealth = 1
        
        if flagProtocol != None and flagHealth == 1:
            self.instance.dfManager.delete_context(flagProtocol)

    
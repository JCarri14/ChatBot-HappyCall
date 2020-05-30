import dialogflow_v2 as dialogflow
import re


class DialogflowManager:

    def __init__(self, project_id, session_id, language_code):

        self.project_id = project_id
        self.session_id = session_id

        self.intents_client = dialogflow.IntentsClient()
        self.parent = self.intents_client.project_agent_path(project_id)
        self.intents = self.intents_client.list_intents(self.parent) 
        
        self.contexts_client = dialogflow.ContextsClient()
        self.context_parent = self.contexts_client.session_path(project_id, session_id)
        
        self.session_client = dialogflow.SessionsClient()
        self.session = self.session_client.session_path(project_id, session_id)
        self.lang_code = "es"
    
    def get_intents(self):
        return self.intents
    
    def get_contexts(self):
        return self.contexts_client.list_contexts(self.context_parent)
    
    def set_contexts(self, contexts):
        self.contexts_client.delete_all_contexts(self.context_parent)
        for c in contexts:
            self.contexts_client.create_context(self.context_parent, c)

    def delete_context(self, context):
        self.contexts_client.delete_context(self.context_parent, context)

    def request_fulfillment_text(self, text):
        res = ""
        if text:
            text_input = dialogflow.types.TextInput(text=text, language_code=self.lang_code)
            query_input = dialogflow.types.QueryInput(text=text_input)
            try:
                response = self.session_client.detect_intent(session=self.session, query_input=query_input)
                res = self.handleResponse(response)
            except Exception:
                raise

        return res
    
    def handleResponse(self, response):
        res = {}
        res['text'] = response.query_result.fulfillment_text
        res['intent'] = response.query_result.intent.display_name
        res['params'] = {}
        word = re.compile('contexts/__system_counters__') 
        
        for context in response.query_result.output_contexts:
            if word.search(context.name):
                for param in context.parameters:
                    res['params'][param] = param
                break
        
        word = re.compile('mood_') 
        
        for param in response.query_result.parameters:
            if word.search(param.lower()):
                res['params'][param.lower()] = response.query_result.parameters[param]
        return res



    


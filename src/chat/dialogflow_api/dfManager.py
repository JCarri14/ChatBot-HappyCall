import dialogflow as dialogflow


class DialogflowManager:

    def __init__(self, project_id, session_id, language_code):
        self.intents_client = dialogflow.IntentsClient()
        self.parent = self.intents_client.project_agent_path(project_id)
        self.intents = self.intents_client.list_intents(self.parent) 

        self.session_client = dialogflow.SessionsClient()
        self.session = self.session_client.session_path(project_id, session_id)
        self.lang_code = "es"
    
    def get_intents(self):
        return self.intents

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
        res['params'] = response.query_result.parameters
        for context in response.query_result.output_contexts:
            if "contexts/__system_counters__" in context.name:
                res['params'] = response.query_result.output_contexts
        return res



    


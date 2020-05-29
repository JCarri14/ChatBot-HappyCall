def checkPersonAttributes(user_input, params):
    words = sentence_to_tokens(user_input)
    print(words)
    if params:
        for param in params:
            if param.key == "Person":
                self.handlePersonValues(param.values)

def handlePersonValues(values):
    print(values)

def checkOwnershipName(user_input):
    if "mi nombre es" in user_input:
        return True
    if "me llamo" in user_input:
        return True
    if "soy" in user_input:
        return True
    return False

def checkOwnershipValues(user_input):
    if "uno de los" in user_input:
        return False
    if "una de las" in user_input:
        return False
    if "un grupo de" in user_input:
        return False
    return True

def checkPersonName(params):
    for param in params:
        if param == "person.original":
            return params[param][0]
    return "Person"

def checkPersonsQuantity(params):
    for param in params:
        if param == "number":
            return params[param][0]
    return 1
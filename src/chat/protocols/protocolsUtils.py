from chat.models import *

#params.get(param) != None

def checkPersonName(params):
    for param in params:
        if param == "person.original":
            if isinstance(params[param], list):
                if len(params[param]) > 0:
                    return params[param][0]
            elif params.get(param):
                return params[param]
    return "Person"

def checkPersonsQuantity(params):
    for param in params:
        if param == "number":
            if isinstance(params[param], list):
                if len(params[param]) > 0:
                    return params[param][0]
            elif params.get(param):
                return params[param]
    return 1

def defaultPerson():
    disorders = {}
    for m in (Moods):
        disorders[m.value] = 0
    healthContext = HealthContext(disorders=disorders)

    coefficients = {}
    for c in (Coefficients):
        coefficients[c.value] = 0.0
    return Person(role=Roles.Transmitter,
            healthContext = healthContext,
            sentimentCoefficients = coefficients)
    

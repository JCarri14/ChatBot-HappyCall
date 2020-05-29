from chat.models import *

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
    

from chat.models import *
import re

#params.get(param)

def checkEmergencyLocation(params):
    return checkParameters(["number", "address.original", "location.original", "Location.original", "EmergencyLocation.original", "emergencylocation.original"], params)

def checkEmergencyLocationNoNumber(params):
    return checkParameters(["address.original", "EmergencyLocation.original", "emergencylocation.original"], params)

def checkAggressionType(params):
    return checkParameters(["AggressionType.original"], params)

def checkAggresionInstrument(params):
    return checkParameters(["AggressionInstrument.original"], params)

def checkHealthProblem(params):
    return checkParameters(["HealthProblem.original"], params)

def checkUndefinedPerson(params):
    return checkParameters(["UndefinedPerson.original, undefinedperson.original"], params)

def checkPersonPreferences(params):
    return checkParameters(["UserPreference.original", "userpreference.original"], params)

def checkPersonDescription(params):
    return checkParameters(["persondescription.original", "personDescription.original", "PersonDescription.original"], params)

def checkUndefinedPersonName(params):
    return checkParameters(["person.original"], params)

def checkPersonName(params):
    return checkParameters(["person.original"], params)

def checkPersonsQuantity(params):
    return checkParameters(["number", "Number"], params)

#Append: add list as value in the other one
#Extend: add values to the corresponding list
def checkParameters(search, params):
    result = []
    for param in params:
        if param in search:
            if isinstance(params[param], list):
                if len(params[param]) > 0:
                    result.extend(params[param])
            elif params.get(param):
                result.append(params[param])
    return result

def checkIfWitnessProblem(user_input):
    values = ["Me estoy", "Estoy perdiendo", "Tengo un", "Tengo una", "Estoy sangrando"
                "Llevo una hora sangrando", "Estoy sufriendo", "Me está", "Me han metido"]
    expr = re.compile("|".join(values))
    if expr.search(user_input):
        return True
    return False

def defaultPerson(name="Person", role=Roles.Transmitter.value):
    disorders = {}
    for m in (Moods):
        disorders[m.value] = 0
    healthContext = HealthContext(disorders=disorders)

    coefficients = {}
    for c in (Coefficients):
        coefficients[c.value] = 0.0
    return Person(role=role, name = name, healthContext = healthContext,
                sentimentCoefficients = coefficients)
    
def defaultEmergency():
    return Emergency(etype=EmergencyTypes.Normal, 
                    num_involved=1, is_active=True)
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

def checkPersonPreferences(params):
    return checkParameters(["UserPreference.original", "userpreference.original"], params)

def checkPersonDescription(params):
    return checkParameters(["persondescription.original", "personDescription.original", "PersonDescription.original"], params)

def checkPersonName(params):
    return checkParameters(["UndefinedPerson", "undefinedperson", "person.original", "Person.original"], params)

def checkPersonName2(params):
    return checkParameters(["UndefinedPerson1", "undefinedperson1", "person.original", "Person.original"], params)

def checkPersonsQuantity(params):
    return checkParameters(["UndefinedPerson", "undefinedperson", "number", "Number"], params)

def checkPersonsQuantity2(params):
    return checkParameters(["UndefinedPerson1", "undefinedperson1", "number", "Number"], params)

# -------------------------------------------------------------- #

def loopDictParameters(result, search, params):
    expr = re.compile("|".join(search[2:]))

    for items in params:
        for key, value in items.items():
            if expr.match(key):
                if isinstance(value, list):
                    if len(value) > 0:
                        result.append(value)
                elif value:
                    result.append(value)
    return result

#Append: add list as value in the other one
#Extend: add values to the corresponding list
def checkParameters(search, params):
    result = []
    #expr = re.compile("|".join(search))
    for param in params:
        if param in search:
            if param == "UndefinedPerson":
                if not isinstance(params[param][0],str):
                    result = loopDictParameters(result, search, params[param])
                else:
                    if "number" in search:
                        result.append(1)
                    else:   
                        result.append(params[param][0])
            else:
                try: p = list(params[param].items())
                except: p = params[param]
                if isinstance(p, list):
                    result.append(p)
                elif params.get(param):
                    result.append(p)
    return result

def checkIfWitnessProblem(user_input):
    values = ["Me estoy", "Estoy perdiendo", "Tengo un", "Tengo una", "He sufrido", "Estoy sangrando"
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
    return Person(role=role, name=name, healthContext=healthContext,
                sentimentCoefficients = coefficients)
    
def defaultEmergency(etype=EmergencyTypes.Normal.value):
    return Emergency(etype=etype, num_aggressors=0, 
                    num_victims=0, is_active=True)
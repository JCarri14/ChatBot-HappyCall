from chat.ddbb.MongoODMManager import MongoODMManager
from chat.models import Moods, Coefficients

conditionalProbs = {
    "ansiety": {
        "loneliness": 0.65,
        "happiness": 0.05,
        "monetaryproblems": 0.5,
        "aggressiveness": 0.5,
        "confused": 0.35,
        "fear": 0.7,
        "sadness":  0.6,
        "stress": 0.95
    },
    "depression": {
        "loneliness": 0.6,
        "happiness": 0.01,
        "monetaryproblems": 0.75,
        "aggressiveness": 0.35,
        "confused": 0.15,
        "fear": 0.35,
        "sadness":  0.95,
        "stress": 0.1
    },
    "esquizofrenia": {
        "loneliness": 0.1,
        "happiness": 0.05,
        "monetaryproblems": 0.1,
        "aggressiveness": 0.85,
        "confused": 0.75,
        "fear": 0.6,
        "sadness":  0.5,
        "stress": 0.6
    },
    "panico": {
        "loneliness": 0.55,
        "happiness": 0.01,
        "monetaryproblems": 0.25,
        "aggressiveness": 0.3,
        "confused": 0.75,
        "fear": 0.9,
        "sadness":  0.5,
        "stress": 0.85
    }
}

certaintyFactors = {
    "ansiety": {
        "loneliness": 0.65,
        "happiness": -0.85,
        "monetaryproblems": 0.5,
        "aggressiveness": 0.3,
        "confused": -0.35,
        "fear": 0.7,
        "sadness":  0.6,
        "stress": 0.95
    },
    "depression": {
        "loneliness": 0.6,
        "happiness": -0.95,
        "monetaryproblems": 0.75,
        "aggressiveness": -0.3,
        "confused": -0.4,
        "fear": 0.3,
        "sadness":  0.95,
        "stress": 0.5
    },
    "esquizofrenia": {
        "loneliness": -0.7,
        "happiness": -0.85,
        "monetaryproblems": -0.8,
        "aggressiveness": 0.9,
        "confused": 0.75,
        "fear": 0.6,
        "sadness":  0.5,
        "stress": 0.6
    },
    "panico": {
        "loneliness": 0.6,
        "happiness": -0.95,
        "monetaryproblems": -0.2,
        "aggressiveness": -0.3,
        "confused": 0.75,
        "fear": 0.95,
        "sadness":  0.5,
        "stress": 0.75
    }
}

def calcularCertaintyFactor(listKeys, probs, sentiment):
    actualCoefficient = probs[listKeys[0]] * certaintyFactors[sentiment][listKeys[0]]
        
    for j in range(1, len(listKeys)):
        probabilityX = actualCoefficient
        probabilityY = probs[listKeys[j]] * certaintyFactors[sentiment][listKeys[j]]
        
        if probabilityX > 0 and probabilityY > 0:
            actualCoefficient = probabilityX + probabilityY * (1 - probabilityX)
        
        elif probabilityX < 0 and probabilityY < 0:
            actualCoefficient = probabilityX + probabilityY * (1 + probabilityX)
        
        else:
            actualCoefficient = (probabilityX + probabilityY) / (1 - min([abs(probabilityX), abs(probabilityY)]))
    return actualCoefficient

def calcularConditionalProbability(listKeys, probs, sentiment):
    actualProbability = 0
    sumProbabilities = 0

    print(listKeys)
    for i in range(len(listKeys)):
        sumProbabilities = sumProbabilities + (probs[listKeys[i]] * conditionalProbs[sentiment][listKeys[i]])
    
    for i in range(len(listKeys)):
        actualProbability = actualProbability + (probs[listKeys[i]] * conditionalProbs[sentiment][listKeys[i]] * conditionalProbs[sentiment][listKeys[i]]) / sumProbabilities

    return actualProbability

def calculateSentiment(dbManager, conversation_name, moods, person):
    print(moods)
    coefficients = dbManager.get_person_coefficients(conversation_name)
    probs = {i: moods[i]/moods["counter"] for i in moods if i != "counter"}
    
    for sentiment in coefficients:
        listKeys = list(certaintyFactors[sentiment].keys())
        print("------------", sentiment, "------------")
        print("BAYESSIAN PROBABILITY: ", calcularConditionalProbability(listKeys, probs, sentiment))
        coefficients[sentiment] = calcularCertaintyFactor(listKeys, probs, sentiment)
        print("CERTAINTY FACTOR: ", coefficients[sentiment])

    dbManager.update_person_coefficients(conversation_name, coefficients)
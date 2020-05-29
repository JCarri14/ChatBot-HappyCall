from chat.ddbb.MongoODMManager import MongoODMManager
from chat.models import Moods, Coefficients

conditionalProbs = {
    "Ansiety": {
        "Loneliness": 0.65,
        "Happyness": 0.05,
        "MonetaryProblems": 0.5,
        "Agressiveness": 0.5,
        "Confused": 0.35,
        "Sadness":  0.6,
        "Stressed": 0.95
    },
    "Depression": {
        "Loneliness": 0.6,
        "Happyness": 0.01,
        "MonetaryProblems": 0.75,
        "Agressiveness": 0.35,
        "Confused": 0.15,
        "Sadness":  0.95,
        "Stressed": 0.1
    },
    "Esquizofrenia": {
        "Loneliness": 0.1,
        "Happyness": 0.05,
        "MonetaryProblems": 0.1,
        "Agressiveness": 0.85,
        "Confused": 0.75,
        "Sadness":  0.5,
        "Stressed": 0.6
    },
    "Panico": {
        "Loneliness": 0.55,
        "Happyness": 0.01,
        "MonetaryProblems": 0.25,
        "Agressiveness": 0.3,
        "Confused": 0.75,
        "Sadness":  0.5,
        "Stressed": 0.85
    }
}

certaintyFactors = {
    "Ansiety": {
        "Loneliness": 0.65,
        "Happyness": -0.85,
        "MonetaryProblems": 0.5,
        "Agressiveness": 0.3,
        "Confused": -0.35,
        "Sadness":  0.6,
        "Stressed": 0.95
    },
    "Depression": {
        "Loneliness": 0.6,
        "Happyness": -0.95,
        "MonetaryProblems": 0.75,
        "Agressiveness": -0.3,
        "Confused": -0.4,
        "Sadness":  0.95,
        "Stressed": 0.5
    },
    "Esquizofrenia": {
        "Loneliness": -0.7,
        "Happyness": -0.85,
        "MonetaryProblems": -0.8,
        "Agressiveness": 0.9,
        "Confused": 0.75,
        "Sadness":  0.5,
        "Stressed": 0.6
    },
    "Panico": {
        "Loneliness": 0.6,
        "Happyness": -0.95,
        "MonetaryProblems": -0.2,
        "Agressiveness": -0.3,
        "Confused": 0.85,
        "Sadness":  0.5,
        "Stressed": 0.85
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
                actualCoefficient = (probabilityX + probabilityY) / (1 - min([abs(probabilityX), abs(probabilityY)])
    
    return actualCoefficient

def calcularConditionalProbability(listKeys, probs, sentiment):
    actualProbability = 0
    sumProbabilities = 0

    for i in range(len(listKeys)):
        sumProbabilities = sumProbabilities + (probs[listKeys[i]] * conditionalProbs[sentiment][listKeys[i]])
    
    for i in range(len(listKeys)):
        actualProbability = actualProbability + (probs[listKeys[i]] * conditionalProbs[sentiment][listKeys[i]] * conditionalProbs[sentiment][listKeys[i]]) / sumProbabilities

    return actualProbability

def calculateSentiment(dbManager, moods, person):
    coefficients = dbManager.get_person_coefficients(res)
    probs = {i: moods[i]/moods["Counter"] for i in moods if i != "Counter"}
    
    for sentiment in coefficients:
        listKeys = certaintyFactors[sentiment].keys()
        print("------------", sentiment, "------------")
        print("BAYESSIAN PROBABILITY: ", calcularConditionalProbability(listKeys, probs, sentiment))
        coefficients[sentiment] = calcularCertaintyFactor(listKeys, probs, sentiment)
        print("CERTAINTY FACTOR: ", coefficients[sentiment])

    
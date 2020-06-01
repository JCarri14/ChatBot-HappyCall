from pymodm import EmbeddedMongoModel, MongoModel, fields
from pymodm.connection import connect

import datetime, enum

connect("mongodb://localhost:27017/happy_call", alias="my-app")

class EmergencyTypes(enum.Enum):
    Aggression = "Aggression"
    SuicideAttempt = "SuicideAttempt"
    Critical = "Critical"
    Fire = "Fire"
    Accident = "Accident"
    Normal = "Normal"

class HealthStatus(enum.Enum):
    Critical = "Critical"
    Bleeding = "Bleeding"
    Fainted = "Fainted"
    Wounded = "Wounded"

class Roles(enum.Enum):
    Transmitter = "Transmitter"
    Aggressor = "Aggressor"
    Victim = "Victim"

class Moods(enum.Enum):
    Loneliness = "loneliness"
    Happiness = "happiness"
    MonetaryProblems = "monetaryproblems"
    Agressiveness = "aggressiveness"
    Confused = "confused"
    Fear = "fear"
    Sadness = "sadness"
    Stress = "stress"
    Counter = "counter"

class Coefficients(enum.Enum):
    Ansiety = "ansiety"
    Depression = "depression"
    Esquizofrenia = "esquizofrenia"
    Panico = "panico"

# Create your models here.
class ChatMessage(EmbeddedMongoModel):
    sender = fields.CharField()
    text = fields.CharField()
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)

class HealthContext(EmbeddedMongoModel):
    status = fields.CharField()
    isPhysicallyHurt = fields.BooleanField(default=False)
    diseases = fields.ListField(fields.CharField())
    aggressions = fields.ListField(fields.CharField())
    injuries = fields.ListField(fields.CharField())
    disorders = fields.DictField()

class Person(MongoModel):
    name = fields.CharField()
    role = fields.CharField()
    gender = fields.CharField()    
    age = fields.IntegerField(min_value=0)
    description = fields.ListField(fields.CharField())
    preferences = fields.ListField(fields.CharField())
    dislikes = fields.ListField(fields.CharField())
    healthContext = fields.EmbeddedDocumentField(HealthContext)
    sentimentCoefficients = fields.DictField()

class Emergency(MongoModel):
    etype = fields.CharField()
    location = fields.ListField(fields.CharField())
    num_involved = fields.IntegerField(min_value=0)
    pers_involved = fields.ListField(fields.ReferenceField(Person))
    is_active = fields.BooleanField(default=True)

class Conversation(MongoModel):
    name = fields.CharField()
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)
    finished_at = fields.DateTimeField()
    messages = fields.EmbeddedDocumentListField(ChatMessage)
    witness = fields.ReferenceField(Person)
    emergencies = fields.ListField(fields.ReferenceField(Emergency))

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
    Loneliness = "Loneliness"
    Happyness = "Happyness"
    MonetaryProblems = "MonetaryProblems"
    Agressiveness = "Agressiveness"
    Confused = "Confused"
    Sadness = "Sadness"
    Stressed = "Stressed"

class Coefficients(enum.Enum):
    Ansiety = "Ansiety"
    Depression = "Depression"

# Create your models here.
class ChatMessage(EmbeddedMongoModel):
    sender = fields.CharField()
    text = fields.CharField()
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)

class HealthContext(EmbeddedMongoModel):
    status = fields.CharField()
    isPhysicallyHurt = fields.BooleanField(default=False)
    injuries = fields.ListField(fields.CharField())
    disorders = fields.DictField(IntegerField(min_value=0, default=0))

class Person(EmbeddedMongoModel):
    name = fields.CharField()
    role = fields.CharField()
    gender = fields.CharField()    
    age = fields.IntegerField(min_value=0)
    healthContext = fields.EmbeddedDocumentField(HealthContext)
    sentimentCoefficients = fields.DictField(FloatField(min_value=0, max_value=100, default=0))

class EmergencyContext(EmbeddedMongoModel):
    address = fields.CharField()
    place = fields.CharField()

class Emergency(MongoModel):
    etype = fields.CharField()
    context = fields.EmbeddedDocumentField(EmergencyContext)
    num_involved = fields.IntegerField(min_value=0)
    pers_involved = fields.EmbeddedDocumentListField(Person)

class Conversation(MongoModel):
    name = fields.CharField()
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)
    finished_at = fields.DateTimeField()
    messages = fields.EmbeddedDocumentListField(ChatMessage)
    emergency = fields.ReferenceField(Emergency)






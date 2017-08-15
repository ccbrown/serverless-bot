import urllib
from . import register, Base


class GetPerson(Base):
    def definition(self):
        return {
            'sampleUtterances': [
                'who is {Person}',
                'who is that',
                'who are they',
                'who is this person',
            ],
            'slots': [{
                'name': 'Person',
                'slotConstraint': 'Required',
                'slotType': 'AMAZON.Person',
                'valueElicitationPrompt': {
                    'messages': [{
                        'contentType': 'PlainText',
                        'content': 'Who?',
                    }],
                    'maxAttempts': 1,
                },
            }],
        }

    def fulfill(self, slots):
        return {
            'text': 'https://lmgtfy.com/?q=who+is+'+urllib.quote_plus(slots['Person']),
        }

register(GetPerson())

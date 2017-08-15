from . import register, Base


class GetCurrentTime(Base):
    def definition(self):
        return {
            'sampleUtterances': [
                'what time is it',
            ],
        }

    def fulfill(self, slots):
        return {
            'text': 'Adventure time!',
        }

register(GetCurrentTime())

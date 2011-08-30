from django.dispatch import Signal

api_user_created = Signal(providing_args=['instance'])
api_key_created = Signal(providing_args=['instance'])

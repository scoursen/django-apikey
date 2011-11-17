from django.dispatch import Signal

api_user_created = Signal(providing_args=['instance'])
api_key_created = Signal(providing_args=['instance'])
api_user_logged_in = Signal(providing_args=['instance'])
api_user_logged_out = Signal(providing_args=['instance'])

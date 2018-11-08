from django.dispatch import Signal

deposit_done = Signal(providing_args=["user", "amount"])

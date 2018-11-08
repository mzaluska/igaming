from django.apps import AppConfig


class PlayerConfig(AppConfig):
    name = 'player'

    def ready(self):
        import player.signals
        import player.handlers
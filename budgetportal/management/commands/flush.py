from django.core.management.commands.flush import Command as BaseFlushCommand


class Command(BaseFlushCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--allow-cascade', action='store_true', dest='allow_cascade', default=True,
                help='Adds "CASCADE" option to TRUNCATE command if supported by db backend. Default=False.',
        )

from django.core.management.base import BaseCommand, CommandError
import csv
from playerpoints.models import Players

class Command(BaseCommand):
    help = 'Imports team data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        file_path = options['csv_file']
        
        try:
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    Players.objects.create(
                        name=row['name'],
                        team=row['team'],
                        picture=row['picture']
                    )
            self.stdout.write(self.style.SUCCESS('Successfully imported team data'))
        except FileNotFoundError:
            raise CommandError('File "%s" does not exist' % file_path)

from django.core.management.base import BaseCommand
from infos.models import CollectionsModel


class Command(BaseCommand):

    def handle(self, *args, **options):
        numbers = CollectionsModel.objects.all().values('number', 'id')
        num_dict = {}
        for num_model in numbers:
            if not num_dict.get(num_model['number']):
                num_dict[num_model['number']] = num_model['id']
            else:
                CollectionsModel.objects.get(pk=num_model['id']).delete()

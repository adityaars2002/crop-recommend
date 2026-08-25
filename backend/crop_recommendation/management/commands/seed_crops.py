import json
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from crop_recommendation.models import Crop

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Seeds the database with crop data from data/crops/crops.json'

    def handle(self, *args, **kwargs):
        # Path relative to PROJECT_ROOT
        data_path = settings.PROJECT_ROOT / 'data' / 'crops' / 'crops.json'
        
        if not data_path.exists():
            self.stdout.write(self.style.ERROR(f"Data file not found at {data_path}"))
            return

        with open(data_path, 'r', encoding='utf-8') as f:
            try:
                crops_data = json.load(f)
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f"Invalid JSON: {e}"))
                return

        created_count = 0
        updated_count = 0

        for crop_data in crops_data:
            name = crop_data.get('name')
            if not name:
                continue

            crop, created = Crop.objects.update_or_create(
                name=name,
                defaults={
                    'scientific_name': crop_data.get('scientific_name', ''),
                    'description': crop_data.get('description', ''),
                    'soil_type': crop_data.get('soil_type', ''),
                    'min_ph': crop_data.get('min_ph'),
                    'max_ph': crop_data.get('max_ph'),
                    'water_requirement': crop_data.get('water_requirement', ''),
                    'growing_duration': crop_data.get('growing_duration', ''),
                    'general_information': crop_data.get('general_information', '')
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created crop: {name}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated crop: {name}"))

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded crops. Created: {created_count}, Updated: {updated_count}"
        ))

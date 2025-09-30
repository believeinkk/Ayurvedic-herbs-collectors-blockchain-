from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from traceability.models import (
    Collector, HerbSpecies, CollectionEvent, ProcessingBatch, 
    ProcessingStep, QualityTest
)

class Command(BaseCommand):
    help = 'Load sample data for demonstration'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')
        
        # Create herb species
        species_data = [
            ('ashwagandha', 'Withania somnifera', 'Adaptogenic herb known for stress relief'),
            ('tulsi', 'Ocimum tenuiflorum', 'Sacred basil with immune-boosting properties'),
            ('brahmi', 'Bacopa monnieri', 'Cognitive enhancer and memory booster'),
            ('neem', 'Azadirachta indica', 'Natural antimicrobial and skin health herb'),
            ('turmeric', 'Curcuma longa', 'Anti-inflammatory golden spice'),
            ('ginger', 'Zingiber officinale', 'Digestive aid and anti-nausea herb'),
            ('amla', 'Phyllanthus emblica', 'Vitamin C rich immunity booster'),
        ]
        
        for name, scientific, desc in species_data:
            species, created = HerbSpecies.objects.get_or_create(
                name=name,
                defaults={'scientific_name': scientific, 'description': desc}
            )
            if created:
                self.stdout.write(f'Created species: {species.get_name_display()}')

        # Create collectors
        collectors_data = [
            ('COL001', 'Ramesh Kumar', '9876543210', 'Sitapur', 'Uttar Pradesh', 'LIC001'),
            ('COL002', 'Sunita Devi', '9876543211', 'Lucknow', 'Uttar Pradesh', 'LIC002'),
            ('COL003', 'Mohan Singh', '9876543212', 'Kanpur', 'Uttar Pradesh', 'LIC003'),
            ('COL004', 'Geeta Sharma', '9876543213', 'Agra', 'Uttar Pradesh', 'LIC004'),
            ('COL005', 'Vijay Prasad', '9876543214', 'Allahabad', 'Uttar Pradesh', 'LIC005'),
            ('COL006', 'Maya Kumari', '9876543215', 'Varanasi', 'Uttar Pradesh', 'LIC006'),
        ]
        
        for collector_id, name, phone, village, state, license_num in collectors_data:
            collector, created = Collector.objects.get_or_create(
                collector_id=collector_id,
                defaults={
                    'name': name,
                    'phone': phone,
                    'village': village,
                    'state': state,
                    'license_number': license_num
                }
            )
            if created:
                self.stdout.write(f'Created collector: {collector.name}')

        # Create collection events
        locations = [
            (26.8467, 80.9462),  # Lucknow
            (25.4358, 81.8463),  # Allahabad
            (27.1767, 78.0081),  # Agra
            (26.4499, 80.3319),  # Kanpur
            (25.3176, 82.9739),  # Varanasi
            (27.5706, 80.0982),  # Sitapur
        ]
        
        weather_conditions = ['Sunny, 28°C', 'Cloudy, 25°C', 'Light rain, 22°C', 'Clear sky, 30°C']
        
        collectors = list(Collector.objects.all())
        all_species = list(HerbSpecies.objects.all())
        
        for i in range(20):  # Create 20 collection events
            collector = random.choice(collectors)
            species = random.choice(all_species)
            location = random.choice(locations)
            
            harvest_date = timezone.now().date() - timedelta(days=random.randint(1, 60))
            
            collection = CollectionEvent.objects.create(
                collector=collector,
                species=species,
                harvest_date=harvest_date,
                gps_latitude=location[0] + random.uniform(-0.1, 0.1),
                gps_longitude=location[1] + random.uniform(-0.1, 0.1),
                quantity_kg=random.uniform(5.0, 50.0),
                quality_grade=random.choice(['A', 'B', 'C']),
                weather_conditions=random.choice(weather_conditions),
                soil_ph=random.uniform(6.0, 8.0),
                organic_certified=random.choice([True, False]),
                fair_trade_certified=random.choice([True, False]),
            )
            
            if i < 5:  # Show first few
                self.stdout.write(f'Created collection: {collection.species.name} by {collection.collector.name}')

        # Create processing batches with steps and quality tests
        batch_data = [
            ('ASH-2024-001', 'Himalayan Herbs Processing Pvt Ltd', 'ashwagandha'),
            ('TUL-2024-002', 'Organic India Processing Center', 'tulsi'),
            ('BRA-2024-003', 'Ayurvedic Wellness Solutions', 'brahmi'),
            ('NEE-2024-004', 'Natural Remedies Facility', 'neem'),
            ('TUR-2024-005', 'Golden Spice Processing Unit', 'turmeric'),
        ]
        
        for batch_id, facility, species_name in batch_data:
            # Create batch
            start_date = timezone.now() - timedelta(days=random.randint(10, 30))
            
            batch = ProcessingBatch.objects.create(
                batch_id=batch_id,
                processing_facility=facility,
                start_date=start_date,
                batch_size_kg=random.uniform(100.0, 500.0),
                status=random.choice(['processing', 'quality_testing', 'completed']),
                end_date=start_date + timedelta(days=random.randint(5, 15)) if random.choice([True, False]) else None
            )
            
            # Add collection events to batch
            species_collections = CollectionEvent.objects.filter(species__name=species_name)[:3]
            for collection in species_collections:
                batch.collection_events.add(collection)
            
            # Create processing steps
            step_types = ['cleaning', 'drying', 'grinding', 'sieving', 'packaging']
            operators = ['Rajesh Kumar', 'Priya Singh', 'Amit Sharma', 'Neha Gupta']
            
            for j, step_type in enumerate(step_types[:random.randint(3, 5)]):
                ProcessingStep.objects.create(
                    batch=batch,
                    step_type=step_type,
                    temperature=random.uniform(20.0, 60.0) if step_type in ['drying', 'cleaning'] else None,
                    humidity=random.uniform(30.0, 70.0) if step_type in ['drying', 'cleaning'] else None,
                    duration_hours=random.uniform(2.0, 24.0),
                    operator_name=random.choice(operators),
                    equipment_used=f'Equipment-{random.randint(100, 999)}',
                    notes=f'Standard {step_type} process completed successfully.',
                    timestamp=start_date + timedelta(days=j, hours=random.randint(0, 23))
                )
            
            # Create quality test if batch is in testing or completed
            if batch.status in ['quality_testing', 'completed']:
                test_status = 'passed' if batch.status == 'completed' else random.choice(['pending', 'passed'])
                
                QualityTest.objects.create(
                    batch=batch,
                    test_date=batch.start_date + timedelta(days=random.randint(3, 10)),
                    lab_name=random.choice([
                        'Analytical Labs India Pvt Ltd',
                        'Quality Control Testing Services',
                        'Ayurvedic Research Laboratory',
                        'Herbal Testing Institute'
                    ]),
                    lab_license=f'LAB-{random.randint(1000, 9999)}',
                    moisture_content=random.uniform(5.0, 15.0),
                    pesticide_residue=random.choice(['none', 'low']),
                    heavy_metals='pass',
                    microbial_count=random.randint(100, 10000),
                    dna_verification=True,
                    test_status=test_status,
                    certificate_number=f'CERT-{batch_id}-{random.randint(100000, 999999)}',
                    notes='All parameters within acceptable limits.',
                    active_compounds={
                        'active_ingredient_1': f'{random.uniform(0.5, 5.0):.2f}%',
                        'active_ingredient_2': f'{random.uniform(0.1, 2.0):.2f}%'
                    }
                )
            
            self.stdout.write(f'Created batch: {batch_id}')
        
        # Generate QR codes for all batches
        for batch in ProcessingBatch.objects.all():
            if not batch.qr_code:
                batch.generate_qr_code()
        
        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
        
        # Print summary
        self.stdout.write('\n=== DATA SUMMARY ===')
        self.stdout.write(f'Species: {HerbSpecies.objects.count()}')
        self.stdout.write(f'Collectors: {Collector.objects.count()}')
        self.stdout.write(f'Collection Events: {CollectionEvent.objects.count()}')
        self.stdout.write(f'Processing Batches: {ProcessingBatch.objects.count()}')
        self.stdout.write(f'Processing Steps: {ProcessingStep.objects.count()}')
        self.stdout.write(f'Quality Tests: {QualityTest.objects.count()}')
from django.db import models
from django.utils import timezone
import uuid
import qrcode
from PIL import Image
import io
import os
from django.conf import settings
from django.core.files.base import ContentFile

class Collector(models.Model):
    collector_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, blank=True)
    village = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    license_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.collector_id})"

class HerbSpecies(models.Model):
    SPECIES_CHOICES = [
        ('ashwagandha', 'Ashwagandha (Withania somnifera)'),
        ('tulsi', 'Tulsi (Ocimum tenuiflorum)'),
        ('brahmi', 'Brahmi (Bacopa monnieri)'),
        ('neem', 'Neem (Azadirachta indica)'),
        ('turmeric', 'Turmeric (Curcuma longa)'),
        ('ginger', 'Ginger (Zingiber officinale)'),
        ('amla', 'Amla (Phyllanthus emblica)'),
    ]
    
    name = models.CharField(max_length=50, choices=SPECIES_CHOICES, unique=True)
    scientific_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_name_display()

class CollectionEvent(models.Model):
    event_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE)
    species = models.ForeignKey(HerbSpecies, on_delete=models.CASCADE)
    harvest_date = models.DateField()
    gps_latitude = models.FloatField()
    gps_longitude = models.FloatField()
    quantity_kg = models.FloatField()
    quality_grade = models.CharField(max_length=10, choices=[
        ('A', 'Grade A'), ('B', 'Grade B'), ('C', 'Grade C')
    ])
    weather_conditions = models.CharField(max_length=100)
    soil_ph = models.FloatField(null=True, blank=True)
    organic_certified = models.BooleanField(default=False)
    fair_trade_certified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.species.name} - {self.collector.name} - {self.harvest_date}"

class ProcessingBatch(models.Model):
    batch_id = models.CharField(max_length=50, unique=True)
    collection_events = models.ManyToManyField(CollectionEvent)
    processing_facility = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    batch_size_kg = models.FloatField()
    status = models.CharField(max_length=20, choices=[
        ('processing', 'Processing'),
        ('quality_testing', 'Quality Testing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ], default='processing')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr_code()
    
    def generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr_data = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8000'}/batch/{self.batch_id}/"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_{self.batch_id}.png'
        
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        super().save(update_fields=['qr_code'])
    
    def __str__(self):
        return f"Batch {self.batch_id}"

class ProcessingStep(models.Model):
    STEP_TYPES = [
        ('cleaning', 'Cleaning'),
        ('drying', 'Drying'),
        ('grinding', 'Grinding'),
        ('sieving', 'Sieving'),
        ('packaging', 'Packaging'),
    ]
    
    batch = models.ForeignKey(ProcessingBatch, on_delete=models.CASCADE, related_name='processing_steps')
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    temperature = models.FloatField(null=True, blank=True, help_text="Temperature in Celsius")
    humidity = models.FloatField(null=True, blank=True, help_text="Humidity percentage")
    duration_hours = models.FloatField(null=True, blank=True)
    operator_name = models.CharField(max_length=100)
    equipment_used = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.batch.batch_id} - {self.get_step_type_display()}"

class QualityTest(models.Model):
    TEST_STATUS = [
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ]
    
    batch = models.ForeignKey(ProcessingBatch, on_delete=models.CASCADE, related_name='quality_tests')
    test_date = models.DateTimeField(default=timezone.now)
    lab_name = models.CharField(max_length=200)
    lab_license = models.CharField(max_length=100)
    moisture_content = models.FloatField(help_text="Moisture percentage")
    pesticide_residue = models.CharField(max_length=10, choices=[
        ('none', 'None Detected'),
        ('low', 'Low Levels'),
        ('high', 'High Levels'),
    ])
    heavy_metals = models.CharField(max_length=10, choices=[
        ('pass', 'Within Limits'),
        ('fail', 'Exceeds Limits'),
    ])
    microbial_count = models.IntegerField(help_text="CFU/g")
    dna_verification = models.BooleanField(default=True, help_text="Species DNA verified")
    active_compounds = models.JSONField(default=dict, blank=True)
    test_status = models.CharField(max_length=10, choices=TEST_STATUS, default='pending')
    certificate_number = models.CharField(max_length=100, unique=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.batch.batch_id} - {self.lab_name} - {self.test_status}"
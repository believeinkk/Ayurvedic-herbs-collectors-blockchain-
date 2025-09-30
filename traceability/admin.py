from django.contrib import admin
from .models import Collector, HerbSpecies, CollectionEvent, ProcessingBatch, ProcessingStep, QualityTest

@admin.register(Collector)
class CollectorAdmin(admin.ModelAdmin):
    list_display = ('collector_id', 'name', 'village', 'state', 'created_at')
    search_fields = ('name', 'collector_id', 'village')
    list_filter = ('state', 'created_at')

@admin.register(HerbSpecies)
class HerbSpeciesAdmin(admin.ModelAdmin):
    list_display = ('name', 'scientific_name')
    search_fields = ('name', 'scientific_name')

@admin.register(CollectionEvent)
class CollectionEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'collector', 'species', 'harvest_date', 'quantity_kg', 'quality_grade')
    list_filter = ('species', 'quality_grade', 'harvest_date', 'organic_certified', 'fair_trade_certified')
    search_fields = ('collector__name', 'species__name')
    date_hierarchy = 'harvest_date'

class ProcessingStepInline(admin.TabularInline):
    model = ProcessingStep
    extra = 0

class QualityTestInline(admin.TabularInline):
    model = QualityTest
    extra = 0

@admin.register(ProcessingBatch)
class ProcessingBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_id', 'processing_facility', 'start_date', 'batch_size_kg', 'status')
    list_filter = ('status', 'processing_facility', 'start_date')
    search_fields = ('batch_id', 'processing_facility')
    inlines = [ProcessingStepInline, QualityTestInline]
    filter_horizontal = ('collection_events',)

@admin.register(ProcessingStep)
class ProcessingStepAdmin(admin.ModelAdmin):
    list_display = ('batch', 'step_type', 'operator_name', 'timestamp')
    list_filter = ('step_type', 'timestamp')
    search_fields = ('batch__batch_id', 'operator_name')

@admin.register(QualityTest)
class QualityTestAdmin(admin.ModelAdmin):
    list_display = ('batch', 'lab_name', 'test_date', 'test_status', 'certificate_number')
    list_filter = ('test_status', 'lab_name', 'test_date')
    search_fields = ('batch__batch_id', 'lab_name', 'certificate_number')
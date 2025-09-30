from rest_framework import serializers
from .models import Collector, HerbSpecies, CollectionEvent, ProcessingBatch, ProcessingStep, QualityTest

class CollectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collector
        fields = '__all__'

class HerbSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HerbSpecies
        fields = '__all__'

class CollectionEventSerializer(serializers.ModelSerializer):
    collector_name = serializers.CharField(source='collector.name', read_only=True)
    species_name = serializers.CharField(source='species.get_name_display', read_only=True)
    
    class Meta:
        model = CollectionEvent
        fields = '__all__'

class ProcessingStepSerializer(serializers.ModelSerializer):
    step_type_display = serializers.CharField(source='get_step_type_display', read_only=True)
    
    class Meta:
        model = ProcessingStep
        fields = '__all__'

class QualityTestSerializer(serializers.ModelSerializer):
    test_status_display = serializers.CharField(source='get_test_status_display', read_only=True)
    
    class Meta:
        model = QualityTest
        fields = '__all__'

class ProcessingBatchSerializer(serializers.ModelSerializer):
    processing_steps = ProcessingStepSerializer(many=True, read_only=True)
    quality_tests = QualityTestSerializer(many=True, read_only=True)
    collection_events = CollectionEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProcessingBatch
        fields = '__all__'
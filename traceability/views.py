from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
import json
from .models import Collector, HerbSpecies, CollectionEvent, ProcessingBatch, ProcessingStep, QualityTest
from .serializers import (CollectorSerializer, HerbSpeciesSerializer, CollectionEventSerializer, 
                         ProcessingBatchSerializer, ProcessingStepSerializer, QualityTestSerializer)

# Web Views
def home(request):
    """Dashboard view showing statistics and recent activity"""
    context = {
        'total_collections': CollectionEvent.objects.count(),
        'active_batches': ProcessingBatch.objects.filter(status__in=['processing', 'quality_testing']).count(),
        'completed_batches': ProcessingBatch.objects.filter(status='completed').count(),
        'total_collectors': Collector.objects.count(),
        'recent_collections': CollectionEvent.objects.select_related('collector', 'species').order_by('-created_at')[:5],
        'recent_batches': ProcessingBatch.objects.order_by('-start_date')[:5],
    }
    return render(request, 'traceability/home.html', context)

def collector_form(request):
    """Form for collectors to submit collection events"""
    if request.method == 'POST':
        try:
            collector_id = request.POST.get('collector_id')
            collector, created = Collector.objects.get_or_create(
                collector_id=collector_id,
                defaults={
                    'name': request.POST.get('collector_name'),
                    'village': request.POST.get('village'),
                    'state': request.POST.get('state'),
                    'phone': request.POST.get('phone', ''),
                }
            )
            
            species = get_object_or_404(HerbSpecies, name=request.POST.get('species'))
            
            collection = CollectionEvent.objects.create(
                collector=collector,
                species=species,
                harvest_date=request.POST.get('harvest_date'),
                gps_latitude=float(request.POST.get('gps_latitude')),
                gps_longitude=float(request.POST.get('gps_longitude')),
                quantity_kg=float(request.POST.get('quantity_kg')),
                quality_grade=request.POST.get('quality_grade'),
                weather_conditions=request.POST.get('weather_conditions'),
                organic_certified=request.POST.get('organic_certified') == 'on',
                fair_trade_certified=request.POST.get('fair_trade_certified') == 'on',
            )
            
            messages.success(request, f'Collection event {collection.event_id} recorded successfully!')
            return redirect('collector_form')
            
        except Exception as e:
            messages.error(request, f'Error recording collection: {str(e)}')
    
    context = {
        'species': HerbSpecies.objects.all(),
        'collectors': Collector.objects.all(),
    }
    return render(request, 'traceability/collector_form.html', context)

def processing_form(request):
    """Form for processing facilities to log processing steps"""
    if request.method == 'POST':
        try:
            batch_id = request.POST.get('batch_id')
            
            # Create batch if it doesn't exist
            if not ProcessingBatch.objects.filter(batch_id=batch_id).exists():
                batch = ProcessingBatch.objects.create(
                    batch_id=batch_id,
                    processing_facility=request.POST.get('processing_facility'),
                    start_date=timezone.now(),
                    batch_size_kg=float(request.POST.get('batch_size_kg', 0)),
                )
                
                # Add collection events to batch
                collection_ids = request.POST.getlist('collection_events')
                for event_id in collection_ids:
                    try:
                        event = CollectionEvent.objects.get(event_id=event_id)
                        batch.collection_events.add(event)
                    except CollectionEvent.DoesNotExist:
                        continue
            else:
                batch = ProcessingBatch.objects.get(batch_id=batch_id)
            
            # Add processing step
            ProcessingStep.objects.create(
                batch=batch,
                step_type=request.POST.get('step_type'),
                temperature=float(request.POST.get('temperature')) if request.POST.get('temperature') else None,
                humidity=float(request.POST.get('humidity')) if request.POST.get('humidity') else None,
                duration_hours=float(request.POST.get('duration_hours')) if request.POST.get('duration_hours') else None,
                operator_name=request.POST.get('operator_name'),
                equipment_used=request.POST.get('equipment_used', ''),
                notes=request.POST.get('notes', ''),
            )
            
            messages.success(request, 'Processing step recorded successfully!')
            return redirect('processing_form')
            
        except Exception as e:
            messages.error(request, f'Error recording processing step: {str(e)}')
    
    context = {
        'batches': ProcessingBatch.objects.all(),
        'collection_events': CollectionEvent.objects.all(),
        'step_types': ProcessingStep.STEP_TYPES,
    }
    return render(request, 'traceability/processing_form.html', context)

def lab_form(request):
    """Form for labs to submit quality test results"""
    if request.method == 'POST':
        try:
            batch = get_object_or_404(ProcessingBatch, batch_id=request.POST.get('batch_id'))
            
            QualityTest.objects.create(
                batch=batch,
                lab_name=request.POST.get('lab_name'),
                lab_license=request.POST.get('lab_license'),
                moisture_content=float(request.POST.get('moisture_content')),
                pesticide_residue=request.POST.get('pesticide_residue'),
                heavy_metals=request.POST.get('heavy_metals'),
                microbial_count=int(request.POST.get('microbial_count')),
                dna_verification=request.POST.get('dna_verification') == 'on',
                test_status=request.POST.get('test_status'),
                certificate_number=request.POST.get('certificate_number'),
                notes=request.POST.get('notes', ''),
            )
            
            # Update batch status if test is completed
            if request.POST.get('test_status') == 'passed':
                batch.status = 'completed'
                batch.end_date = timezone.now()
                batch.save()
            elif request.POST.get('test_status') == 'failed':
                batch.status = 'rejected'
                batch.save()
            
            messages.success(request, 'Quality test recorded successfully!')
            return redirect('lab_form')
            
        except Exception as e:
            messages.error(request, f'Error recording quality test: {str(e)}')
    
    context = {
        'batches': ProcessingBatch.objects.filter(status__in=['processing', 'quality_testing']),
    }
    return render(request, 'traceability/lab_form.html', context)

def consumer_portal(request):
    """Consumer portal homepage"""
    return render(request, 'traceability/consumer_portal.html')

def batch_detail(request, batch_id):
    """Detailed view of a batch for consumers"""
    try:
        batch = get_object_or_404(ProcessingBatch, batch_id=batch_id)
        
        context = {
            'batch': batch,
            'collection_events': batch.collection_events.all(),
            'processing_steps': batch.processing_steps.all(),
            'quality_tests': batch.quality_tests.all(),
        }
        return render(request, 'traceability/batch_detail.html', context)
        
    except ProcessingBatch.DoesNotExist:
        messages.error(request, 'Batch not found!')
        return redirect('consumer_portal')

def qr_scan(request, batch_id):
    """QR code scan result page"""
    return redirect('batch_detail', batch_id=batch_id)

def get_batch_data(request, batch_id):
    """API endpoint to get batch data for maps and charts"""
    try:
        batch = ProcessingBatch.objects.get(batch_id=batch_id)
        
        # Prepare collection events for map
        collection_data = []
        for event in batch.collection_events.all():
            collection_data.append({
                'lat': event.gps_latitude,
                'lng': event.gps_longitude,
                'collector': event.collector.name,
                'species': event.species.get_name_display(),
                'harvest_date': event.harvest_date.strftime('%Y-%m-%d'),
                'quantity': event.quantity_kg,
                'grade': event.quality_grade,
            })
        
        # Prepare processing timeline
        timeline_data = []
        for step in batch.processing_steps.all():
            timeline_data.append({
                'step': step.get_step_type_display(),
                'timestamp': step.timestamp.strftime('%Y-%m-%d %H:%M'),
                'operator': step.operator_name,
                'temperature': step.temperature,
                'humidity': step.humidity,
            })
        
        # Prepare quality test data
        quality_data = []
        for test in batch.quality_tests.all():
            quality_data.append({
                'lab': test.lab_name,
                'date': test.test_date.strftime('%Y-%m-%d'),
                'status': test.get_test_status_display(),
                'moisture': test.moisture_content,
                'pesticide': test.get_pesticide_residue_display(),
                'certificate': test.certificate_number,
            })
        
        return JsonResponse({
            'batch_id': batch.batch_id,
            'status': batch.get_status_display(),
            'facility': batch.processing_facility,
            'collection_events': collection_data,
            'processing_timeline': timeline_data,
            'quality_tests': quality_data,
        })
        
    except ProcessingBatch.DoesNotExist:
        return JsonResponse({'error': 'Batch not found'}, status=404)

# REST API ViewSets
class CollectorViewSet(viewsets.ModelViewSet):
    queryset = Collector.objects.all()
    serializer_class = CollectorSerializer

class HerbSpeciesViewSet(viewsets.ModelViewSet):
    queryset = HerbSpecies.objects.all()
    serializer_class = HerbSpeciesSerializer

class CollectionEventViewSet(viewsets.ModelViewSet):
    queryset = CollectionEvent.objects.all()
    serializer_class = CollectionEventSerializer
    
    @action(detail=False, methods=['get'])
    def map_data(self, request):
        """Get collection events data for map display"""
        events = self.get_queryset().select_related('collector', 'species')
        data = []
        for event in events:
            data.append({
                'id': str(event.event_id),
                'lat': event.gps_latitude,
                'lng': event.gps_longitude,
                'collector': event.collector.name,
                'species': event.species.get_name_display(),
                'harvest_date': event.harvest_date.strftime('%Y-%m-%d'),
                'quantity': event.quantity_kg,
                'grade': event.quality_grade,
            })
        return Response(data)

class ProcessingBatchViewSet(viewsets.ModelViewSet):
    queryset = ProcessingBatch.objects.all()
    serializer_class = ProcessingBatchSerializer
    lookup_field = 'batch_id'

class ProcessingStepViewSet(viewsets.ModelViewSet):
    queryset = ProcessingStep.objects.all()
    serializer_class = ProcessingStepSerializer

class QualityTestViewSet(viewsets.ModelViewSet):
    queryset = QualityTest.objects.all()
    serializer_class = QualityTestSerializer
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'collectors', views.CollectorViewSet)
router.register(r'species', views.HerbSpeciesViewSet)
router.register(r'collections', views.CollectionEventViewSet)
router.register(r'batches', views.ProcessingBatchViewSet)
router.register(r'processing-steps', views.ProcessingStepViewSet)
router.register(r'quality-tests', views.QualityTestViewSet)

urlpatterns = [
    # Web interface URLs
    path('', views.home, name='home'),
    path('collector/', views.collector_form, name='collector_form'),
    path('processing/', views.processing_form, name='processing_form'),
    path('lab/', views.lab_form, name='lab_form'),
    path('consumer/', views.consumer_portal, name='consumer_portal'),
    path('batch/<str:batch_id>/', views.batch_detail, name='batch_detail'),
    path('qr/<str:batch_id>/', views.qr_scan, name='qr_scan'),
    
    # API endpoints
    path('api/batch-data/<str:batch_id>/', views.get_batch_data, name='batch_data_api'),
    path('api/', include(router.urls)),
]
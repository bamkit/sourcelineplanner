from django.urls import path
from .views import HomeView, UploadCSVView, DisplayPointsView, UploadPolygonView, MapView, PointsDataView, LoadPreplotView, LoadSequenceView
from .views import DeletePreplotLineView, DeleteFileView, DeleteAllPreplotLinesView
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('upload/', UploadCSVView.as_view(), name='upload_csv'),
    path('display/', DisplayPointsView.as_view(), name='display_points'),
    path('upload_polygon/', UploadPolygonView.as_view(), name='upload_polygon'),
    path('map/', MapView.as_view(), name='map'),
    path('points_data/', PointsDataView.as_view(), name='points_data'),
    path('delete-file/<int:file_id>/', DeleteFileView.as_view(), name='delete_file'),
    path('load-preplot/', LoadPreplotView.as_view(), name='load_preplot'),
    path('delete-preplot-line/<int:line_id>/', DeletePreplotLineView.as_view(), name='delete_preplot_line'),
    path('delete-all-preplot-lines/', DeleteAllPreplotLinesView.as_view(), name='delete_all_preplot_lines'),
    path('load-sequence/', LoadSequenceView.as_view(), name='load_sequence'),
]
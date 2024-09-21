import csv
import re   
import os
# import tempfile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from .models import File, Point, Polygon, PreplotLine
from .models import SequenceFile, SequenceFileDetail
from .forms import CSVUploadForm
import json
from django.http import JsonResponse
from pyproj import CRS, Transformer
from django.shortcuts import redirect
# from django.db import transaction
from .functions import srecords_to_df
import pandas as pd
from background_task import background
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

class HomeView(View):

    def get(self, request):
        # def get(self, request):
        files = File.objects.all()
        points = Point.objects.all()
        polygon = Polygon.objects.first()
        sequences = SequenceFile.objects.all()
        
        # Fetch first and last shotpoints for each SequenceFile
        sequence_points = []
        for sequence in sequences:
            first_point = SequenceFileDetail.objects.filter(sequence_file=sequence).order_by('datetime').first()
            last_point = SequenceFileDetail.objects.filter(sequence_file=sequence).order_by('datetime').last()
            
            if first_point and last_point:
                sequence_points.extend([
                    {
                        'lat': first_point.mean_lat,
                        'lon': first_point.mean_lon,
                        'sp': first_point.sp,
                        'depth': first_point.depth,
                        'sequence_name': sequence.linename,
                        'point_type': 'First'
                    },
                    {
                        'lat': last_point.mean_lat,
                        'lon': last_point.mean_lon,
                        'sp': last_point.sp,
                        'depth': last_point.depth,
                        'sequence_name': sequence.linename,
                        'point_type': 'Last'
                    }
                ])
        
        # Add P190 lines data
        lines = PreplotLine.objects.all()
        lines_data = [
            {
                'linename': line.linename,
                'latitude1': line.latitude1,
                'longitude1': line.longitude1,
                'shotpoint1':line.shotpoint1,
                'latitude2': line.latitude2,
                'longitude2': line.longitude2,
                'shotpoint2': line.shotpoint2
            } for line in lines
        ]
        
        context = {
            'files': files,
            'points': points,
            'polygon': polygon,
            'preplot_lines': json.dumps(lines_data),
            'sequence_points': json.dumps(sequence_points)
        }
        return render(request, 'planner/home.html', context)

class UploadCSVView(View):

    @staticmethod
    def utm_to_latlon(utm_easting, utm_northing, zone=15, northern_hemisphere=True):
        """
        Convert UTM coordinates to geographic coordinates (latitude, longitude in degrees).

        Parameters:
        utm_easting (float): Easting in meters.
        utm_northing (float): Northing in meters.
        zone (int): UTM zone number.
        northern_hemisphere (bool): True if the UTM coordinates are in the northern hemisphere, False for southern hemisphere.

        Returns:
        tuple: (latitude, longitude) in degrees.
        """
        # Define the CRS for UTM Zone with WGS84
        utm_crs = CRS(proj='utm', zone=zone, ellps='WGS84', datum='WGS84', south=not northern_hemisphere)

        # Define the geographic coordinate system (WGS 84)
        wgs84_crs = CRS(proj='latlong', ellps='WGS84', datum='WGS84')

        # Create a transformer object to convert UTM to geographic coordinates
        transformer = Transformer.from_crs(utm_crs, wgs84_crs)

        # Perform the transformation from UTM to latitude/longitude
        longitude, latitude = transformer.transform(utm_easting, utm_northing)

        return latitude, longitude

    def get(self, request):
        form = CSVUploadForm()
        return render(request, 'planner/upload.html', {'form': form})

    def post(self, request):
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            filename = csv_file.name.split('.')[0]  # Get filename without extension

            try:
                file_obj = File.objects.create(name=filename)
                
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                next(reader)  # Skip the header row
                
                for row in reader:
                    if len(row) >= 4:  # Ensure the row has at least 4 columns
                        lat, long = self.utm_to_latlon(float(row[2]), float(row[3]))
                        Point.objects.create(
                            file=file_obj,
                            shotpoint=int(row[1]),
                            east=lat,
                            north=long
                        )
                
                messages.success(request, f"File '{filename}' uploaded successfully.")
                return redirect('display_points')
            except Exception as e:
                messages.error(request, f"An error occurred while processing the file: {str(e)}")
        else:
            for error in form.errors.values():
                messages.error(request, error)

        return render(request, 'planner/upload.html', {'form': form})

class DisplayPointsView(View):
    def get(self, request):
        files = File.objects.all()
        points = Point.objects.all()
        polygon = Polygon.objects.first()
        sequences = SequenceFile.objects.all()
        
        # Fetch first and last shotpoints for each SequenceFile
        sequence_points = []
        for sequence in sequences:
            first_point = SequenceFileDetail.objects.filter(sequence_file=sequence).order_by('datetime').first()
            last_point = SequenceFileDetail.objects.filter(sequence_file=sequence).order_by('datetime').last()
            
            if first_point and last_point:
                sequence_points.extend([
                    {
                        'lat': first_point.mean_lat,
                        'lon': first_point.mean_lon,
                        'sp': first_point.sp,
                        'depth': first_point.depth,
                        'sequence_name': sequence.linename,
                        'point_type': 'First'
                    },
                    {
                        'lat': last_point.mean_lat,
                        'lon': last_point.mean_lon,
                        'sp': last_point.sp,
                        'depth': last_point.depth,
                        'sequence_name': sequence.linename,
                        'point_type': 'Last'
                    }
                ])
        
        # Add P190 lines data
        lines = PreplotLine.objects.all()
        lines_data = [
            {
                'linename': line.linename,
                'latitude1': line.latitude1,
                'longitude1': line.longitude1,
                'latitude2': line.latitude2,
                'longitude2': line.longitude2
            } for line in lines
        ]
        
        context = {
            'files': files,
            'points': points,
            'polygon': polygon,
            'preplot_lines': json.dumps(lines_data),
            'sequence_points': json.dumps(sequence_points)
        }
        return render(request, 'planner/display.html', context)


class UploadPolygonView(View):
    def post(self, request):
        polygon_data = json.loads(request.POST['polygon'])
        Polygon.objects.all().delete()  # Remove existing polygon
        Polygon.objects.create(name="Uploaded Polygon", coordinates=json.dumps(polygon_data))
        return redirect('display_points')
    
class PointsDataView(View):
    def get(self, request):
        points = Point.objects.all().values('shotpoint', 'east', 'north')
        return JsonResponse(list(points), safe=False)

class MapView(View):
    def get(self, request):
        return render(request, 'planner/map.html')
    
class DeleteFileView(View):
    def post(self, request, file_id):
        file = get_object_or_404(File, id=file_id)
        file_name = file.name
        file.delete()
        messages.success(request, f"File '{file_name}' has been deleted successfully.")
        return redirect('display_points')  # or wherever you want to redirect after deletion
    
class LoadPreplotView(View):
    def get(self, request):
        return render(request, 'planner/load_preplot.html')

    def post(self, request):
        if 'preplot_file' not in request.FILES:
            messages.error(request, 'No file was uploaded.')
            return redirect('load_prelot')

        preplot_file = request.FILES['preplot_file']
        if not preplot_file.name.endswith('.p190'):
            messages.error(request, 'Invalid file type. Please upload a .p190 file.')
            return redirect('load_preplot')

        lines_processed = self.process_preplot_file(preplot_file)

        messages.success(request, f'Successfully loaded {preplot_file.name}. Processed {lines_processed} lines.')
        return redirect('home')  # or wherever you want to redirect after upload

    def process_preplot_file(self, file):
        lines_processed = 0
        current_line = None
        for line in file:
            line = line.decode('utf-8').strip()
            if line.startswith('V'):
                match = re.match(r'V(\d+)\s+(\d+)(\d{2})(\d{2})(\d{2}\.\d+)N(\d{3})(\d{2})(\d{2}\.\d+)W\s+(\d+\.\d+)\s*(\d+\.\d+)', line)
                if match:
                    linename = int(match.group(1))
                    shotpoint = int(match.group(2))
                    lat_deg, lat_min, lat_sec = map(float, match.group(3, 4, 5))
                    lon_deg, lon_min, lon_sec = map(float, match.group(6, 7, 8))
                    eastings = float(match.group(9))
                    northings = float(match.group(10))
                    
                    latitude = lat_deg + lat_min/60 + lat_sec/3600
                    longitude = -(lon_deg + lon_min/60 + lon_sec/3600)  # Negative for West
                    
                    if current_line and current_line.linename == linename:
                        current_line.shotpoint2 = shotpoint
                        current_line.eastings2 = eastings
                        current_line.northings2 = northings
                        current_line.latitude2 = latitude
                        current_line.longitude2 = longitude
                        current_line.save()
                        lines_processed += 1
                        current_line = None
                    else:
                        current_line = PreplotLine(
                            linename=linename,
                            shotpoint1=shotpoint,
                            eastings1=eastings,
                            northings1=northings,
                            latitude1=latitude,
                            longitude1=longitude
                        )

        return lines_processed
    
class DeletePreplotLineView(View):
    def post(self, request, line_id):
        line = get_object_or_404(PreplotLine, id=line_id)
        line.delete()
        messages.success(request, f"Preplot Line {line.linename} has been deleted.")
        return redirect('home')
    
class DeleteAllPreplotLinesView(View):
    def post(self, request):
        PreplotLine.objects.all().delete()
        messages.success(request, "All Preplot Lines have been deleted.")
        return redirect('home')
    
@background(schedule=60)
def process_sequence_file(file_path):
    try:
        # Read the file using Django's storage system
        with default_storage.open(file_path) as file:
            df = srecords_to_df(file)

        filename = os.path.basename(file_path)

        # Convert jday and time to a single datetime column
        df['datetime'] = pd.to_datetime(df['jday'].astype(str) + ' ' + df['time'], format='%j %H%M%S')
        
        # Drop the original jday and time columns
        df = df.drop(['jday', 'time'], axis=1)

        sequence_file_obj, created = SequenceFile.objects.get_or_create(
            linename=str(df['linename'].iloc[0]),
            defaults={
                'preplot_number': filename[0:4],
                'type': filename[4],
                'pass_number': filename[5],
                'sequence_number': filename[6:10],
                'filename': filename
            }
        )

        # Create SequenceFileDetail instances
        sequence_file_details = []
        for _, row in df.iterrows():
            sequence_file_detail = SequenceFileDetail(
                sequence_file=sequence_file_obj,
                sp=row['sp'],
                lat=row['lat'],
                long=row['long'],
                east=row['east'],
                north=row['north'],
                depth=row['depth'],
                datetime=row['datetime'],
                zlat1=row['zlat1'],
                zlon1=row['zlon1'],
                zlat2=row['zlat2'],
                zlon2=row['zlon2'],
                zlat3=row['zlat3'],
                zlon3=row['zlon3'],
                mean_lat=row['mean lat'],
                mean_lon=row['mean lon']
            )
            sequence_file_details.append(sequence_file_detail)

        # Bulk create all SequenceFileDetail instances
        SequenceFileDetail.objects.bulk_create(sequence_file_details)

    finally:
        # Delete the temporary file
        default_storage.delete(file_path)

    return len(df)

class LoadSequenceView(View):
    def get(self, request):
        return render(request, 'planner/load_sequence.html')

    def post(self, request):
        try:
            if 'sequence_file' not in request.FILES:
                messages.error(request, 'No file was uploaded.')
                return redirect('load_sequence')

            sequence_files = request.FILES.getlist('sequence_file')
            total_files = len(sequence_files)

            if total_files > settings.DATA_UPLOAD_MAX_NUMBER_FILES:
                messages.error(request, f'Too many files. Maximum allowed is {settings.DATA_UPLOAD_MAX_NUMBER_FILES}.')
                return redirect('load_sequence')

            files_to_process = []
            files_already_loaded = []

            for sequence_file in sequence_files:
                if not sequence_file.name.endswith('.p190'):
                    messages.error(request, f'Invalid file type for {sequence_file.name}. Please upload only .p190 files.')
                    continue

                # Check if file has already been loaded
                if SequenceFile.objects.filter(filename=sequence_file.name).exists():
                    files_already_loaded.append(sequence_file.name)
                    continue

                # Save the file using Django's storage system
                file_path = os.path.join('temp_sequences', sequence_file.name)
                full_path = default_storage.save(file_path, ContentFile(sequence_file.read()))
                files_to_process.append(full_path)

            # Schedule background tasks for files to process
            for file_path in files_to_process:
                process_sequence_file(file_path, schedule=timezone.now())

            # Prepare messages
            if files_to_process:
                messages.success(request, f'Processing {len(files_to_process)} files in the background. Check back later for results.')
            
            if files_already_loaded:
                messages.warning(request, f'The following files were already loaded and skipped: {", ".join(files_already_loaded)}')

            if not files_to_process and not files_already_loaded:
                messages.error(request, 'No valid files were uploaded.')

            return redirect('display_points')

        except ValidationError as e:
            messages.error(request, f'Validation error: {str(e)}')
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {str(e)}')

        return redirect('load_sequence')

from django.http import JsonResponse
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

from api.commands import start, stop, set_params, get_params, get_track, set_track, status


class Start(APIView):
    '''(GET) api/start/ Endpoint for start command'''

    def post(self, request):

        params: dict = request.query_params         # Getting all POST query params

        movement = params.get('movement', None)           # Getting certain params to pass to function
        power = params.get('power', None)
        reserved = params.get('reserved', None)

        responce = start(movement, power, reserved) # Station quering function call and getting responce

        return JsonResponse({                       # Returning responce as JSON
            'info': 'Request was been sent. START',
            'responce': responce,
            })


class Stop(APIView):
    '''(GET) api/stop/ Endpoint for stop command'''
    
    def get(self, request):

        responce: dict = stop()     # Station quering function call and getting responce

        return JsonResponse({       # Returning responce as JSON
            'info': 'Request was been sent. STOP',
            'responce': responce,
            })


class Params(APIView):
    '''(GET/POST) api/params/ Endpoint for set-params/get-params commands'''
    
    def post(self, request): # Set params

        params: dict = request.query_params         # Getting all POST query params
        addr = params.get('addr', None)
        mask = params.get('mask', None)
        gateway = params.get('gateway', None)       # Extracting required params
        systime = params.get('systime', None)
        postname = params.get('postname', None)

        responce: dict = set_params(addr, mask, gateway, systime, postname) # Station-quering function call and getting responce

        return JsonResponse({                       # Returning responce as JSON
            'info': 'Request was been sent. SetParams',
            'responce': responce,
            })
    
    def get(self, request): # Get params

        responce: dict = get_params()               # Station-quering function call and getting responce

        return JsonResponse({                       # Returning responce as JSON
            'info': 'Request was been sent. GetParams',
            'responce': responce,
            })


class Track(APIView):
    '''(GET/POST) api/track/ Endpoint for get/set-track commands'''
    
    def get(self, request): # Get current track

        responce: list = get_track()         # Station quering function call and getting responce

        return JsonResponse({                       # Returning responce as JSON
            'info': 'Request was been sent. GetTrack',
            'responce': responce,
            })

    def post(self, request): # Set new track

        points = request.data           # Getting points array
        responce = set_track(points)    # Station quering function call and getting responce

        return JsonResponse({
            'info': 'Request was been sent. SetTrack',
            'responce': responce,
        })
    

class Status(APIView):
    '''(GET) api/status/ Endpoint for status command'''

    def get(self, request):
        responce = status()                         # Station quering function call and getting responce

        return JsonResponse({                       # Returning responce as JSON
            'info': 'Request was been sent. STATUS',
            'responce': responce,
            })


@api_view(['GET'])
def api_doc(request):
    '''Get REST API documentation in HTML'''

    return render(request, 'api/ppop_api.html')
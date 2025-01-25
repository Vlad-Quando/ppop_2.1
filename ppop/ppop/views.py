from rest_framework.decorators import api_view
from django.http import JsonResponse

@api_view(['GET'])
def api_not_found(request):
    '''For incorrect url'''

    return JsonResponse({
        'info': 'Incorrect url, command does not exist'
    })
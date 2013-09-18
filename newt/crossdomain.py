# $Id: crossdomain.py 671 2011-02-02 23:59:24Z shreyas $
from django import http
import logging
from django.conf import settings
from urlparse import urlparse
from netaddr import all_matching_cidrs
from socket import gethostbyname

logger = logging.getLogger(__name__)
logger.setLevel(getattr(settings, 'LOG_LEVEL', logging.DEBUG))

try:
    XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
    XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
except:
    XS_SHARING_ALLOWED_ORIGINS = '*'
    XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE', 'HEAD']


def check_xs_allowed(url):
    """
    Returns True if cross-domain requests are permitted
    for url and False if not

    Checks against settings.ALLOWED_HOSTS and settings.ALLOWED_CIDRS
    for whitelisted hosts and networks
    """
    try:
        hostname = urlparse(url).hostname
        # Allow whitelisted hosts (to avoid network lookups if not needed
        if hostname in settings.ALLOWED_HOSTS:
            return True
        if all_matching_cidrs(gethostbyname(hostname), settings.ALLOWED_CIDRS):
            return True
        else:
            return False
    except Exception, e:
        logger.warn("Failed lookup on %s: " % hostname)
        return False



class CORSMiddleware(object):
    """
    Enabl
    """
    def process_request(self, request):
        logger.debug("Processing request")
        setattr(request, '_dont_enforce_csrf_checks', True)
        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            if ('HTTP_ORIGIN' in request.META) and check_xs_allowed(request.META['HTTP_ORIGIN']):
                response['Access-Control-Allow-Origin']  = request.META['HTTP_ORIGIN']
            else:
                response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS 
                
            response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS ) 
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Headers'] = 'x-requested-with, content-type'

            return response

        return None

    def process_response(self, request, response):
        logger.debug("Processing response")
        if ('HTTP_ORIGIN' in request.META) and check_xs_allowed(request.META['HTTP_ORIGIN']):
            response['Access-Control-Allow-Origin']  = request.META['HTTP_ORIGIN']
        else:
            response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS        
        
        response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Headers'] = 'x-requested-with, content-type'
        

        return response

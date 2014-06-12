import logging
from django.contrib.auth.models import User 
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

import socket
import re
from OpenSSL import crypto, SSL

logger = logging.getLogger(__name__)

class GetException(Exception): 
    pass
class RetrieveProxyException(Exception): 
    pass

def debuglevel(level):
    return settings.DEBUG


def create_cert_req(keyType = crypto.TYPE_RSA,
                    bits = 1024,
                    messageDigest = "md5"):
    """
    Create certificate request.
    
    Returns: certificate request PEM text, private key PEM text
    """

    # Create certificate request
    req = crypto.X509Req()

    # Generate private key
    pkey = crypto.PKey()
    pkey.generate_key(keyType, bits)

    req.set_pubkey(pkey)
    req.sign(pkey, messageDigest)
    
    cert_req_pem = crypto.dump_certificate_request(crypto.FILETYPE_ASN1,req)
    key_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM,pkey)

    # Nasty OpenSSL 1.0 Hack
    # OpenSSL 1.0 changes the headers from "RSA PRIVATE KEY" to "PRIVATE KEY"
    try:
        ssl_version = SSL.SSLeay_version(SSL.SSLEAY_VERSION)
        logger.debug('Using SSL: ' + ssl_version)
        if ssl_version.startswith("OpenSSL 1"):
            key_pem = re.sub(r'BEGIN PRIVATE KEY', r'BEGIN RSA PRIVATE KEY', key_pem)
            key_pem = re.sub(r'END PRIVATE KEY', r'END RSA PRIVATE KEY', key_pem)
    except Exception, e:
        logger.warn('Using older version of openSSL without SSLeay_version: %s' + e)
    
    return (cert_req_pem, key_pem)
        
def deserialize_response(msg):
    """
    Deserialize a MyProxy server response
    
    Returns: integer response, errortext (if any)
    """
    
    lines = msg.split('\n')
    
    # get response value
    responselines = filter( lambda x: x.startswith('RESPONSE'), lines)
    responseline = responselines[0]
    response = int(responseline.split('=')[1])
    
    # get error text
    errortext = ""
    errorlines = filter( lambda x: x.startswith('ERROR'), lines)
    for e in errorlines:
        etext = e.split('=')[1]
        errortext += etext
    
    return response,errortext
 
               
def deserialize_certs(inp_dat):
    
    pem_certs = []
    
    dat = inp_dat
    
    while dat:

        # find start of cert, get length        
        ind = dat.find('\x30\x82')
        if ind < 0:
            break
            
        len = 256*ord(dat[ind+2]) + ord(dat[ind+3])

        # extract der-format cert, and convert to pem
        c = dat[ind:ind+len+4]
        x509 = crypto.load_certificate(crypto.FILETYPE_ASN1,c)
        pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM,x509)
        pem_certs.append(pem_cert)

        # trim cert from data
        dat = dat[ind + len + 4:]
    

    return pem_certs


CMD_GET="""VERSION=MYPROXYv2
COMMAND=0
USERNAME=%s
PASSPHRASE=%s
LIFETIME=%d\0"""

def myproxy_logon(hostname,username,passphrase,outfile,lifetime=43200,port=7512):
    """
    Function to retrieve a proxy credential from a MyProxy server
    
    Exceptions:  GetException, RetrieveProxyException
    """
    
    context = SSL.Context(SSL.SSLv3_METHOD)
    
    # disable for compatibility with myproxy server (er, globus)
    # globus doesn't handle this case, apparently, and instead
    # chokes in proxy delegation code
    context.set_options(0x00000800L)
    
    # connect to myproxy server
    logger.debug("connect to myproxy server %s" %hostname)
    conn = SSL.Connection(context,socket.socket())
    conn.connect((hostname,port))
    
    # send globus compatibility stuff
    logger.debug("send globus compat byte")
    conn.write('0')

    # send get command
    logger.debug("send get command")
    cmd_get = CMD_GET % (username,passphrase,lifetime)
    conn.write(cmd_get)

    # process server response
    logger.debug("get server response")
    dat = conn.recv(8192)
    logger.debug("receive: %r" %dat)

    response,errortext = deserialize_response(dat)
    if response:
        logger.debug("error: " + errortext)
        raise GetException(errortext)
    else:
        logger.debug("server response ok")
    
    # generate and send certificate request
    # - The client will generate a public/private key pair and send a 
    #   NULL-terminated PKCS#10 certificate request to the server.
    logger.debug("send cert request")
    certreq,privatekey = create_cert_req()
    conn.send(certreq)

    # process certificates
    # - 1 byte , number of certs
    dat = conn.recv(1)
    numcerts = ord(dat[0])
    
    # - n certs
    logger.debug("receive certs")
    dat = conn.recv(8192)
    # if debuglevel(2):
    #     logger.debug('dumping cert data to "%s"' %settings.MYPROXY_DUMP_FILE)
    #     f = file(settings.MYPROXY_DUMP_FILE,'w')
    #     f.write(dat)
    #     f.close()

    # process server response
    logger.debug("get server response")
    resp = conn.recv(8192)
    response,errortext = deserialize_response(resp)
    if response:
        logger.debug("RetrieveProxyException " + errortext)
        raise RetrieveProxyException(errortext)
    else:
        logger.debug("server response ok")

    # deserialize certs from received cert data
    pem_certs = deserialize_certs(dat)
    if len(pem_certs) != numcerts:
        logger.debug("Warning: %d certs expected, %d received" % (numcerts,len(pem_certs)))

    # write certs and private key to file
    # - proxy cert
    # - private key
    # - rest of cert chain
    
    return dict(cert=pem_certs[0], key=privatekey, calist=pem_certs[1:])

#    if debuglevel(1):   print "debug: write proxy and certs to",outfile
#    f = file(outfile,'w')
#    f.write(pem_certs[0])
#    f.write(privatekey)
#    for c in pem_certs[1:]:
#        f.write(c)
#    f.close()
#    return (pem_certs[0],privatekey)



class Cred:
    def __init__(self, cert, key, user, calist=None):
        self.cert = cert
        self.key = key
        self.calist = calist
        self.user = user
  
    def __unicode__(self):
        return self.cert
  


class MyProxyBackend:
    
    def authenticate(self, username=None, password=None, request=None):
        logger.debug('authenticate "%s"' %username)
        try:
            # certs are 15 hours long, (sessions are 12 hours + globus-job-submit needs a 3 hour buffer )
            credentials = myproxy_logon(settings.MYPROXY_SERVER, 
                                        username, password, None, 
                                        lifetime=settings.NEWT_COOKIE_LIFETIME+10800)
        except Exception, e:
            logger.debug("MyProxy Exception: %s" % e)            
            return None

        if credentials == None:
            return None

        try:
            myuser = User.objects.get(username=username)
        except ObjectDoesNotExist:
            # This isn't actually used anywhere, but you might make this smarter
            email = "%s@%s" % (username, settings['NEWT_DOMAIN'])
            try:
                myuser = User.objects.create_user(username, email)
            except Exception,ex:
                logger.error(ex)
                raise ex

        mycred = Cred(cert=credentials['cert'], key=credentials['key'], calist=''.join(credentials['calist']), user=myuser)

        # If we have a request object save the credential in the session
        if request:
            request.session.__setitem__("cred", mycred)
        myuser.backend = 'django.contrib.auth.backends.ModelBackend'
        return myuser
  
    def get_user(self, user_id):
        """Returns User object, throws User.DoesNotExist
        """
        logger.debug("get_user %d " %(user_id))
        try:
            return User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return None

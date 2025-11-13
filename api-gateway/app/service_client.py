"""
Client HTTP pour communiquer avec les autres microservices
"""
import requests
from .auth_middleware import AUTH_SERVICE_URL, USER_SERVICE_URL, ORDERS_SERVICE_URL

class ServiceClient:
    """Client pour communiquer avec les microservices"""
    
    @staticmethod
    def forward_request(service_url, path, method='GET', data=None, headers=None):
        """
        Forward une requête vers un service
        
        Args:
            service_url: URL de base du service
            path: Chemin de la requête
            method: Méthode HTTP
            data: Données à envoyer (pour POST/PUT)
            headers: Headers additionnels
        """
        url = f"{service_url}{path}"
        request_headers = {'Content-Type': 'application/json'}
        
        if headers:
            request_headers.update(headers)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=request_headers, timeout=5)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=request_headers, timeout=5)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=request_headers, timeout=5)
            elif method == 'DELETE':
                response = requests.delete(url, headers=request_headers, timeout=5)
            else:
                return None, {'error': 'Méthode HTTP non supportée'}, 405
            
            return response.json(), None, response.status_code
        except requests.exceptions.RequestException as e:
            return None, {'error': f'Erreur de communication avec le service: {str(e)}'}, 503
    
    @staticmethod
    def forward_to_auth(path, method='GET', data=None, headers=None):
        """Forward vers Auth Service"""
        return ServiceClient.forward_request(AUTH_SERVICE_URL, path, method, data, headers)
    
    @staticmethod
    def forward_to_user(path, method='GET', data=None, headers=None):
        """Forward vers User Service"""
        return ServiceClient.forward_request(USER_SERVICE_URL, path, method, data, headers)
    
    @staticmethod
    def forward_to_orders(path, method='GET', data=None, headers=None):
        """Forward vers Orders Service"""
        return ServiceClient.forward_request(ORDERS_SERVICE_URL, path, method, data, headers)


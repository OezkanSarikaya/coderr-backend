from django.utils.html import strip_tags
import json

class StripHTMLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.content_type == 'application/json':  # Nur JSON-Daten prüfen
                try:
                    # Den Body des Requests parsen
                    data = json.loads(request.body)                    
                    # HTML-Bereinigung anwenden
                    cleaned_data = self.clean_data(data)                    
                    # Den bereinigten Body zurücksetzen
                    request._body = json.dumps(cleaned_data).encode('utf-8')
                except json.JSONDecodeError:
                    print("Invalid JSON format in request body.")
        return self.get_response(request)

    def clean_data(self, data):
        """
        Recursively clean HTML tags from data.
        """
        if isinstance(data, dict):
            return {key: self.clean_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.clean_data(item) for item in data]
        elif isinstance(data, str):
            return strip_tags(data)
        return data

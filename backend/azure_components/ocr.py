from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

import time

'''
Authenticate
Authenticates your credentials and creates a client.
'''
class OCR():
    def __init__(self):
        self.subscription_key = "93cb651cca77468bb4436121527f69f8"
        self.endpoint = "https://uclcsshackathon.cognitiveservices.azure.com/"

        self.computervision_client = ComputerVisionClient(self.endpoint, CognitiveServicesCredentials(self.subscription_key))

    def get_ocr(self, file_name):
        # Get an image with text
        if "png" in file_name or "jpeg" in file_name or "jpg" in file_name:
            read_url = "https://uclcsshackathon.blob.core.windows.net/test/test.png"
        if "pdf" in file_name:
            read_url = "https://uclcsshackathon.blob.core.windows.net/test/test.pdf"
        # Call API with URL and raw response (allows you to get the operation location)
        print(read_url)
        read_response = self.computervision_client.read(read_url,  raw=True)

        # Get the operation location (URL with an ID at the end) from the response
        read_operation_location = read_response.headers["Operation-Location"]
        # Grab the ID from the URL
        operation_id = read_operation_location.split("/")[-1]

        # Call the "GET" API and wait for it to retrieve the results
        while True:
            read_result = self.computervision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)
        result = ""
        # Print the detected text, line by line
        if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    result += (line.text + "\n")
        return result


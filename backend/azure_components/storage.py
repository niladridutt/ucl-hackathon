import uuid
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient

class azure_storage():
    def __init__(self):
        self.storage_name = "uclcsshackathon"
        self.key = "cXjXg5bsojb13C/XlWHigGydjblxc0tGtwtaVN3HKOsTwSmuRLtbZFzCT2K0aTL6UI0QkyUyKef5+ASt9bNKqA=="
        self.default_credential = DefaultAzureCredential()
        self.sas_token = generate_account_sas(
            account_name=self.storage_name,
            account_key=self.key,
            resource_types=ResourceTypes(service=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        self.container_name = "test"
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName=uclcsshackathon;AccountKey=cXjXg5bsojb13C/XlWHigGydjblxc0tGtwtaVN3HKOsTwSmuRLtbZFzCT2K0aTL6UI0QkyUyKef5+ASt9bNKqA==;EndpointSuffix=core.windows.net"
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # self.blob_service_client = BlobServiceClient(account_url="https://%s.blob.core.windows.net/"%self.storage_name, credential=self.sas_token)
        self.container_client = self.blob_service_client.get_container_client(container= self.container_name)

    def upload(self, data_name, data):
        blob_client = BlobClient.from_connection_string(
            self.connection_string, container_name=self.container_name, blob_name=data_name)
        blob_client.upload_blob(data)

    def list_all(self):
        blob_list = self.container_client.list_blobs()
        names = []
        for blob in blob_list:
            names.append(blob.name)

    def delete(self, file_name):
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        blob_client.delete_blob(delete_snapshots="include")

    def get_link(self, file_name):
        url = "https: // uclcsshackathon.blob.core.windows.net / test / %s" % file_name
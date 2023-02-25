from azure.storage.blob import BlobServiceClient


service = BlobServiceClient(account_url="https://<my-storage-account-name>.blob.core.windows.net/", credential=credential)

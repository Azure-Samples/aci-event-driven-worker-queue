from azure.identity import DefaultAzureCredential
import os

class AzureContext(object):
   """Azure Security Context. 

      remarks:
      This is a helper to combine service principal credentials with the subscription id.
      Notice that the client is using default Azure credentials.
      To make default credentials work, ensure that environment variables 'Azure_Client_ID',
      'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
   """
   
   def __init__(self, subscription_id):
      self.credentials = DefaultAzureCredential()
      self.subscription_id = subscription_id


azure_context = AzureContext(
      subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
   )

#ACI Specific configurations
ACI_CONFIG = {
    "subscriptionId": os.getenv("AZURE_SUBSCRIPTION_ID"),
    "resourceGroup": os.getenv("AZURE_RESOURCE_GROUP"),
    "location": os.getenv("AZURE_LOCATION")
}

#CosmosMongoDb without the ssl
DATABASE_URI = os.getenv("COSMOS_CONNECTION_STRING")

queueConf = {
      'queue_name': os.getenv("SERVICE_BUS_CREATE_QUEUE"),
      'delete_queue_name': os.getenv("SERVICE_BUS_DELETE_QUEUE"),
      'connstr': os.getenv('SERVICE_BUS_CONNECTION_STR')
}

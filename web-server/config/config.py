from azure.common.credentials import ServicePrincipalCredentials
import os

class AzureContext(object):
   """Azure Security Context. 

      remarks:
      This is a helper to combine service principal credentials with the subscription id.
      See README for information on how to obtain a service principal attributes client id, secret, etc. for Azure
   """
   
   def __init__(self, subscription_id, client_id, client_secret, tenant):
      self.credentials = ServicePrincipalCredentials(
         client_id = client_id,
         secret = client_secret,
         tenant = tenant
      )
      self.subscription_id = subscription_id


azure_context = AzureContext(
      subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID"),
      client_id =  os.getenv("AZURE_CLIENT_ID"),
      client_secret =  os.getenv("AZURE_CLIENT_SECRET"),
      tenant =  os.getenv("AZURE_TENANT_ID")
   )

#ACI Specific configurations
ACI_CONFIG = {
    "subscriptionId": os.getenv("AZURE_SUBSCRIPTION_ID"),
    "resourceGroup": os.getenv("AZURE_RESOURCE_GROUP")
}

#CosmosMongoDb without the ssl
DATABASE_URI = os.getenv("COSMOS_CONNECTION_STRING")

queueConf = {
      'service_namespace': os.getenv("SERVICE_BUS_NAMESPACE"),
      'saskey_name': os.getenv("SERVICE_BUS_SASKEY_NAME"),
      'saskey_value': os.getenv("SERVICE_BUS_SASKEY_VALUE"),
      'queue_name': os.getenv("SERVICE_BUS_CREATE_QUEUE"),
      'delete_queue_name': os.getenv("SERVICE_BUS_DELETE_QUEUE")
}

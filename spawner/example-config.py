from azure.identity import DefaultAzureCredential

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
      subscription_id = '<subId>'
   )

#ACI Specific configurations
ACI_CONFIG = {
    "subscriptionId": "",
    "resourceGroup": "",
    "location": ""
}

#CosmosMongoDb without the ssl
DATABASE_URI = ""

queueConf = {
      'queue_name': '',
      'connstr': ''
}

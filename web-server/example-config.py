from azure.common.credentials import ServicePrincipalCredentials

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

#Service Principle Creds for ACI
azure_context = AzureContext(
      subscription_id = '',
      client_id = '', #Service Principle ID
      client_secret = '', #SP Key
      tenant = ''  #Directory ID
   )

#ACI Specific configurations
ACI_CONFIG = {
    "subscriptionId": "",
    "resourceGroup": "",
    "location": ""
}

#Cosmosdb mongodb api connection string
DATABASE_URI = "" 

#Service Bus Queue Config
queueConf = {
      'service_namespace': '',
      'saskey_name': '',
      'saskey_value': '',
      'queue_name': ''
}

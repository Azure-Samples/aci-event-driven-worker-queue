'use strict'

var msRestAzure = require("ms-rest-azure");
var resourceManagement = require('azure-arm-resource');
var containerInstance = require('azure-arm-containerinstance');

var clientId = process.env.client_id,
    secret = process.env.client_secret,
    domain = process.env.tenant,
    subscriptionId = process.env.subscription_id,
    db_uri = process.env.CUSTOMCONNSTR_CosmosDB,
    resourceGroupName = process.env.resourceGroup;

const baseName = ["anders", "wenjun", "robbie", "robin", "allen", "tony", "xiaofeng", "tingting", "harry", "chen"];
const IMAGE = "pskreter/worker-container:latest";

var makeId = function() {
    let text = '';
    let possible = "abcdefghijklmnopqrstuvwxyz0123456789";
    for (let i = 0; i < 5; i++){
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}


module.exports = function(context, mySbMsg) {
    context.log('JavaScript ServiceBus queue trigger function processed message', mySbMsg);

    msRestAzure.loginWithServicePrincipalSecret(clientId, secret, domain, function(err, credentials) {
        let client = new containerInstance.ContainerInstanceManagementClient(credentials,subscriptionId);
        let containerName =  baseName[Math.floor(Math.random() * baseName.length)] + "-" + makeId();
        
        let containerGroup = {
            containers: [
                {
                name: containerName,
                environmentVariables: [
                    {   
                        name: "MESSAGE",
                        value: mySbMsg 
                    },
                    {   
                        name: "CONTAINER_NAME",
                        value: containerName
                    },
                    {   
                        name: "DATABASE_URI",
                        value: db_uri
                }],
                image: IMAGE,
                ports: [
                    {
                        "port": 80
                    }
                    ],
                    resources: {
                    requests: {
                        cpu: 1,
                        memoryInGB: 1.5
                    }
                    },
                }
            ],
            restartPolicy: "Never",
            ipAddress: {
                ports: [{ port: 80 }]
            },
            osType: "Linux",
            location: "East US"
        }

        client.containerGroups.createOrUpdate(resourceGroupName, containerName, containerGroup)
            .then( (cgroup) => {
                context.log(cgroup)
            }).catch((err) => {
                context.log(err);
                return;
            });
    });

    context.done();
};
'use strict'

var { ClientSecretCredential } = require("@azure/identity");
var { ContainerInstanceManagementClient } = require("@azure/arm-containerinstance");

var clientId = process.env.client_id,
    secret = process.env.client_secret,
    domain = process.env.tenant,
    subscriptionId = process.env.subscription_id,
    db_connection = process.env.CUSTOMCONNSTR_CosmosDB,
    resourceGroupName = process.env.resourceGroup;

var db_user = db_connection.slice(10, db_connection.indexOf(':',10));
var db_pwd = db_connection.slice(db_connection.indexOf(':',10) + 1, db_connection.indexOf('@'));
var db_uri = 'mongodb://' + db_connection.slice(db_connection.indexOf('@')+1) + '&ssl=true';

const db_name = "containerstate";
const IMAGE = "hubertsui/go-worker:latest";
const MongoClient = require('mongodb').MongoClient;

module.exports = function(context, mySbMsg) {
    if ( !mySbMsg || mySbMsg.length == 0){
        context.done('JavaScript ServiceBus queue message is empty');
        return;
    }

    mySbMsg = mySbMsg.replace(/: u'/g,": '").replace(/'/g,"\"");
    context.log.info('service bus message', mySbMsg);
    var sbMsgObj = JSON.parse(mySbMsg);
    if ( !sbMsgObj || !sbMsgObj.hasOwnProperty('name')){
        let errMsg = 'JavaScript ServiceBus queue message has no container name.'
        context.log.error(errMsg);
        context.done(errMsg);
        return;
    }

    context.log('JavaScript ServiceBus queue trigger function processed message', mySbMsg);
    try{
        context.log.info("got credentials");
        const credentials = new ClientSecretCredential(domain,clientId,secret);

        let client = new ContainerInstanceManagementClient(credentials,subscriptionId);
        let containerName =  sbMsgObj.name;
        let containerMsg = sbMsgObj.input;

        let containerGroup = {
            containers: [
                {
                name: containerName,
                environmentVariables: [
                    {   
                        name: "MESSAGE",
                        value: containerMsg
                    },
                    {   
                        name: "CONTAINER_NAME",
                        value: containerName
                    },
                    {   
                        name: "DATABASE_URI",
                        value: db_connection
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
        };

        context.log.info("creating container");
        client.containerGroups.beginCreateOrUpdateAndWait(resourceGroupName, containerName, containerGroup)
            .then( (cgroup) => {
                context.log(cgroup);
                context.done();
            }).catch((err) => {
                context.log('created container error', err);
                MongoClient.connect(db_uri, { auth:{ user: db_user , password: db_pwd }}, function(dbError, client) {
                    if (dbError){
                        context.log(dbError);
                        context.done(err);
                        return; 
                    }
                
                    context.log("Connected to cosmosdb server");

                    let db = client.db(db_name);
                    let col = db.collection(db_name);
                    col.updateMany({name: containerName }, {$set: { state: "Error", message: JSON.stringify(err) }}, function(dbUpdateError, r){
                        if (dbUpdateError){
                            context.log(dbUpdateError);
                        }
                        client.close();
                        context.done(err)
                    })
                });
            });
    }catch(err){
        console.log(err);
    }

};
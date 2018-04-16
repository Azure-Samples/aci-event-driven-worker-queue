az container create \
    -g aciherodemo \
    -n spawner \
    --image pskreter/spawner:prod \
    --azure-file-volume-account-name $STORAGE_NAME \
    --azure-file-volume-account-key $STORAGE_KEY \
    --azure-file-volume-share-name $SHARE_NAME \
    --azure-file-volume-mount-path /app/config/
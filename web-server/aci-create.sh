az container create \
    -g msazure-aciaks-temp \
    -n web-server \
    --image hubertsui/web-server \
    --dns-name-label msazurebatchdev\
    --ip-address public \
    --ports 80
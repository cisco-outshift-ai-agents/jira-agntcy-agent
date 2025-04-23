source .env

echo "API_PORT=$API_PORT"
echo "API_KEY=$API_KEY"
echo "AGENT_ID=$AGENT_ID"

curl -s -H "content-type: application/json" \
     -H "x-api-key: $API_KEY" \
     -d '{
       "agent_id": "'"$AGENT_ID"'",
       "input": {
         "query": "get details for project APT"
       },
       "config": {
         "configurable": {}
       }
     }' \
     http://127.0.0.1:$API_PORT/runs/wait
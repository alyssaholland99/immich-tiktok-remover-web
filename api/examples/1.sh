curl -X POST -H "Content-Type: application/json" -d '{
  "immich_url": "https://immich.alyssaserver.co.uk/",
  "immich_api_key": "WHablZwyi9OfhsUcMiZXeisQD3OISzVc0KIX0O54",
}' http://localhost:5000/remove

curl -X GET -H "Content-Type: application/json" -d '{
  "pod_id": "immich-tiktok-remover-ae7b5af6274808ba401bfc4538d3a97f-9fbf7qtn"
}' http://localhost:5000/logs
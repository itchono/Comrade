docker image build -t music-bot ./
docker save music-bot
kubectl apply -f deploy.yaml
kubectl get pod --namespace=music-bot

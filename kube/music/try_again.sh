docker image build -t seendsouza/music-bot .
docker push seendsouza/music-bot
kubectl apply -f deploy.yaml
kubectl get pod --namespace=music-bot

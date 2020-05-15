docker image build -t comrade-v3-kubernetes ../
docker save comrade-v3-kubernetes
kubectl apply -f pod.yaml
kubectl get pod --namespace=comrade-v3

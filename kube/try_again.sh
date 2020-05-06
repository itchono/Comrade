docker image build -t comrade-v2-kubernetes ../
docker save comrade-v2-kubernetes
kubectl apply -f pod.yaml
kubectl get pod --namespace=comrade-v2

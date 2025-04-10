for i in {1..100}; do
  kubectl run my-deployment-$i --namespace=apf --image=nginx --restart=Always --expose --port=80
done
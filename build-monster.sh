dockername="$1"

git pull
cname="monster$dockername"
echo "docker name: $dockername"

docker rmi -f $cname
docker  build -t $cname .
docker rm -f $dockername
docker run -it -d --name $dockername $cname


# drm

$imageName = "pskreter/web-server:latest"
$containerName  = "hero-web-server"


if ($args.Count -gt 0 ){

    if($args[0] -eq "dev"){
        docker stop $containerName
        docker run --name $containerName -it --rm -p 8000:8000 -v ${PWD}:/app $imageName /bin/bash
    }
    elseif($args[0] -eq "build-run") {
        docker build -t $imageName .
        docker stop $containerName
        docker run --rm -p 8000:8000 --name $containerName  $imageName
    }
    elseif($args[0] -eq "build-push"){
        docker build -t $imageName .
        docker push $imageName
    }
}
else {
    docker stop $containerName
    docker run --rm -p 8000:8000 --name $containerName  $imageName
}


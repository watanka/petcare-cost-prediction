#!/bin/bash

TARGET_LABEL="OLD"

for service in $(docker-compose ps --services); do
    echo "Service $service"
    if echo "$service" | grep -q '^ml'; then
        
        container=$(docker ps -q --filter "name=$service")
        echo "Container $container"

        env_file_path="/app/app.env"
        
        if docker exec "$container" test -f "$env_file_path"; then
            # .env 파일에서 LABEL을 읽어오기
            label_value=$(docker exec "$container" grep -E '^LABEL=' "$env_file_path" | cut -d '=' -f2 | tr -d '"')

            # LABEL 값이 설정되어 있는지 확인
            if [ -n "$label_value" ]; then
                echo "LABEL found in $container: $label_value"


                if [ "$label_value" = "$TARGET_LABEL" ]; then
                    echo "Stopping container: $container with LABEL: $label_value"
                    # docker stop "$container"

                    echo "Service $service needs to be recreated."

                    docker-compose --env-file .env up -d --no-deps --force-recreate "$service"
                fi
            else
                echo "No LABEL found in $container"
            fi
        else
            echo ".env file not found in $container"
        fi
    fi
done

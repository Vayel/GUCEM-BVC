build:
	docker build . -t bvc --no-cache

create:
	docker run -it --name bvc -u bvc -p 8000:8000 bvc /bin/bash

run:
	docker start bvc
	docker exec -u bvc -d bvc ./runserver.sh

connect:
	docker exec -it bvc /bin/bash

connect_root:
	docker exec -it --user root bvc /bin/bash

stop:
	docker stop bvc

clean: stop
	docker rm bvc

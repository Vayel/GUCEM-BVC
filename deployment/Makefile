build:
	docker build . -t bvc --no-cache

create:
	docker run -it --name bvc bvc /bin/bash

run:
	docker start bvc
	docker exec -u bvc -d bvc ./runserver.sh

connect:
	docker exec -it bvc /bin/bash

connect_root:
	docker exec -it --user root bvc /bin/bash

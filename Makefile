VERSION=0.0.1

build_meteotoni:
	docker build -t meteotoni:$(VERSION) meteotoni

build_all:
	docker build -t meteotoni:$(VERSION) meteotoni
	docker build -t simulator:$(VERSION) simulator

run_meteotoni:
	docker-compose -f docker-compose.yml up -d

run_all:
	docker-compose -f docker-compose.yml -f docker-compose.simulator.yml up -d

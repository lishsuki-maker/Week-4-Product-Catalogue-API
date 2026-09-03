.PHONY: build security

build:
	docker build -t product-catalogue-api:2.0.0 .

security: build
	./security_gate.sh

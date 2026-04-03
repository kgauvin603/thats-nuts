# Architecture

## v0.1 architecture

Client
-> FastAPI backend
-> ingredient parser
-> nut rules engine
-> JSON seed dictionary

## Near-term evolution

v0.2
-> PostgreSQL for ingredient and product persistence

v0.3
-> UPC lookup service
-> external product sources
-> cached product assessments

v0.4
-> Flutter mobile app
-> barcode scanning

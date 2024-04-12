Install requirements packages:
pip install -r requirements.txt

Run wer-server:
flask --app main.py --debug run

Run mongodb:
sudo docker-compose -f docker-compose.yaml up

Show containers:
docker ps -a

Restart mongodb:
 sudo docker stop tulip_mongodb_1
 sudo docker stop tulip_mongo-express_1
 sudo docker rm $(docker ps -a -q) 
 sudo docker rm tulip_mongo-express_1
 sudo docker rm tulip_mongodb_1

Mongodb server:
http://0.0.0.0:8081/


Fill db testing data:
python fill_db.py

Testing server(tests/test_server.py):
export PYTHONPATH="$PYTHONPATH:."
pytest




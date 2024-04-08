Install requirements packages:
pip install -r requirements.txt

Run wer-server:
flask --app main.py --debug run

Run mongodb:
sudo docker-compose -f docker-compose.yaml up

Fill db testing data:
python fill_db.py



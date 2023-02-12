from fastapi.testclient import TestClient
from main import app

client = TestClient(app=app)

PAYLOAD = {
    "inputs": [
        "İskenderun Hatay Mustafa Kemal mahallesi 544 sokak no:11 (Batı Göz hastanesi"
        " sokağı) Selahattin Yurt Dudu Yurt Sezer Yurt GÖÇÜK ALTINDALAR!!! #DEPREMOLDU"
        " #depremhatay #deprem #Hatay #hatayacil #HatayaYardım #hataydepremi",
        "LÜTFEN YAYIN!!!! 8 katlı bina HATAYDA Odabaşı mah. Uğur Mumcu caddesi no 4"
        " Mahmut Karakaş kat 4",
    ]
}


def test_intent():
    payload = PAYLOAD
    response = client.post("/intent-extractor/", json=payload)
    assert response.status_code == 200

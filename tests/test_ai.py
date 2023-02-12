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
    ],
}


def test_intent():
    response = client.post("/intent-extractor/", json=PAYLOAD)
    assert response.status_code == 200
    outputs = response.json()["response"]
    assert isinstance(outputs, list)

    for obj in outputs:
        assert isinstance(obj, dict)
        assert "string" in obj
        assert "processed" in obj
        assert isinstance(obj["processed"]["intent"], list)
        assert len(obj["processed"]["intent"]) > 0
        assert isinstance(obj["processed"]["detailed_intent_tags"], list)
        assert len(obj["processed"]["detailed_intent_tags"]) > 0

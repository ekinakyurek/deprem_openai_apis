from typing import List
from pydantic import BaseModel, Field


class RequestAddress(BaseModel):
    inputs: List[str] = Field(
        description="list of tweets to classify or parse",
        default="""["İskenderun Hatay Mustafa Kemal mahallesi 544 sokak no:11 (Batı Göz hastanesi sokağı) Selahattin Yurt Dudu Yurt Sezer Yurt GÖÇÜK ALTINDALAR!!! #DEPREMOLDU #depremhatay #deprem #Hatay #hatayacil #HatayaYardım #hataydepremi", "LÜTFEN YAYIN!!!! 8 katlı bina HATAYDA Odabaşı mah. Uğur Mumcu caddesi no 4 Mahmut Karakaş kat 4"]""",
    )


class RequestIntent(BaseModel):
    inputs: List[str] = Field(
        description="list of tweets to classify or parse",
        default="""["İskenderun Hatay Mustafa Kemal mahallesi 544 sokak no:11 (Batı Göz hastanesi sokağı) Selahattin Yurt Dudu Yurt Sezer Yurt GÖÇÜK ALTINDALAR!!! #DEPREMOLDU #depremhatay #deprem #Hatay #hatayacil #HatayaYardım #hataydepremi", "LÜTFEN YAYIN!!!! 8 katlı bina HATAYDA Odabaşı mah. Uğur Mumcu caddesi no 4 Mahmut Karakaş kat 4"]""",
    )

import json
from Levenshtein import distance


class Validator:
    def __init__(self, data_path: str, llm_output: str):
        # LLM output example: {'province': 'Hatay', 'city': 'İskenderun', 'mahallesi | bulvarı': 'Mustafa Kemal Mahallesi', 'sokak | caddesi | yolu': '544 Sokak', 'no | blok': '11', 'sitesi | apartmanı': '', 'phone': '', 'isimler': 'Selahattin Yurt, Dudu Yurt, Sezer Yurt'}
        self.llm_output: dict = json.loads(llm_output)
        self.data_path: str = data_path
        self.cities: list = []
        self.provinces: list = []
        self.province_city_mapping: list = {}
        self._load_json()

    def fetch_closest(self) -> tuple:
        # This method will return the most closest province and city to the LLM output. The output from the llm could be noisy or incorrent.
        # Will return closest province and city
        llm_province = self.llm_output["province"].lower()
        llm_city = self.llm_output["city"].lower()
        city_scores = {}
        province_scores = {}
        for province in self.provinces:
            province_scores[province] = self._get_score(llm_province, province.lower())
        for city in self.cities:
            city_scores[city] = self._get_score(llm_city, city.lower())
        closest_province = min(province_scores, key=province_scores.get)
        closest_city = min(city_scores, key=city_scores.get)
        return (closest_province, closest_city)

    def validate(self):
        # This method will validate whether the city and province are correct or not.
        # Initially, we will only validate whether a city is in a province or not.
        province, city = self.fetch_closest()
        if city in self.province_city_mapping[province]["cities"]:
            return True
        return False

    def _load_json(self):
        f = open(self.data_path)
        self.province_city_mapping = json.load(f)
        self.provinces = list(self.province_city_mapping.keys())
        for province in self.provinces:
            self.cities.extend(self.province_city_mapping[province]["cities"])
        f.close()

    def _get_score(self, a: str, b: str):
        # returns the levenshtein distance between two strings
        return distance(a, b)

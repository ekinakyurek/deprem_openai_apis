# TODOs

1) Check the error handling
- batch size > 20, give error --- # başka bir endpoint gelirse apikey ile artırılabilir. current limit <= 20
- token size limit prompt token + context token <= 4097, current prompt ile 2000 olabilir ama 1000 ok.
- current prompt v5 categories token size --> Tokens = 1,472
- json.loads() #
- eval() # eval kullanmayacakmısız

# fix postprocess_for_intent_v2
    - regex.match -> eger match olmazsa ne oluyor, 
        INTENT için halucination olursa sorun değil çünkü intent ler sadece bert den gelecek, ilgili text in needs leri gerekiyor sadece.
        bu yüzden belki prompt da değişiebilir bu noktadan sonra. [TODO]
    - constant formate - input ve output örnekleri lazım
        INPUT
        
## INPUT BATCH INPUT
{'inputs': ['İncilikaya mahallesi Şehitkamil/Gaziantep Lütfen bu bölgeye acil çadır, ilaç, aspirin desteği insanlar kendi imkanlarıyla olan çadırlara sığmaya çalışıyorlar lütfen yardım edin !! @AFADBaskanlik @ahbap @EmniyetGM @jandarma @Kizilay',
  'İncilikaya mahallesi Şehitkamil/Gaziantep Lütfen bu bölgeye acil çadır, ilaç, aspirin desteği insanlar kendi imkanlarıyla olan çadırlara sığmaya çalışıyorlar lütfen yardım edin !! @AFADBaskanlik @ahbap @EmniyetGM @jandarma @Kizilay']}

## EXAMPLE BATCH OUTPUT
{'response': [{'string': ['People need [çadır, ilaç, aspirin], tags are [SHELTER, HEALTH, MEDICINE]'],
   'processed': {'intent': ['Barinma', 'Saglik', 'MEDICINE'],
    'detailed_intent_tags': ['çadır', 'ilaç', 'aspirin']}},
  {'string': ['People need [çadır, ilaç, aspirin], tags are [SHELTER, HEALTH, MEDICINE]'],
   'processed': {'intent': ['Barinma', 'Saglik', 'MEDICINE'],
    'detailed_intent_tags': ['çadır', 'ilaç', 'aspirin']}}]}

        örnek request
        batch inference nasıl dönüyor

3) Prompt fix & automatic CI
    prompts/intent_v5_categories.txt
    # update after TAG_MAP

5) Grad IO?

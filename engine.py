
import warnings
warnings.filterwarnings('ignore')

import os
import argparse
import json

import config
import annotate
import dbengine

import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence

CEND = '\033[0m'
CSEL = '\33[7m'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('split')
    parser.add_argument('table_id')
    args = parser.parse_args()

    r = sr.Recognizer()
    print(CSEL + "Speak up your Question: " + CEND)
    with sr.Microphone() as source:
        audio_data = r.record(source, duration=5)
        question = r.recognize_google(audio_data) + "?"
        print("\n\n" + "Your Question: " + question)

    annotate.annotate_and_save(question.lower(), args.table_id, args.split)
    generate_queries = \
    "python3 ./sqlova/predict.py --bert_type_abb {} \
        --model_file {}/model_best.pt \
        --bert_model_file {}/model_bert_best.pt  \
        --bert_path {}/ \
        --result_path ./ \
        --data_path {}/ \
        --split {} > /dev/null 2>&1".format(config.BERT_TYPE,
                                    config.MODELS_PATH,
                                    config.MODELS_PATH,
                                    config.MODELS_PATH,
                                    config.DATABASE_PATH,
                                    args.split,
                                    )

    os.system(generate_queries)

    with open('results_{}.jsonl'.format(args.split), 'r') as result:
        result = json.load(result)
    print("Generated Query:" , result['sql'])
    db = dbengine.DBEngine("{}/{}.db".format(config.DATABASE_PATH, args.split))
    table = db.execute_query(args.table_id, result['query'])
    print(table)


import warnings
warnings.filterwarnings('ignore')

import os
import json

from dbva import config
from dbva.annotate import annotate_and_save
from dbva.dbengine import DBEngine

import os

def convert_to_query(question, split, table_id):

    if question[-1] != "?":
        question += "?"

    annotate_and_save(question.lower(), table_id, split)
    generate_queries = \
    "python3 ./dbva/sqlova/predict.py --bert_type_abb {} \
        --model_file ./dbva/{}/model_best.pt \
        --bert_model_file ./dbva/{}/model_bert_best.pt  \
        --bert_path ./dbva/{}/ \
        --result_path ./dbva/ \
        --data_path ./dbva/{}/ \
        --split {} > /dev/null 2>&1".format(config.BERT_TYPE,
                                    config.MODELS_PATH,
                                    config.MODELS_PATH,
                                    config.MODELS_PATH,
                                    config.DATABASE_PATH,
                                    split,
                                    )
    #
    os.system(generate_queries)

    with open('./dbva/results_{}.jsonl'.format(split), 'r') as result:
        result = json.load(result)
    print("Generated Query:" , result['sql'])
    db = DBEngine("./dbva/{}/{}.db".format(config.DATABASE_PATH, split))
    query = db.execute_query(table_id, result['query'])
    print("Query from sqlova is: ")
    print(query)
    return query

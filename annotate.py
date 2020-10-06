import argparse
import json

import config

template = {
    "phase": 1,
    "table_id": "",
    "question": "",
    "sql": {
        "sel": 0,
        "conds": [],
        "agg": 0
        },
    "question_tok": [],
    "query":""
    }

def annotated_json(question, table_id):
    question_tok = []
    cur_tok = ''
    for i in range(len(question)):
        if question[i].isalnum():
            cur_tok += question[i]
        else:
            if question[i] == '-':
                cur_tok += question[i]    
                continue
            question_tok.append(cur_tok)
            cur_tok = ''
            if question[i] != ' ':
                question_tok.append(question[i])
    template['question'] = question
    template['question_tok'] = question_tok
    template['table_id'] = table_id
    return template


def annotate_and_save(question, table_id, split):

    json_file_name = '{}/{}_tok.jsonl'.format(config.DATABASE_PATH, split)
    annotated_data = annotated_json(question, table_id)
    with open(json_file_name, 'w') as fout:
        json.dump(annotated_data, fout)
        fout.write('\n')

if __name__ == '__main__':
    pass

import sys
sys.path.append("/home/rushabh/anaconda3/lib/python3.7/site-packages/")

import records
import re
from babel.numbers import parse_decimal, NumberFormatError
from dbva.sqlova.wikisql.lib.query import Query

schema_re = re.compile(r'\((.+)\)')
num_re = re.compile(r'[-+]?\d*\.\d+|\d+')

class DBEngine:

    def __init__(self, fdb):
        self.db = records.Database('sqlite:///{}'.format(fdb))

    def execute_query(self, table_id, query, *args, **kwargs):
        return self.execute(table_id, query['sel'], query['agg'], query['conds'], *args, **kwargs)

    def execute(self, table_id, select_index, aggregation_index, conditions, lower=True):
        if not table_id.startswith('table'):
            table_id = 'table_{}'.format(table_id.replace('-', '_'))
        table_info = self.db.query('SELECT sql from sqlite_master WHERE tbl_name = :name', name=table_id).all()[0].sql
        table_info = table_info.replace('\n', '')
        schema_info = schema_re.findall(table_info)
        schema_str = schema_info[0] if schema_info else ''
        schema = {}
        if schema_str:
            for tup in schema_str.split(', '):
                tup = tup.strip(' ')
                c, t = tup.split()
                schema[c] = t

        select = 'col{}'.format(select_index)
        agg = Query.agg_ops[aggregation_index]
        if agg:
            select = '{}({})'.format(agg, select)
        where_clause = []
        where_map = {}
        for col_index, op, val in conditions:
            if lower and isinstance(val, str):
                val = val.lower()
            if schema['col{}'.format(col_index)] in 'real' and not isinstance(val, (int, float)):
                try:
                    val = float(parse_decimal(val))
                except NumberFormatError:
                    val = float(num_re.findall(val)[0])
            where_clause.append('col{} {} :col{}'.format(col_index, Query.cond_ops[op], col_index))
            where_map['col{}'.format(col_index)] = val
        where_str = ''
        if where_clause:
            where_str = 'WHERE ' + ' AND '.join(where_clause)
            for key, val in where_map.items():
                where_str = where_str.replace(":{}".format(key), val)

        return 'SELECT {} AS result FROM {} {}'.format(select, table_id, where_str)


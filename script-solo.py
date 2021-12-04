import psycopg2
from psycopg2 import Error
import json
from decimal import Decimal


def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(
        "Object of type '%s' is not  hjhjhJSON serializable" % type(obj).__name__)


class MultiDimensionalArrayEncoder(json.JSONEncoder):
    def encode(self, obj):
        def hint_tuples(item):
            if isinstance(item, tuple):
                return {'__tuple__': True, 'items': item}
            if isinstance(item, list):
                return [hint_tuples(e) for e in item]
            if isinstance(item, Decimal):
                return str(item)
            if isinstance(item, dict):
                return {key: hint_tuples(value) for key, value in item.items()}
            else:
                return item

        return super(MultiDimensionalArrayEncoder, self).encode(hint_tuples(obj))


def hinted_tuple_hook(obj):
    if '__tuple__' in obj:
        return tuple(obj['items'])
    else:
        return obj


db = "db"
password = "password"
user = "user"
host = "host"
port = "port"

connectionA = ""
folderA = "B/"
resultA = 0
result = []
for i in range(1, 13):
    try:
        connectionA = psycopg2.connect(user=user,
                                       password=password,
                                       host=host,
                                       port=port,
                                       database=db)

        # Create a cursor to perform database operations
        cursorA = connectionA.cursor()

        queryA = ''.join(
            open(folderA+'query_'+str(i)+'.sql', 'r').readlines()).strip().strip('\n')

        explodeA = queryA.replace('\n', ' ').split(";")
        if "" in explodeA:
            explodeA.remove("")

        firstA = explodeA[0:len(explodeA)-1]
        lastA = explodeA[len(explodeA)-1]

        cursorA.execute(queryA)

        resultA = cursorA.fetchall()

        print()
        uguale = {"id": i, "content": {
            "A": {"query": queryA, "result": resultA}}, "status": 'ok'}
        result.append(uguale)

    except (Exception, Error) as error:
        diversa = {"id": i, "content": {"A": {"query": queryA,
                                              "result": resultA, }, }, "status": "err", "error": str(error)}
        result.append(diversa)
        print("ERRORE:", error)
    finally:
        if (connectionA):
            cursorA.close()
            connectionA.close()
result = json.dumps(result, default=default)

# result = (MultiDimensionalArrayEncoder()).encode(diverse)
# result = json.dumps(diverse, default=default)
open("web/result.json", 'w').write(result)

import psycopg2
from psycopg2 import Error
import json
import re
from decimal import Decimal
import credentials


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

scriviUguali = True

connectionA = ""
connectionB = ""
folderA = "A/"
folderB = "B/"
uguali = []
diverse = []
tutte = []

resultA = 0
resultB = 0
for i in range(1, 13):
    try:
        connectionA = psycopg2.connect(user=credentials.user,
                                       password=credentials.password,
                                       host=credentials.host,
                                       port=credentials.port,
                                       database=credentials.db)
        connectionB = psycopg2.connect(user=credentials.user,
                                       password=credentials.password,
                                       host=credentials.host,
                                       port=credentials.port,
                                       database=credentials.db)
        connectionC = psycopg2.connect(user=credentials.user,
                                       password=credentials.password,
                                       host=credentials.host,
                                       port=credentials.port,
                                       database=credentials.db)

        # Create a cursor to perform database operations
        cursorA = connectionA.cursor()
        cursorB = connectionB.cursor()
        cursorC = connectionC.cursor()

        queryA = ''.join(
            open(folderA+'query_'+str(i)+'.sql', 'r').readlines()).strip()
        queryB = ''.join(
            open(folderB+'query_'+str(i)+'.sql', 'r').readlines()).strip()

        queryA = re.sub(
            '(\/*(\*)+[^*]+\*\/)|--[^\n\r]+?(?:\*\)|[\n\r])|--\n', '', queryA)
        queryB = re.sub(
            '(\/*(\*)+[^*]+\*\/)|--[^\n\r]+?(?:\*\)|[\n\r])|--\n', '', queryB)

        queryA = queryA.strip('\n')
        queryB = queryB.strip('\n')

        explodeA = queryA.replace('\n', ' ').split(";")
        if "" in explodeA:
            explodeA.remove("")
        explodeB = queryB.replace('\n', ' ').split(";")
        if "" in explodeB:
            explodeB.remove("")

        firstA = explodeA[0:len(explodeA)-1]
        lastA = explodeA[len(explodeA)-1]
        firstB = explodeB[0:len(explodeB)-1]
        lastB = explodeB[len(explodeB)-1]

        cursorA.execute(queryA)
        cursorB.execute(queryB)

        resultA = cursorA.fetchall()
        resultB = cursorB.fetchall()

        print()
        if resultA == resultB:
            print("query "+str(i)+" è UGUALE")
            uguale = {"id": i, "content": {"A": {"query": queryA, "result": resultA}, "B": {
                "query": queryB, "result": resultB}}, "status": 'ok'}
            uguali.append(uguale)
            tutte.append(uguale)
        else:
            print("query "+str(i)+" è DIVERSA")

            # print("queri di A:")
            # print(queryA)
            # print("dati di A")
            # print(resultA)
            # print("queri di B:")
            # print(queryB)
            # print("dati di B")
            # print(resultB)
            queryDiffAinB = "select * from ("+lastA + \
                ")A except select * from ("+lastB+")B"
            queryDiffBinA = "select * from ("+lastB + \
                ")B except select * from ("+lastA+")A"

            queryFirstA = ';'.join(firstA)
            queryFirstB = ';'.join(firstB)

            # print("<query>  ", queryFirstA, " </query>")
            # print("<query>  ", queryFirstB, " </query>")

            queryFirst = queryFirstA+";"+queryFirstB+";"
            queryFull = queryFirst + queryDiffAinB

            # print(queryFull)

            cursorC.execute(queryFull)
            resDiffAinB = cursorC.fetchall()
            cursorC.execute(queryDiffBinA)
            resDiffBinA = cursorC.fetchall()

            diversa = {"id": i, "content": {"A": {"query": queryA, "result": resultA, "diff": resDiffAinB}, "B": {
                "query": queryB, "result": resultB, "diff": resDiffBinA}}, "status": 'div'}
            diverse.append(diversa)
            tutte.append(diversa)

    except (Exception, Error) as error:
        diversa = {"id": i, "content": {"A": {"query": queryA, "result": resultA, "diff": resDiffAinB}, "B": {
            "query": queryB, "result": resultB, "diff": resDiffBinA}}, "status": "err", "error": str(error)}
        diverse.append(diversa)
        tutte.append(diversa)
        print("ERRORE:", error)
        print(queryDiffAinB)
        print(queryDiffBinA)
    finally:
        if (connectionA):
            cursorA.close()
            connectionA.close()
        if (connectionB):
            cursorB.close()
            connectionB.close()
print()
print("-----STATISTICHE-----")
print("uguali: ", str(len(uguali))+"/"+str(12))
print("diversi: ", str(len(diverse))+"/"+str(12))

result = json.dumps(tutte, default=default)

open("web/result.json", 'w').write(result)

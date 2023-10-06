import cx_Oracle
import config_db as cfg

def get_token_DB():
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()
    cursor.execute("SELECT TOKEN FROM SABRE_TOKEN")

    token = cursor.fetchall()
    connection.commit()

    cursor.close()
    connection.close()

    return token[0][0]


def updateToken(token):
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()
    sql = "UPDATE SABRE_TOKEN SET TOKEN = :v, CREATE_DATE = sysdate WHERE USER_NAME = '85018'"
    
    cursor.execute(sql, {'v': token})
    connection.commit()

    cursor.close()
    connection.close()


def insertPrice(valueList):
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()
    cursor.executemany("""
                        INSERT INTO FARE_ALERT_PRICE_LIST_V2("DEPARTURE_CITY", "DESTINATION_CITY", "DEPARTURE_DATE", "RETURN_DATE", "ADULT_DEPARTURE_PRICE_FROM", "ADULT_RETURN_PRICE_FROM", "CURRENCY", "ROUTE_TYPE", "TOTAL_PASSENGER", "ADULT", "CHILDREN", "INFANT", "CHILDREN_DEPARTURE_PRICE_FROM", "CHILDREN_RETURN_PRICE_FROM", "INFANT_DEPARTURE_PRICE_FROM", "INFANT_RETURN_PRICE_FROM", "TOTAL_DEPARTURE_PRICE", "TOTAL_RETURN_PRICE") 
                        VALUES (:1, :2, TO_DATE(REPLACE(:3, 'T', ' '),'yyyy-mm-dd HH24:MI:SS'), TO_DATE(REPLACE(:4, 'T', ' '),'yyyy-mm-dd HH24:MI:SS'),:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18)
                        """
                        ,valueList)
    # commit work
    connection.commit()

    cursor.close()
    connection.close()
import cx_Oracle
import config_db as cfg

def get_token_DB():
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()
    cursor.execute("SELECT TOKEN FROM SF_TOKEN")

    token = cursor.fetchall()
    connection.commit()

    cursor.close()
    connection.close()

    return token[0][0]


def updateToken(token):
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()
    sql = "UPDATE SF_TOKEN SET TOKEN = :v, CREATE_DATE = sysdate WHERE USER_NAME = 'admin.gms2@vna.sca'"
    
    cursor.execute(sql, {'v': token})
    connection.commit()

    cursor.close()
    connection.close()


def getDistinctSFtable():
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()
    
    cursor.execute("SELECT DISTINCT SF_TABLE FROM CONFIG_FROM_SF_TO_DWH where status = 'active'")
    sf_tables = cursor.fetchall()
    connection.commit()

    cursor.close()
    connection.close()

    tables = list()
    for table in sf_tables:
        tables.append(table[0])
    
    return tables



def getSelectForm(tableSF):
    result = getSFfields(tableSF)
    sf_where = getSFwhere(tableSF)
    
    sql = "SELECT "
    for i in range(len(result) - 1):
        sql += f"{result[i][0]}, "
    sql += f"{result[-1][0]} FROM {tableSF} {sf_where}"
    
    return sql


def getSFwhere(tableSF):
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()

    sql = f"SELECT SF_WHERE FROM INT.CONFIG_FROM_SF_TO_DWH WHERE SF_TABLE = '{tableSF}'"

    cursor.execute(sql)

    sf_where = cursor.fetchall()

    connection.commit()

    cursor.close()
    connection.close()

    return sf_where[0][0]


def getSFfields(tableSF):
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()

    sql = f"SELECT SF_FIELDS FROM INT.CONFIG_FROM_SF_TO_DWH WHERE SF_TABLE = '{tableSF}' ORDER BY SF_FIELDS"

    cursor.execute(sql)

    sf_fileds = cursor.fetchall()

    connection.commit()

    cursor.close()
    connection.close()

    return sf_fileds


def getDWHfields(tableSF):
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()

    sql = f"SELECT DWH_FIELDS FROM INT.CONFIG_FROM_SF_TO_DWH  WHERE SF_TABLE = '{tableSF}' ORDER BY SF_FIELDS"

    cursor.execute(sql)

    dwh_fileds = cursor.fetchall()

    connection.commit()

    cursor.close()
    connection.close()

    return dwh_fileds


def getPrimaryKeyFields():
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()

    sql = "SELECT SF_FIELDS, DWH_FIELDS FROM INT.CONFIG_FROM_SF_TO_DWH WHERE IS_PRIMARY_KEY = 1"

    cursor.execute(sql)

    PK_fileds = cursor.fetchall()

    connection.commit()

    cursor.close()
    connection.close()

    SF_PK_fields = PK_fileds[0][0]
    DWH_PK_fields = PK_fileds[0][1]

    return SF_PK_fields, DWH_PK_fields


def getNonPrimaryKeyFields():
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()

    sql = "SELECT SF_FIELDS, DWH_FIELDS FROM INT.CONFIG_FROM_SF_TO_DWH WHERE IS_PRIMARY_KEY = 0"

    cursor.execute(sql)

    non_PK_fields = cursor.fetchall()

    connection.commit()

    cursor.close()
    connection.close()

    SF_non_PK_fields = list()
    DWH_non_PK_fields = list()
    for item in non_PK_fields:
        SF_non_PK_fields.append(item[0])
        DWH_non_PK_fields.append(item[1])
    return SF_non_PK_fields, DWH_non_PK_fields


def getMergeStatement(tableSF):
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()

    sql =f"""
    with t_props as (
    select 

        ROW_NUMBER() OVER (ORDER BY 1 ) seq
        ,t.id, t.sf_table, t.sf_fields, t.dwh_schema, t.dwh_table, t.dwh_fields, t.is_primary_key
        ,'merge into ' 
            || t.dwh_schema || '.' || t.dwh_table
            || ' t using ( select [param_using_statement] ) s on ( [param_key_merge] )'
            || ' when matched then update set [param_update_statement]'
            || ' when not matched then insert [param_insert_statement]' as rs
    from CONFIG_FROM_SF_TO_DWH t
    where sf_table = '{tableSF}'
    --and is_primary_key <> 1
    order by sf_fields
    )
    , on_statement as (
    select 't.'||dwh_fields || ' = s.' || dwh_fields as on_statement
    from t_props 
    where is_primary_key =1
    )

    , t_using_2 as (
    select 
        ':' || seq || ' as ' || dwh_fields as rs
        ,seq

    from t_props
    )
    ,using_statement as (
    select 
        LISTAGG(rs, ', ') WITHIN GROUP (ORDER BY seq) || ' from dual' as using_statement
    from t_using_2
    )
    ,insert_value_statement as 
    (
    select 
        '(' || LISTAGG(t.dwh_fields, ', ') WITHIN GROUP (ORDER BY seq) || ')' as insert_statement
        ,'values (' || LISTAGG('s.' || t.dwh_fields, ', ') WITHIN GROUP (ORDER BY seq) || ')' as insert_value_statement
    from t_props t
    )
    ,update_value_statement as 
    (
    select 
        LISTAGG(t.rs, ', ') WITHIN GROUP (ORDER BY 1)  as update_value_statement
        
    from(
        select 't.' || dwh_fields || ' = ' || 's.' || dwh_fields as rs
        from t_props
        where is_primary_key <> 1
    ) t
    )

    select 
        replace(
                replace(
                    replace 
                        (
                            replace
                                (
                                    t_props.rs,'[param_using_statement]',using_statement.using_statement    
                                ),'[param_key_merge]' ,on_statement.on_statement 
                        )
                        ,'[param_update_statement]',update_value_statement.update_value_statement
                )
                ,'[param_insert_statement]' ,insert_value_statement.insert_statement || insert_value_statement.insert_value_statement  
                )
        
    from t_props, insert_value_statement, using_statement, on_statement, update_value_statement
    where rownum = 1
    """

    cursor.execute(sql)

    sqlStatement = cursor.fetchall()

    connection.commit()

    cursor.close()
    connection.close()

    return sqlStatement[0][0]

def upsert(tableSF, values):
    connection = cx_Oracle.connect(cfg.username, cfg.password, cfg.dsn, encoding=cfg.encoding)
    cursor = connection.cursor()

    sql = getMergeStatement(tableSF)

    cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'")

    print("Total rows Upsert:", len(values))
    
    cursor.executemany(sql, values)

    connection.commit()

    cursor.close()
    connection.close()
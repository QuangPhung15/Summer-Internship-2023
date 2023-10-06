import SF_hook
import oracle_hook
import time
import property_SF as ppt

def main ():
    max_attempts = 3
    attempt = 0
    limit = ppt.rowLimitUpsert
    totalUpsertTime = 0
    while attempt <= max_attempts:
        try:
            token = oracle_hook.get_token_DB()
            sf_tables = oracle_hook.getDistinctSFtable()
            for tableSF in sf_tables:
                print("-------------------------------------------------------")
                print("Executing Upsert table:", tableSF)
                param = oracle_hook.getSelectForm(tableSF)

                start_time = time.time()
                rawData = SF_hook.getDataSF(token, param)
                end_time = time.time()
                execution_time = end_time - start_time
                print("Get Data time:", round(execution_time, 2), "seconds")
                print()

                cleanData = SF_hook.getCleanData(rawData)

                j = 0

                for i in range(len(cleanData)//limit):
                    start_time = time.time()
                    oracle_hook.upsert(tableSF, cleanData[limit*i:limit*(i+1)])
                    end_time = time.time()
                    execution_time = end_time - start_time
                    print((i + 1), "Upsert Database time:", round(execution_time, 2), "seconds")
                    print()
                    j = i + 1
                    totalUpsertTime += execution_time
                
                start_time = time.time()
                oracle_hook.upsert(tableSF, cleanData[limit*j:])
                end_time = time.time()
                execution_time = end_time - start_time
                print((j + 1), "Upsert Database time:", round(execution_time, 2), "seconds")
                print()

                totalUpsertTime += execution_time
                print("Total Upsert Time:", round(totalUpsertTime, 2), "seconds")
                print()

            print("Success!")
            break
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            attempt += 1
            token = SF_hook.createToken()
            oracle_hook.updateToken(token)
    else:
        # Executed if the maximum number of attempts is reached
        print("Maximum number of attempts reached. Exiting...")
        raise Exception()

main()
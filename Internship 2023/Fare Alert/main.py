import sabre_hook
import oracle_hook

max_attempts = 3
attempt = 1
while attempt <= max_attempts:
    try:
        token = oracle_hook.get_token_DB()
        data = sabre_hook.getPrice("HAN", "SGN", "3", "1", "1", "1", "2023-08-16", token, "2023-08-20")
        oracle_hook.insertPrice(data)
        print("Success!")
        break
    except Exception as e:
        print(f"Attempt {attempt} failed: {e}")
        attempt += 1
        newToken = sabre_hook.createSession()
        oracle_hook.updateToken(newToken)
else:
    # Executed if the maximum number of attempts is reached
    print("Maximum number of attempts reached. Exiting...")

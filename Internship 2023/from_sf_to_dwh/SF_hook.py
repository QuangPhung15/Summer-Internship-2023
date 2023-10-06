import requests
import json
from datetime import datetime
import property_SF as ppt

def escapeResponse(json_string):
    try:
        response_dict = json.loads(json_string)
    except:
        specialChar = [",", "]", "[", "{", "}", ":"]
        endChar = [",", "]", "}"]
        clean_str = ""

        count = 0
        i = 0
        while i < len(json_string):
            if json_string[i] == '"':
                count += 1

            if count == 2:
                k = i + 1
                while json_string[k] in specialChar:
                    k += 1
                    if k >= len(json_string):
                        clean_str += json_string[i:]
                        break
                else:
                    if k - i == 1:
                        count = 1
                        clean_str += "'"
                        i += 1
                    elif json_string[k] == '"':
                        count = 0
                        clean_str += '"'
                        i += 1
                    elif json_string[k].isnumeric():
                        while json_string[k].isnumeric():
                            k += 1
                        if json_string[k] in endChar:
                            count = 0
                            clean_str += '"'
                            i += 1
                    elif json_string[k] == "n":
                        try:
                            if json_string[k+1:k+4] == "ull" and (json_string[k+4] in endChar):
                                count = 0
                                clean_str += '"'
                                i += 1
                            else:
                                count = 1
                                clean_str += "'"
                                i += 1
                        except Exception as e:
                            if isinstance(e, IndexError):
                                count = 1
                                clean_str += "'"
                                i += 1
                    elif json_string[k] == "t":
                        try:
                            if json_string[k+1:k+4] == "rue" and (json_string[k+4] in endChar):
                                count = 0
                                clean_str += '"'
                                i += 1
                            else:
                                count = 1
                                clean_str += "'"
                                i += 1
                        except Exception as e:
                            if isinstance(e, IndexError):
                                count = 1
                                clean_str += "'"
                                i += 1
                    elif json_string[k] == "f":
                        try:
                            if json_string[k+1:k+5] == "alse" and (json_string[k+5] in endChar):
                                count = 0
                                clean_str += '"'
                                i += 1
                            else:
                                count = 1
                                clean_str += "'"
                                i += 1
                        except Exception as e:
                            if isinstance(e, IndexError):
                                count = 1
                                clean_str += "'"
                                i += 1
                    else:
                        count = 1
                        clean_str += "'"
                        i += 1
            else:
                clean_str += json_string[i]
                i += 1
            response_dict = json.loads(clean_str)
    
    return response_dict

def createToken():
    url = ppt.tokenURL
    payload = {
        'username': ppt.username,
        'password': ppt.password,
        'grant_type': ppt.grant_type,
        'client_id': ppt.client_id,
        'client_secret': ppt.client_secret
    }

    headers = {
        'Cookie': ppt.cookie
    }

    response = requests.post(url, headers=headers, data=payload)
    response_dict = json.loads(response.text)
    return response_dict["access_token"]


def getDataSF(token, sqlStr):
    tokenSF = "Bearer " + token
    url = ppt.dataURL + sqlStr

    headers = {
        'Authorization': tokenSF,
        'Cookie': ppt.cookie
    }

    response = requests.get(url, headers=headers)
    data = list()

    if response.ok:
        response_dict = escapeResponse(response.text)
        # response_dict = response.json()
        data.extend(response_dict.get("records", []))
    else:
        print("Error occurred while fetching data from Salesforce:", response.text)
        raise ValueError("Session expired or invalid")
    
    try:
        nextURL = response_dict["nextRecordsUrl"]
    
        while nextURL:
            url = ppt.urlSF + nextURL
            response = requests.get(url, headers=headers)

            if response.ok:
                response_dict = escapeResponse(response.text)
                # response_dict = response.json()
                data.extend(response_dict.get("records", []))
            else:
                print("Error occurred while fetching data from Salesforce:", response.text)
                raise ValueError("Session expired or invalid")
            
            try:
                nextURL = response_dict["nextRecordsUrl"]
            except:
                nextURL = ""
    except:
        pass
    
    rawData = list()
    for item in data:
        rawData.append(list(item.values())[1:])

    return rawData

def getCleanData(rawData):
    valueList = list()
    for item in rawData:
        cleanData = list()
        for data in item:
            if data == True or data == False:
                data = int(data)
                cleanData.append(data)
            elif type(data) == int or type(data) == float:
                cleanData.append(data)
            elif data and ".000+0000" in data and len(data) == 28:
                input_format = '%Y-%m-%dT%H:%M:%S.%f%z'
                output_format = '%Y-%m-%d %H:%M:%S'
                # Parse the input date string
                parsed_date = datetime.strptime(data, input_format)

                # Format the date as desired
                formatted_date = parsed_date.strftime(output_format)
                
                cleanDate = f"{formatted_date}"
                cleanData.append(cleanDate)
            else:
                cleanData.append(data)
        valueList.append(cleanData)
    
    return valueList
import requests
import json
import xmltodict

def createSession():
    url = "https://webservices.cert.platform.sabre.com/vn/websvc"
    payload = """
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Header>
            <wsse:Security xmlns:wsse="http://schemas.xmlsoap.org/ws/2002/12/secext">
                <wsse:UsernameToken>
                    <wsse:Username>85018</wsse:Username>
                    <wsse:Password>CDS1207</wsse:Password>
                    <Organization>VN</Organization>
                    <Domain>VN</Domain>
                    <SessionType>ATK</SessionType>
                </wsse:UsernameToken>
            </wsse:Security>
            <eb:MessageHeader xmlns:eb="http://www.ebxml.org/namespaces/messageHeader">
                <eb:From>
                    <eb:PartyId>999999</eb:PartyId>
                </eb:From>
                <eb:To>
                    <eb:PartyId>123123</eb:PartyId>
                </eb:To>
                <eb:CPAId>Sabre</eb:CPAId>
                <eb:ConversationId>92c515bf-ebfb-4b47-aebe-cb994738ef85</eb:ConversationId>
                <eb:Action>TokenCreateRQ</eb:Action>
                <eb:Service>Session</eb:Service>
                <eb:MessageData>
                    <eb:MessageId>92c515bf-ebfb-4b47-aebe-cb994738ef85</eb:MessageId>
                    <eb:Timestamp>2019-11-27T14:08:27.129Z</eb:Timestamp>
                    <eb:RefToMessageId>92c515bf-ebfb-4b47-aebe-cb994738ef85</eb:RefToMessageId>
                </eb:MessageData>
            </eb:MessageHeader>
        </soap:Header>
        <soap:Body>
            <TokenCreateRQ Version="1.0.0" xmlns="http://www.opentravel.org/OTA/2002/11"/>
        </soap:Body>
    </soap:Envelope>
    """
    headers = {
        'Content-Type': 'text/xml'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # Convert XML to OrderedDict
    data_dict = xmltodict.parse(response.text)

    # Convert OrderedDict to JSON
    json_data = json.dumps(data_dict)

    json_data = json.loads(json_data)
    
    token = json_data["soap-env:Envelope"]["soap-env:Header"]["wsse:Security"]["wsse:BinarySecurityToken"]["#text"]

    return token
    

def getPrice(org, des, numPassengers, adult, children, infant, departDate, token, returnDate = None):
    url = "https://webservices.cert.platform.sabre.com/vn/websvc"
    header = f"""
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Header>
            <ns4:MessageHeader xmlns:ns8="http://www.opentravel.org/OTA/2003/05" xmlns:ns7="http://www.w3.org/2000/09/xmldsig#" xmlns:ns6="http://schemas.xmlsoap.org/ws/2002/12/secext" xmlns:ns5="http://www.w3.org/1999/xlink" xmlns:ns4="http://www.ebxml.org/namespaces/messageHeader">
                <ns4:From>
                    <ns4:PartyId>99999</ns4:PartyId>
                </ns4:From>
                <ns4:To>
                    <ns4:PartyId>123123</ns4:PartyId>
                </ns4:To>
                <ns4:CPAId>B6</ns4:CPAId>
                <ns4:ConversationId>VietnamMetaTraffic</ns4:ConversationId>
                <ns4:Service>Air Shopping Service</ns4:Service>
                <ns4:Action>AdvancedAirShoppingRQ</ns4:Action>
                <ns4:MessageData>
                    <ns4:MessageId>mid:2022-06-22T12:28:53@sabre.com</ns4:MessageId>
                    <ns4:Timestamp>2022-06-22T12:28:53</ns4:Timestamp>
                </ns4:MessageData>
            </ns4:MessageHeader>
            <ns6:Security xmlns:ns8="http://www.opentravel.org/OTA/2003/05" xmlns:ns7="http://www.w3.org/2000/09/xmldsig#" xmlns:ns6="http://schemas.xmlsoap.org/ws/2002/12/secext" xmlns:ns5="http://www.w3.org/1999/xlink" xmlns:ns4="http://www.ebxml.org/namespaces/messageHeader">
                <ns6:BinarySecurityToken>{token}</ns6:BinarySecurityToken>
            </ns6:Security>
        </soap:Header>
        <soap:Body>
            <OTA_AirLowFareSearchRQ xmlns:xs="http://www.w3.org/2001/XMLSchema" Target="Production" Version="6.7.1" xmlns="http://www.opentravel.org/OTA/2003/05" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <POS>
                <Source AccountingCode="CW" PersonalCityCode="GXW" PseudoCityCode="GXW">
                    <RequestorID Type="0.AAA.X" ID="REQ.ID">
                        <CompanyName Code="SSW"/>
                    </RequestorID>
                </Source>
            </POS>
    """
    if returnDate == None:
        body = f"""
        <OriginDestinationInformation RPH="1">
            <DepartureDateTime>{departDate}T00:00:00</DepartureDateTime>
            <OriginLocation LocationCode="{org}"/>
            <DestinationLocation LocationCode="{des}"/>
            <TPA_Extensions>				
                <SegmentType Code="O"/>
            </TPA_Extensions>
        </OriginDestinationInformation>
        """
    else:
        body = f"""
        <OriginDestinationInformation RPH="1">
            <DepartureDateTime>{departDate}T00:00:00</DepartureDateTime>
            <OriginLocation LocationCode="{org}"/>
            <DestinationLocation LocationCode="{des}"/>
            <TPA_Extensions>				
                <SegmentType Code="O"/>
            </TPA_Extensions>
        </OriginDestinationInformation>
        <OriginDestinationInformation RPH="1">
            <DepartureDateTime>{returnDate}T00:00:00</DepartureDateTime>
            <OriginLocation LocationCode="{des}"/>
            <DestinationLocation LocationCode="{org}"/>
            <TPA_Extensions>				
                <SegmentType Code="O"/>
            </TPA_Extensions>
        </OriginDestinationInformation>
        """

    closing = f"""
    <TravelPreferences>
                <TPA_Extensions>
                </TPA_Extensions>
            </TravelPreferences>
            <TravelerInfoSummary>
                <SeatsRequested>{numPassengers}</SeatsRequested>
                <AirTravelerAvail>
                    <PassengerTypeQuantity Code="ADT" Quantity="{adult}"/>
                    <PassengerTypeQuantity Code="CHD" Quantity="{children}"/>
                    <PassengerTypeQuantity Code="INF" Quantity="{infant}"/>
                </AirTravelerAvail>
                <PriceRequestInformation>
                    <TPA_Extensions>
                    </TPA_Extensions>
                </PriceRequestInformation>
            </TravelerInfoSummary>
            <TPA_Extensions>
                <IntelliSellTransaction Debug="0">
                    <RequestType Name="CACHE"/>
                    <ServiceTag Name="VNMETA"/>		 
                </IntelliSellTransaction>
            <SplitTaxes ByLeg = "true" ByFareComponent = "true"/>
            </TPA_Extensions>
            </OTA_AirLowFareSearchRQ>
        </soap:Body>
    </soap:Envelope>
    """
    payload = header + body + closing

    headers = {
        'Content-Type': 'text/xml'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # Convert XML to OrderedDict
    data_dict = xmltodict.parse(response.text)

    # Convert OrderedDict to JSON
    json_data = json.dumps(data_dict)

    json_data = json.loads(json_data)
    
    flights = json_data["SOAP-ENV:Envelope"]["SOAP-ENV:Body"]["OTA_AirLowFareSearchRS"]["PricedItineraries"]["PricedItinerary"]
    data = []
    oneWay = []
    roundTrip = []
    for item in flights:
        route_type = item["AirItinerary"]["@DirectionInd"]

        if returnDate == None:
            segments = item["AirItinerary"]["OriginDestinationOptions"]["OriginDestinationOption"]["FlightSegment"]
            adt_return_price = None
            chd_return_price = None
            inf_return_price = None
            total_return_price = None
            
            if type(segments) == dict:
                departDate = segments["@DepartureDateTime"]
                if departDate not in oneWay:
                    oneWay.append(departDate)
                    currency = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@CurrencyCode"]
                    
                    if int(adult) > 0 and int(children) == 0 and int(infant) == 0:
                        adt_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        chd_depart_price = None
                        inf_depart_price = None
                        total_depart_price = int(adt_depart_price)
                    elif int(adult) == 0 and int(children) > 0 and int(infant) == 0:
                        adt_depart_price = None
                        chd_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        inf_depart_price = None
                        total_depart_price = int(chd_depart_price)
                    elif int(adult) == 0 and int(children) == 0 and int(infant) > 0:
                        adt_depart_price = None
                        chd_depart_price = None
                        inf_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        total_depart_price = int(inf_depart_price)
                    elif int(adult) > 0 and int(children) > 0 and int(infant) == 0:
                        adt_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        chd_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        inf_depart_price = None
                        total_depart_price = int(adt_depart_price) + int (chd_depart_price)
                    elif int(adult) > 0 and int(children) == 0 and int(infant) > 0:
                        adt_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        chd_depart_price = None
                        inf_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        total_depart_price = int(adt_depart_price) + int (inf_depart_price)
                    elif int(adult) == 0 and int(children) > 0 and int(infant) > 0:
                        adt_depart_price = None
                        chd_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        inf_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        total_depart_price = int(chd_depart_price) + int (inf_depart_price)
                    else:
                        adt_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        chd_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        inf_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][2]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"]["TotalFare"]["@Amount"]
                        total_depart_price = int(adt_depart_price) + int(chd_depart_price) + int (inf_depart_price)
                    
                    valueList = [org, des, departDate, returnDate, adt_depart_price, adt_return_price, currency, route_type, numPassengers, adult, children, infant, chd_depart_price, chd_return_price, inf_depart_price, inf_return_price, total_depart_price, total_return_price]
                    data.append(valueList)
        else:
            segment1 = item["AirItinerary"]["OriginDestinationOptions"]["OriginDestinationOption"][0]["FlightSegment"]
            segment2 = item["AirItinerary"]["OriginDestinationOptions"]["OriginDestinationOption"][1]["FlightSegment"]
            if type(segment1) == dict and type(segment2) == dict:
                departDate = segment1["@DepartureDateTime"]
                returnDate = segment2["@DepartureDateTime"]
                multiSeg = [departDate, returnDate]
                if multiSeg not in roundTrip:
                    roundTrip.append(multiSeg)
                    currency = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@CurrencyCode"]
                    
                    if int(adult) > 0 and int(children) == 0 and int(infant) == 0:
                        adt_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        adt_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        chd_depart_price = None
                        chd_return_price = None
                        inf_depart_price = None
                        inf_depart_price = None
                        total_depart_price = int(adt_depart_price)
                        total_return_price = int(adt_return_price)
                    elif int(adult) == 0 and int(children) > 0 and int(infant) == 0:
                        adt_depart_price = None
                        adt_return_price = None
                        chd_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        chd_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        inf_depart_price = None
                        inf_return_price = None
                        total_depart_price = int(chd_depart_price)
                        total_return_price = int(chd_return_price)
                    elif int(adult) == 0 and int(children) == 0 and int(infant) > 0:
                        adt_depart_price = None
                        adt_return_price = None
                        chd_depart_price = None
                        chd_return_price = None
                        inf_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        inf_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        total_depart_price = int(inf_depart_price)
                        total_return_price = int(inf_return_price)
                    elif int(adult) > 0 and int(children) > 0 and int(infant) == 0:
                        adt_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        adt_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        chd_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        chd_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        inf_depart_price = None
                        inf_return_price = None
                        total_depart_price = int(adt_depart_price) + int(chd_depart_price)
                        total_return_price = int(adt_return_price) + int(chd_return_price)
                    elif int(adult) > 0 and int(children) == 0 and int(infant) > 0:
                        adt_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        adt_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        chd_depart_price = None
                        chd_return_price = None
                        inf_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        inf_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        total_depart_price = int(adt_depart_price) + int(inf_depart_price)
                        total_return_price = int(adt_return_price) + int(inf_return_price)
                    elif int(adult) == 0 and int(children) > 0 and int(infant) > 0:
                        adt_depart_price = None
                        adt_return_price = None
                        chd_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        chd_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        inf_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        inf_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        total_depart_price = int(chd_depart_price) + int(inf_depart_price)
                        total_return_price = int(chd_return_price) + int(inf_return_price)
                    else:
                        adt_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        adt_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][0]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        chd_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        chd_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][1]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        inf_depart_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][2]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][0]["TotalFare"]["@Amount"]
                        inf_return_price = item["AirItineraryPricingInfo"]["PTC_FareBreakdowns"]["PTC_FareBreakdown"][2]["PassengerFare"]["TPA_Extensions"]["Legs"]["Leg"][1]["TotalFare"]["@Amount"]
                        total_depart_price = int(adt_depart_price) + int(chd_depart_price) + int(inf_depart_price)
                        total_return_price = int(adt_return_price) + int(chd_return_price) + int(inf_return_price)
                    
                    valueList = [org, des, departDate, returnDate, adt_depart_price, adt_return_price, currency, route_type, numPassengers, adult, children, infant, chd_depart_price, chd_return_price, inf_depart_price, inf_return_price, total_depart_price, total_return_price]
                    data.append(valueList)
        
    return data
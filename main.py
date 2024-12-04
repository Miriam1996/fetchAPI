from curses.ascii import isalnum
import datetime
import re
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI()
memo = {}

class ReceiptsItem(BaseModel):
    shortDescription: str
    price: str
class Receipts(BaseModel):
    retailer: str
    purchaseDate: str
    purchaseTime: str
    items: List[ReceiptsItem]
    total: str

@app.get("/receipts/{id}/points", status_code=200)
def read_item(id):
    if id in memo:
        return {"points" : memo.get(id)}
    else:
        raise HTTPException(status_code = 404, detail = "No receipt found for that id")

# adding points
def getPointsForTotal(total):
    totalArray = total.split('.')
    if len(totalArray) > 1:
        total = int(totalArray[1])
    else:
        total = int(totalArray[0])
    points = 0
    if total == 0:
        points += 50
    if total%25 ==0:
        points += 25
    return points

#len of trim description is multiple of 3
def parseItems(items: List[ReceiptsItem]): # type: ignore
    points = 0
    points += int(len(items)/2) * 5
    for item in items:
        trimmedDescription = item.shortDescription.strip()
        if (len(trimmedDescription)% 3 ==0):
            points += int(float(item.price) * .2 +1)
    return points
def parseRetailer(retailer):
    points = 0
    for letter in retailer:
        if isalnum(letter):
            points += 1
    return points
def isValidTime(purchaseTime):
  
    regex = "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    p =re.compile(regex)
    m = re.search(p, purchaseTime)
    if not  m == None:
        return True
    else:
        return False
def isValidDate(purchaseDate):
    try:
        datetime.datetime.strptime(purchaseDate, "%Y-%m-%d")
        return True
    except:
        return False
@app.post("/receipts/process", status_code=200)
def update_item(receipt: Receipts):
    points  = 0
    if receipt:
        try:
            if not isValidTime(receipt.purchaseTime) or not isValidDate(receipt.purchaseDate):
                raise HTTPException(status_code=400, detail="The receipt is invalid")
            # handle & not alpha numeric need to ebvaluater
            points += parseRetailer(receipt.retailer)
            #get cents value as string and parse to int
            points+= getPointsForTotal(receipt.total)
            points += parseItems(receipt.items)
            day =int(receipt.purchaseDate.split("-")[2])
            #odd day add 6 points
            if day% 2 == 1:
                points+=6
            #parse datetime too
            time= receipt.purchaseTime.split(":")
            hour = int(time[0])
            if hour >= 14 and hour <=16:
                points+=10
        except ValueError as e:
            raise HTTPException(status_code=400, detail="The receipt is invalid")
        id = str(uuid.uuid4())
        memo[id] = points
        return {"id" : id}







from time import sleep
import requests
from html.parser import HTMLParser
import json
import smtplib
from pymongo import MongoClient
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
load_dotenv()


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.ids = []

    def handle_starttag(self, tag, attrs):
        # gets the internal ID
        if tag == "a":
            for t in enumerate(attrs):
                if t[1][0] == "aria-labelledby":
                    id = t[1][1][5:]
                    self.ids.append(id)


def get_ids_from_html():
    url = "https://streeteasy.com/for-rent/nyc/area:117,158,113,116,108,109,162,107,106,157"
    url2 = "https://streeteasy.com/for-rent/nyc/area:117,158,113,116,108,109,162,107,106,157?page=2"
    url3 = "https://streeteasy.com/for-rent/nyc/area:117,158,113,116,108,109,162,107,106,157?page=3"

    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
        'Cookie': '_actor=eyJpZCI6ImtGMkxzS25oVkZ3cmlldUdpWk9Ra3c9PSJ9--78f70167626768f220014112fe9fa8fca408184c; _se_t=9823828b-3fcb-4e09-8cf0-b5041ac68403; _ses=WUpoSjIxblg1d2RKUU1lVTJ0T05iTi9KQkY4MXB4V1JxdmlCUlhkTnJHMk1OZVR2N1VpaFkzMjkvYVpmeUhIeVlOQmdDTDFaVmZ6SS9GTlJVWXdUK0VJYVVTeTJKT1c2RXl4VVdvSC9EMncxUEx5V2RCSStncVlTWmhLRm9ESWdpSkJkbnUydHdxVExpcC93b1hvRXZ4RFJ4VzhtSG9UVEtoK3pycVpzWS9mdWlxWFdJazYwS0FZcFpWR0phSkRJV0EySkYydUpqYmxwQTFzUUh0YW91akRtM3V5UjlnRXA1aE41aGIvK0E4OFlxR1kwOHptUGYrTW10NDVzL2cxUnlOYk11R0pGV3A3UC9ucWZiNlF2U2Z1dFZTZGliSGF3aGpaSTBBdzZkZVZURkdHSXA2VmxSdTB6aHBwTzFIUGFvS29RYUd4Q2srbzhBaEtveWlvL1FNQWdRb05OMW5LZUduYmNweTVxbUp3UUhwbVgveElPWDIrd1FtdldWUEFvcUExUGlvSXVZbkh6ck1IQ1JJM242NlVVTEdRblFrWHBQMzJEMHFRcTdBZjFNR2c1Ty9JSjM3dHZiaDY5WTgva0pIRGJ4SVludE01b2JRbW01ZDVobDFsUVBzTWNHRUJicWZlL0k5U3IrSTl1U25aTzdnaHAxL1dZaXc0MFVQWWlzZ0FlNkw2b3NYeExMcHZhcS8vTE0rUUYvUTI5YUViOE9NQWIwdzY0VGovY0JFM3VFcjhCbXBIenRmVzFTUnZULS1Ob3Qvdm5IcWFIVVI0eHVCN0pZajZBPT0%3D--29d2fc67a399e17bb0d39efe39570026acba1bfd; last_search_tab=rentals; recent_searches=%5B%2227967921%7C1658948903%22%2C%223157846%7C1658873834%22%5D; se_lsa=2022-07-27+15%3A08%3A23+-0400'
    }

    p1 = requests.get(url, headers=headers, data=payload)
    sleep(30)
    p2 = requests.get(url2, headers=headers, data=payload)
    sleep(30)
    p3 = requests.get(url3, headers=headers, data=payload)

    parser1 = MyHTMLParser()
    parser2 = MyHTMLParser()
    parser3 = MyHTMLParser()

    parser1.feed(p1.text)
    parser2.feed(p2.text)
    parser3.feed(p3.text)

    ids = parser1.ids + parser2.ids + parser3.ids

    return ids


def gqlRequest(ids):
    url = "https://api-internal.streeteasy.com/graphql"

    payload = json.dumps({
        "operationName": "rentals",
        "variables": {
            "ids": ids
        },
        "query": "query rentals($ids: [ID!]!) {\n  rentals(ids: $ids) {\n    id\n       title_with_unit\n    listed_price\n    anyrooms\n    bedrooms\n    bathrooms\n   available_at\n contacts {name email phone}\n url\n images(max_count: 6) {url(width: 50, height: 100, quality: 100)} \n status \n source\n    __typename\n  }\n}\n"
    })
    headers = {
        'authority': 'api-internal.streeteasy.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://streeteasy.com',
        'os': 'web',
        'referer': 'https://streeteasy.com/',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'Cookie': '_ses=NVBBYVZhcklTQlg3SGxOY3BwWU9DSjFmcnBIZ0ZGVTVSelJieEFsdjNtUzRTNFZMQTEwczVGZUI2ZzNqWXZFYkE0aFVkQ0lFblNOY3RKSDRkMnBsdm0rY3Z2M0Y0VEFMSmZYTmEzUlRJTGVKOWxJZ2xtazhsZ1MxMzY4dkErTHpqaFJ6SE9RMFQ5TVFiL1hyY0Z0MCtrbzcrcnBLQlZocUhTM2dwSjcvL1JCRyt3cHZUNm1VY1E0S0F2b3Nmbmx3ZFR2TXZwYkpZMFlxV3hsR0VpUXdpenFCUm9INDlrYlpMVFdwSTFLWUcxekVmNUF2SUU4czl3eVV1dG9uUTljTTZ5V0UxSU9EWmYvd3RlVjNzSG9tMVdmVnBacUZ5disrZ1d3bm5uS0pyeFZncWc4V0RnT1ZrNVFZZm9uSmdxSFQrSEthaWRML28xZ21xcHdOV3p0MzM4UkRROXEvSnk5WmtDZWRmYjBYeW5hVkF5Y2JTSytwb1FpZEFEcFA3UVoxTzd6SVpSS2I4Ri84VXZDQk1zYm1FVnFVdUJzSGFIRmo2KzA5T09hMGhYOGhPQnhhOWg3THd1bURSUVN3VjZ6OGF1Tjh0U2MzbU9jaDZsS3BjQzYydDB2Wm14N2xtZFZSTnBhaDNHZWN0UUhRTUtlZWVjNXBkNGxEZWdMc3ExVzBwYkxyQTB2M2loYUEyU2Q0Ylc3ZjRUd2RWQ3FVNk5JbG1oLzFVNEpqU0RLV084S1o4NnBCQmJBalVrSUM0UzdoLS1TUktQSXZNd3hCcURKa3h5ZW5Uc0V3PT0%3D--8a37681795aaa795f1ee6b176585a92034cefb91; _se_t=b324d2e5-a843-4809-a9cd-f295a09cb5fb'
    }

    response = requests.post(url, headers=headers, data=payload)
    rentals = response.json()["data"]["rentals"]
    for r in rentals:
        bedrooms = 1 if r["bedrooms"] < 1 else r["bedrooms"]
        price_per_person = r["listed_price"] / bedrooms
        r["price_per_person"] = price_per_person
    return rentals


def send_email(template):
    me = "boristopalov1@gmail.com"
    try:
        server = smtplib.SMTP('smtp.sendgrid.net', 587)
        server.ehlo()
        user = "apikey"
        pw = os.getenv('KEY')
        server.login(user, pw)

        sent_from = "<boristopalov1@gmail.com>"
        to = ['<boristopalov1@gmail.com>']
        subject = 'New StreetEasy Listings'
        email_text = """From: %s \nTo: %s \nSubject: %s \n%s
        """ % (sent_from, ", ".join(to), subject, template)

        email = MIMEText(email_text, "html")  # convert to HTML
        email["From"] = "boristopalov1@gmail.com"
        email["To"] = ["boristopalov1@gmail.com"]
        email["Subject"] = "New StreetEasy Listings"

        server.sendmail(sent_from, to, email.as_string())
        print("Email sent")
    except Exception as e:
        print(e.with_traceback())


def buildTemplate(rentals):
    html = ""
    for r in rentals:
        if r["price_per_person"] > 2250:
            continue
        contact = r["contacts"][0]
        images = r["images"]
        images_html = ""
        for img in images:
            single_img = f"""
              <div>
                <img src={img["url"]} width="200" height="200">
              </div>
              """
            images_html += single_img

        template = f"""
      <div>
        <a href={r["url"]}>
          <h2>{r["title_with_unit"]}</h2>
        </a>
        <h5>Bedrooms: ${int(r["bedrooms"])} </h5>
        <h5>Bathrooms: ${int(r["bathrooms"])} </h5>
        <h5>Total Rooms With Living Room + Others: ${int(r["anyrooms"])} </h5>
        <h5>Price: ${r["listed_price"]} </h5>
        <h5>Price per person: ${r["price_per_person"]}  </h5>
        <h5>Available on: {str(r["available_at"])[:10]}</h5>
        <br>
        <h5>Listed by: {contact["name"]} </h5>
        <h6>Email: {contact["email"]}</h6>
        <h6>Phone: {contact["phone"]}</h6>
        <br>
        <h4>Images</h4>
        <div style="display: flex; flex-wrap: wrap">
          {images_html}
        </div>
      </div>
    """
        html += template
    return html


def main():
    client = MongoClient("localhost", 27017)  # connect to mongo db
    db = client["streeteasy"]
    collection = db["rentals"]

    ids = get_ids_from_html()  # parse html for listing ids
    # list of id's already in the database
    old_ids = list(collection.find({"id": {'$in': ids}}, {'_id': 0, "id": 1}))
    print("old ids:", old_ids)
    # we only care about id's not in the database
    new_ids = [id for id in ids if id not in old_ids]
    print("new ids:", new_ids)

    rentals = gqlRequest(new_ids)
    print("rentals", rentals)
    # insert all the new rentals into the database
    if len(rentals) > 0:
        collection.insert_many(rentals)
        html_email_template = buildTemplate(rentals)
        print("template", html_email_template)
        send_email(html_email_template)


if __name__ == "__main__":
    main()

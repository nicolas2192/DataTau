# Scrapes https://datatau.net/ and sends to 5 articles by email (default=5). Stay ahead of the game!

# Imports
# import pandas as pd
import bs4 as bs
import requests
import smtplib
from email.message import EmailMessage

# Constants
URL = "https://datatau.net"
USER = "" # email address used to send the email "hello@gmail.com" must be a gmail account
PASS =  "" # password "pass123"
RECP = [] # distribution list ["ex1@gmail.com", "ex2@outlook.com"]
ER_RECP = [] # errors distribution list ["ex1@gmail.com", "ex2@outlook.com"]
NUM_ART = 5 # Number of articles to add to the list. Max 30


def get_data(url):
    """
    Parses DataTau.net and returns a list with the first 30 articles. 
    """
    r = requests.get(url)
    
    # Checks connection to DataTau
    if r.status_code != 200:
        print(f"Connection error. DataTau.net is unreachable. Error code: {r.status_code}")
        return r.status_code
    
    else:
        soup = bs.BeautifulSoup(r.text, "lxml")
        t = soup.find("table", {"class": "itemlist"}) # gets main table
        r = t.find_all("tr", {"class": "athing"}) # parses main table, each row will be an item in the list
        
        # Extracts title and link from each item.
        to_df = []
        for i in r:
            '''
            Example:
            title = (['Top 5 Examples of E-commerce Personalization Done Right', '(iunera.com)'],
            link = 'https://www.iunera.com/kraken/big-data-science-intelligence/')
            '''
            item = i.find("td", {"class": "title"}, align=False)
            title = item.text.strip("\n").split("\n ")
            link = item.find("a", {"class": "storylink"}).get("href")

            # Adding all titles and links to a unique list
            title.append(link)
            to_df.append(title)
            
        print("DataTau.net was successfully parsed")
            
        return to_df


# def generate_df(to_df):
#     """
#     Loads previously parsed data into a df. 
#     """
#     df = pd.DataFrame(to_df, columns=["Title", "Webpage", "Link"])
#     df.Webpage = df.Webpage.apply(lambda x: x.lstrip("(").rstrip(")"))
#     return df


def create_html_body(lst, num=5):
    """
    Creates HTML string, num parameter sets how many articles will be added to the email. Max 30. 
    """
    num = 30 if num > 30 else num
    
    html_msg = ""
    for i in range(num):
        wp = lst[i][1][:-(lst[i][1][::-1].index("."))-1].lstrip("(") # removes domain and (); (medium.com)-> medium
        art = f'''
        <p><strong>{i+1}.&nbsp;&nbsp;</strong>
        <a title="article" href="{lst[i][2]}" target="_blank" rel="noopener">{lst[i][0]}</a>
        &nbsp;&nbsp; - &nbsp;&nbsp;<span style="color: #757575;">{wp}</span>
        </p>
        '''
        
        html_msg = html_msg + art
        
    return html_msg


def create_html_msg(html_body):
    """
    Takes the previously generated HTML string and places it within a bigger HTML string 
    which will be used as the email's body. 
    """
    
    full_msg = f'''
    <h4 style="color: #212121;">Hello, good-looking data scientist 😍</h4>
    <h4 style="color: #212121;">Here you have today's top 5 articles!</h4>
    <p>&nbsp;</p>
    {html_body}
    <p>&nbsp;</p>
    <p><span style="color: #000000;">Don't miss the full list at&nbsp;<a title="datatau" href="https://datatau.net/" target="_blank" rel="noopener">DataTau.net</a></span></p>
    <p>&nbsp;</p>
    <p>Sent with ❤️ by Nico</p>
    <p>&nbsp;</p>
    '''
    return full_msg


def send_email(html_msg, user=USER, password=PASS, recepient=RECP):
    """
    Connects to the gmail server and sends data by email
    """
    
    msg = EmailMessage() 
    msg["Subject"] = "This is what everyone is talking about!"
    msg["From"] = user
    msg["To"] = ", ".join(recepient)
    msg.set_content("This message cannot be rendered. Sorry!")
    msg.add_alternative(html_msg, subtype='html')
    
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  # setting server and port
    server.login(user, password)  # login
    server.send_message(msg)  # sending email
    server.quit()  # terminates connection
    
    print("Message sent!")
    return None


def error_notification(articles, user=USER, password=PASS, recepient=ER_RECP):
    """
    Connects to the gmail server and sends error report by email
    """
    
    msg = EmailMessage() 
    msg["Subject"] = "⚠️ DataTau.net is unreachable"
    msg["From"] = user
    msg["To"] = ", ".join(recepient)
    msg.set_content(f"Status code error {articles}")
    
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  # setting server and port	
    server.login(user, password)  # login
    server.send_message(msg)  # sending email
    server.quit()  # terminates connection
    
    print("Error message sent!")
    return None


def main():
    articles = get_data(URL)

    if articles != 200:
        html_body_msg = create_html_body(articles, num=NUM_ART)
        full_html_msg = create_html_msg(html_body_msg)
        send_email(full_html_msg)
    else:
        error_notification(articles)


if __name__ == "__main__":
    main()


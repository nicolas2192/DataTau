# Scrapes https://datatau.net/ and sends top articles by email. Stay ahead of the game!

# Imports
# import pandas as pd
import bs4 as bs
import requests
import smtplib
import os
import csv
from email.message import EmailMessage

# Constants
URL = "https://datatau.net"
USER = "" # email address used to send the email "hello@gmail.com" must be a gmail account
PASS =  "" # password "pass123"
RECP = "data/recipients.csv" # distribution list file path. Default: data/recipients.csv
ER_RECP = [""] # errors distribution list ["ex1@gmail.com", "ex2@outlook.com"]
NUM_ART = 10 # Number of articles to add to the list. Max 30


def get_data(url):
    """
    Parses DataTau.net and returns a list with the first 30 articles. 
    """
    r = requests.get(url)
    
    # Checks connection to DataTau
    if r.status_code != 200:
        
        # If Datatau.net were unreachable, an error message will notify emails set in the ER_RECP constant.
        print(f"Connection error. DataTau.net is unreachable. Error code: {r.status_code}")
        error_notification(r.status_code, user=USER, password=PASS, recepient=ER_RECP)
        exit()
        return None
    
    else:
        # If connection was successful, parses Datatau.net
        soup = bs.BeautifulSoup(r.text, "lxml")
        t = soup.find("table", {"class": "itemlist"}) # gets main table
        r = t.find_all("tr", {"class": "athing"}) # parses main table, each row will be an item in the list
        
        # Extracts title and link from each item.
        parsing = []
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
            title.append(link) # ["Title", "Webpage name", "URL"]
            parsing.append(title) # [["Title", "Webpage name", "URL"], ["Title", "Webpage name", "URL"] , ...]
            
        print("DataTau.net was successfully parsed")
            
        return parsing


def make_recipients_csv(rp_path: str):
    """
    :param rp_path: recipient.csv path. Here will be place the recipients list file.
    :return: Creates new recipients file with its header and two examples. Then, stops the script.
    """
    with open(rp_path, "w") as new_file:
        data_csv = [["Recipient"], ["new_recipient1@example.com"], ["new_recipient2@example.com"]]
        csv_writer = csv.writer(new_file)
        for line in data_csv:
            csv_writer.writerow(line)

        print(f"New recipients.csv file was added at the following path: {rp_path}\n"
              f"Please, add some recipients before running the script again.")
    exit()


def recipients_list(rp_path: str):
    """
    :param rp_path: recipients.csv file
    :return: a list comprising all recipients in the recipients.csv file [rep, rep2, rep3 ...]
    """
    # if recipients.csv file does not exist, it will be created.
    if not os.path.exists(rp_path):
        make_recipients_csv(rp_path)
    else:
        with open(rp_path, "r") as f:
            csv_reader = csv.reader(f)
            next(csv_reader)
            rp_list = [line[0] for line in csv_reader]
            f.close()
            
            # Checking if generic recipients.csv file was updated with real email addresses
            if rp_list[0] == "new_recipient1@example.com":
                print("Please, update recipients.csv file with real email addresses\n"
                      "Nothing was sent")
                exit()
            else:
                return rp_list


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
    Takes the previously generated HTML string (list of relevant links) and places it within a bigger HTML string 
    which will be used as the email's body. 
    """
    
    full_msg = f'''
    <h4 style="color: #212121;">Hello, good-looking data scientist 😏</h4>
    <h4 style="color: #212121;">Here you have today's top articles!</h4>
    <p>&nbsp;</p>
    {html_body}
    <p>&nbsp;</p>
    <p><span style="color: #000000;">Don't miss the full list at&nbsp;<a title="datatau" href="https://datatau.net/" target="_blank" rel="noopener">DataTau.net</a></span></p>
    <p>&nbsp;</p>
    <p>Sent with ❤️ by Nico</p>
    <p>&nbsp;</p>
    '''
    return full_msg


def recipients_string(rp=RECP):
    """
    Loads recipients in the recipients.csv file into a list, then creates a string of email addresses from it.
    ["ex1@gmail.com", "ex2@outlook.com"] -> "ex1@gmail.com, ex2@outlook.com"
    """

    # If recipients.csv does not exist, a generic file will be created before terminating the script.
    distribution_list = recipients_list(rp)
    if distribution_list is None:
        exit()
    else:
        rp_string = ", ".join(distribution_list)
        return rp_string


def send_email(html_msg, recipients, user=USER, password=PASS):
    """
    Connects to the gmail server and sends newsletter by email
    """
    
    msg = EmailMessage() 
    msg["Subject"] = "📡 This is what everyone is talking about!"
    msg["From"] = user
    msg["To"] = ""
    msg["BCC"] = recipients
    msg.set_content("This message cannot be rendered. Sorry!")
    msg.add_alternative(html_msg, subtype='html')
    
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  # setting server and port
    server.login(user, password)  # login
    server.send_message(msg)  # sending email
    server.quit()  # terminates connection
    
    print("Message sent!")
    return None


def error_notification(articles, user=USER, password=PASS, recipient=ER_RECP):
    """
    Connects to the gmail server and sends error report
    """
    
    msg = EmailMessage() 
    msg["Subject"] = "⚠️ DataTau.net is unreachable"
    msg["From"] = user
    msg["To"] = ", ".join(recipient)
    msg.set_content(f"Status code error {articles}")
    
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  # setting server and port
    server.login(user, password)  # login
    server.send_message(msg)  # sending email
    server.quit()  # terminates the connection
    
    print("Error message sent!")
    return None


def main():
    articles = get_data(URL)
    html_body_msg = create_html_body(articles, num=NUM_ART)
    full_html_msg = create_html_msg(html_body_msg)
    rp_string = recipients_string(RECP)
    send_email(full_html_msg, rp_string)


if __name__ == "__main__":
    main()


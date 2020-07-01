import requests
from bs4 import BeautifulSoup as soup
import os
import time
import pandas as pd


# Configuaion
VERBOSE = True                  # If True, the outputs of each block will be printed
OUTPUT_DIRECTORY = "storage/input/JACS"       # The directory to store pdf downloaded
STARTING_PAGE = 0
ENDING_PAGE = 2555                    # Number of result pages to be scaped.
SAVING_INFO_FREQ = 1            # Save updated info table every N result pages 
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
if not os.path.exists(os.path.join(OUTPUT_DIRECTORY,"Info.csv")):
    pd.DataFrame(list()).to_csv(os.path.join(OUTPUT_DIRECTORY,"Info.csv"))       # Load from Info.csv (if not exist, make an empty list)  
info_table = pd.read_csv(os.path.join(OUTPUT_DIRECTORY,"Info.csv"))

# Gather Information of each paper
def gather_information(web_page):
    """
    Extract the following information from the webpage including title, authors, journal,
    volume, issue, SI pdf filename.
        @PARAMS:
            web_page: BeautifulSoup object, containing information from the DOI of papers
        @RETURNS:
            pd.DataFrame of a dictionary, with information mentioned above
            bool, indicating whether the paper title includes "total synthesis"
    """
    title = web_page.find_all("span",{"class":"hlFld-Title"})[0].text
    if title.lower().find("total synthesis") == -1: return None, True
    authors = ""
    for _ in web_page.find_all("span",{"class":"hlFld-ContribAuthor"}):
        authors += _.text + ";"                                                  # Get all authors       
    journal = web_page.find_all("span",{"class":"cit-title"})[0].text            # Get journal name
    year = web_page.find_all("span",{"class":"cit-year-info"})[0].text           # Get publication year
    issue = web_page.find_all("span",{"class":"cit-issue"})[0].text[2:]          # Get issue
    volume = web_page.find_all("span",{"class":"cit-volume"})[0].text[2:]        # Get volume
    return pd.DataFrame({"Title":title,"Authors":authors,"Journal":journal,
                         "Year":year,"Volume":volume,"Issue":issue,"PDFName":""}
                        ,index=[0],columns=['Title','Authors','Journal','Volume',
                                            'Issue','PDFName']), False           # Compile everything into a pd.df

    
    



### Scraping each result page
for page in range(ENDING_PAGE - STARTING_PAGE):
    PARENT_URL = "https://pubs.acs.org/action/doSearch?AllField=\
        total+synthesis&SeriesKey=jacsat&startPage=%i&pageSize=20"%page          # The URL of the searching results

    ### Extract html from the URL
    r = requests.get(PARENT_URL)
    if VERBOSE: print("Result Page %i"%page, "Successfully Connected.\n"
                      if r.status_code==200 else "Fail to Connect")              # Check if the connection is successful
    
    web_page = soup(r.text,"html.parser")


    ### Get the DOIs of all papers displayed on the html
    papers = web_page.body.find_all("h5",{"class":"issue-item_title"})                   # Get all the locations on websites where DOIs are listed         
    if VERBOSE:print("Raw extractions of DOIs:\n", papers)
    DOI_collection = []
    for i in range(len(papers)):
        DOI_raw = str(papers[i])                                                         
        doi_loc = DOI_raw.find('a href="')                                               # Find location of DOI in the DOI_raw
        DOI = "https://pubs.acs.org" + DOI_raw[doi_loc+8:DOI_raw.find('"', doi_loc+8)]   # Extract the DOI string and convert it into URL
        DOI_collection.append(DOI)
    if VERBOSE:print("\nExtracted DOIs:\n", DOI_collection)

    ### Enter the DOI links and Download SI PDFs
    for i in range(len(DOI_collection)):
        ts = time.time()                                                                 # Time each loop
        r = requests.get(DOI_collection[i])
        if r.status_code != 200: continue                                                # If fail to connect, just move on
        web_page = soup(r.text, "html.parser")                                           # Soup the html
 
        info, err = gather_information(web_page)                                         # Get info of the paper and check if it is a "good" paper
        if err:                                                                          # If "total synthesis" is not found in title, ignore the paper
            print("Paper%i is Bad Paper\n"%i)
            continue
        
        
        SIs = web_page.body.find_all("a",{"class":"suppl-anchor"})
        SI_counter = 1                                                                   # One paper may have multiple SIs, label them
        for j in range(len(SIs)):
            SI_raw = str(SIs[j])
            si_loc = SI_raw.find(' href="')
            SI = "https://pubs.acs.org" + SI_raw[si_loc+7:SI_raw.find('"', si_loc+7)]    # Extract the SI string and convert it into URL
            if SI[-4:] != '.pdf': continue                                               # Only download pdf files (skip cif files) 
            pdf_name = SIs[j].text.split(' ')[0]                                         # Get PDF_name
            info.at[0,"PDFName"] = pdf_name                                              # Update info df
            info_table = pd.concat([info_table,info])                                    # Append to the original df
            if VERBOSE: print("Paper%i SI%i:"%(i,SI_counter), SI)
            SI_counter+=1
        
            ### Download SI pdfs to the set directory
            pdf = requests.get(SI)
            if pdf.status_code != 200:
                print("DOWNLOAD FAILED FOR PAPER%i SI%i\n"%(i,SI_counter))
                continue
            open(os.path.join(OUTPUT_DIRECTORY, pdf_name), 'wb').write(pdf.content)

        if VERBOSE:print("DOWNLOAD COMPLETED.TIME ELAPSED:%.3f s\n"%(time.time()-ts))

    if page % SAVING_INFO_FREQ == 0:
        info_table.to_csv(os.path.join(OUTPUT_DIRECTORY,"Info.csv"),index=False)         # Save Info.csv

print("Scraping Completed!")
    

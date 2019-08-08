from bs4 import BeautifulSoup
import re
import urllib.parse
import os
import pandas as pd

def remove_brackets(text):
    return re.sub(r'\[.*?\]','',text)

def remove_pro(text):
    return re.sub(r'Pro \d{1,2}','',text)

def remove_con(text):
    return re.sub(r'Con \d{1,2}','',text)

def remove_unwanted_char(text):
    #text = text.lower()
    text = text.replace("\"", "").replace("\n", "").replace("“", "").replace("\t", "")
    text = text.replace("(", "").replace(")", "").replace("”", "").replace(":", "").replace("' ", " ").replace(" '", " ").replace("-", " ")

    #remove unnecessary white spaces
    split = text.split()
    text = ' '.join(split)

    return remove_brackets(text)

def box_article(soup):

        list_pro = soup.find_all('div', class_='newblue-pro-quote-box')
        list_con = soup.find_all('div', class_='newblue-con-quote-box')
        
        pro = []
        for text in list_pro:
            pro.append(remove_brackets(text.get_text()))

        con = []
        for text in list_con:
            con.append(remove_brackets(text.get_text()))

        return pro, con

def table_article(soup):

    span_pro = soup.find_all('span', text=re.compile('Pro \d{1,2}'))
    span_con = soup.find_all('span', text=re.compile('Con \d{1,2}'))

    list_pro = [x.parent.get_text() for x in span_pro]
    list_con = [x.parent.get_text() for x in span_con]

    pro = []
    for text in list_pro:
        text_ = remove_brackets(remove_pro(text)).replace('\n','')
        if len(text_)>30:
            pro.append(text_)

    con = []
    for text in list_con:
        text_ = remove_brackets(remove_con(text)).replace('\n','')
        if len(text_)>30:
            con.append(text_)
    
    return pro, con

def write_single_argument_file(file, pro_,con_,question='unknown question'):
    argument_list = []
    for pro in pro_:
        text = remove_unwanted_char(pro)
        if len(text)>5:
            argument_list.append({'side':'pro', 'argument':text, 'question':question})
    for con in con_:
        text = remove_unwanted_char(con)
        if len(text)>5:
            argument_list.append({'side':'con', 'argument':text, 'question':question})


    df = pd.DataFrame(argument_list)
    df.to_csv('./intermediate_data/argument/'+file,index=False)
    return

def files_html(directory='./intermediate_data/html/'):
   return os.listdir(directory)

def process_question(text):
    text = text.split('-')[0]

    #remove unnecessary white spaces
    split = text.split()
    question = ' '.join(split)

    #print(question)
    return question

if __name__ == "__main__":
    files=files_html()#[:10]
    #files=['https:www.procon.orgheadline.php?headlineID=005390.html']
    #files=['https:videogames.procon.org.html']

    arguments = []
    files_not_possible = []
    path = os.path.abspath('./intermediate_data/html/')

    for file in files:
        with open(path + '/' + file) as f:
            content = f.read()
        #print(content)
        soup = BeautifulSoup(content)
        string = soup.prettify()
        soup = BeautifulSoup(string,'lxml')

        question = process_question(soup.title.string)
        #try box article
        pro,con = box_article(soup)
        
        #try table article
        if len(pro)+len(con)==0:
            pro,con = table_article(soup)

        if len(pro)+len(con)==0:    
            files_not_possible.append(file)
            print(file)
        else:
            arguments.append((file,pro,con,question))
            write_single_argument_file(file, pro,con,question)
            print(f'pro: {len(pro)} con: {len(con)} in file: {file}')

    print(f'files_not_possible: {len(files_not_possible)}')
    print(f'nr arguments: {len(arguments)}')    

    argument_list = []
    for arg in arguments:
        file_ = arg[0]
        question = arg[3]
        for pro in arg [1]:
            text = remove_unwanted_char(pro)
            if (len(text)>5):
                argument_list.append({'topic': file_, 'side':'pro', 'argument':text, 'question':question})
        for con in arg [2]:
            text = remove_unwanted_char(con)
            if len(text)>5:
                argument_list.append({'topic': file_, 'side':'con', 'argument':text, 'question':question})

    df = pd.DataFrame(argument_list)
    df.to_csv('./output/all_arguments.tsv',sep='\t',index=False)


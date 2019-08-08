#create directories
mkdir ./intermediate_data/
#saved html files
mkdir ./intermediate_data/html/
#csv files with arguments
mkdir ./intermediate_data/argument/
#csv files with body body
mkdir ./intermediate_data/body_body/
#crete output folder
mkdir ./output/

#crawl all html files
scrapy runspider code/procon_spider/spiders/argument_spider.py

#process html files to argumetnts
python3 code/crawl.py

#generate all training files
python3 code/pipeline.py
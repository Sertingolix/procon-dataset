

<p align="center">
<img src="https://mtc.ethz.ch/_jcr_content/rightpar/contextinfo/fullwidthimage/image.imageformat.context.180972075.svg" alt="MTC ETHZ" width="25%"/>
</p>

# ProCon Dataset

We present the ProCon Dataset, a new argument pair dataset helping to combat fake news. The dataset is composed of 35'000+ samples consisting of one question,two arguments and a label denoting if both arguments argue for the same side of the question or not. The dataset is based on [ProCon.org](https://www.ProCon.org). The best models so far predict the dataset with a validation accuracy of 65%. Human performance although is around ~25% higher making the ProCon Dataset a challenging task for future research. The dataset was created as part of the Bachelor Thesis "Fighting the Filter Bubble" by Lucas Brunner ([www.bru.lu](https://www.bru.lu)) at the Media Technology Center, ETH Zürich ([mtc.ethz.ch](https://mtc.ethz.ch)).

## Generating ProCon train and validation dataset
This repo contains code to generate the ProCon training and validation set.
Before running the script make sure the BeautifulSoup and Scrapy are installed. Afterwards simply run the script with `bash run.sh`. After the script finished an `output folder` will be created containing the ProCon Dataset in the body_body subfolder and other datasets which might be usefull. All datasets are saved as .tsv files (tab separated values file).

The output folder contains:
* body_body/: Main ProCon Dataset
* question_body/: Dataset consisting of the question, an argument and the side this argument is on 
* all_questions.tsv: File containing all question which have been crawled
* all_question_body.tsv: File containing all crawled arguments, the question they belong to and the side they are on.
(The dataset from the question_body folder without train/val split) 


## BeautifulSoup4 and Scrapy install

Install BeautifulSoup4 on debian systems with

```
sudo apt-get install python3-bs4
```
or install the python package with
```
pip3 install beautifulsoup4
```

Additionally install Scrapy to scrape all ProCon URLs and html files necessary for building the dataset.
```
pip3 install Scrapy --user
```

import os
import pandas as pd
import numpy as np
import sys
import time
import re

np.random.seed(68758)

def files_argument(directory='./intermediate_data/argument/'):
    #method listing all files in a directory
    return os.listdir(directory)

def get_agree(df):
    '''
    This method takes arguments and a side and creates aggree samples

    input: df frame with columns agree and side
    output: df with columns body1 and body
    '''
    data_agree = df.merge(df, on=['side'])

    data_agree = data_agree.drop(['side'], axis=1)

    data_agree = data_agree.drop_duplicates().reset_index(drop=True)

    # filter out trivial article article relations
    data_agree = data_agree[(
        data_agree.argument_x != data_agree.argument_y)]

    #rename column
    data_agree.columns = ['body1', 'body2']

    # return numpy array of results
    return data_agree.values

def get_disagree(df):
    '''
    This method takes arguments and a side and creates disaggree samples

    input: df frame with columns agree and side
    output: df with columns body1 and body
    '''

    #creating numpy arrays containing only pro or (exlusive) con arguments
    pro = (df[df['side'] == 'pro'])['argument'].values
    con = (df[df['side'] == 'con'])['argument'].values

    # filter out editorial responses
    num_pro = pro.shape[0]
    num_con = con.shape[0]
    if (num_pro == 1) or (num_con == 1) and not (num_pro == num_con):
        return None

    #repeat arguments in different fassion
    a = np.repeat(pro, con.shape[0], axis=0).reshape((-1, 1))
    b = np.tile(con, pro.shape[0]).reshape((-1, 1))

    #concatenate arguments
    result_ab = np.concatenate([a, b], axis=1)
    result_ba = np.concatenate([b, a], axis=1)
    result = np.concatenate([result_ab, result_ba])

    return result

def shuffle_argument(df):
    #suffle a dataframe and return it
    df = df.sample(frac=1., random_state=8971235).reset_index(drop=True)
    return df

def argument2bodybody_file():
    '''
    This method generates files of body body samples from non processed argument samples
    '''

    #create folder for saving files
    os.makedirs('./intermediate_data/body_body_train/', exist_ok=True)
    os.makedirs('./intermediate_data/body_body_val/', exist_ok=True)

    #get all available filenames from argument/question files
    files = files_argument()

    #iterate over all questions
    for file in files:

        #loading argument files
        df = pd.read_csv('./intermediate_data/argument/'+file)
        df = shuffle_argument(df)

        #creating agree samples
        data_agree = get_agree(df[['argument', 'side']])
        agree = np.array(['agree' for i in range(
            data_agree.shape[0])]).reshape((-1, 1))
        data_agree = np.concatenate((data_agree, agree), axis=1)

        #creating disagree samples and handle questions without disagree samples
        data_disagree = get_disagree(df[['argument', 'side']])
        if data_disagree is None:
            train_data = data_agree
        else:
            disagree = np.array(['disagree' for i in range(
                data_disagree.shape[0])]).reshape((-1, 1))
            data_disagree = np.concatenate((data_disagree, disagree), axis=1)

            data_disagree = data_disagree[data_disagree[:, 0]
                                          != data_disagree[:, 1]]

            train_data = np.concatenate((data_agree, data_disagree), axis=0)

        #create DataFrame form data
        train_data = pd.DataFrame(
            train_data, columns=['body1', 'body2', 'stance'])

        # add question column
        train_data['question'] = (df['question'].values)[0]

        ## splitting up data in train and validadation in a 80 20 split
        ## while guaranteeing that each argument is only in one set
        def unique_arguments(df):
            #returning unique argumetns from dataframe
            # remeber it's symetric
            unique = pd.concat((df['body1'], df['body2']), axis=0).drop_duplicates(
            ).reset_index(drop=True).values
            return unique

        def intersection_argument(df_val, df_train):
            #Takes two Dataframes and returns set of all argumetns which are in both DataFrames
            return set(unique_arguments(df_val)).intersection(set(unique_arguments(df_train)))

        #create basic split
        train_data = train_data.sample(frac=1, random_state=768976).reset_index(drop=True)
        split_index = train_data.shape[0]//5
        df_val = train_data[:split_index]
        df_train = train_data[split_index:]

        # removing samples going over the cut but keeping percentage
        # while arguments inbot sets exist
        while not len(intersection_argument(df_val, df_train)) == 0:
            len_train = df_train.shape[0]
            len_val = df_val.shape[0]
            intersection = intersection_argument(df_val, df_train)

            # always remove deterministic element from intersection
            value = min(intersection)
            if (len_train)/5 > len_val:
                # remove from train
                df_train = df_train[df_train.body1 != value]
                df_train = df_train[df_train.body2 != value]
            else:
                # remove from val
                df_val = df_val[df_val.body1 != value]
                df_val = df_val[df_val.body2 != value]

        #save to file
        df_train.to_csv('./intermediate_data/body_body_train/'+file+'.csv', index=False)
        df_val.to_csv('./intermediate_data/body_body_val/'+file+'.csv', index=False)


def aggregate_body_body():
    '''
    This method creates train and validation files from files containing body body samples
    '''
    #getting filenames for train and val set
    trainfiles = os.listdir('./intermediate_data/body_body_train/')
    valfiles = os.listdir('./intermediate_data/body_body_val/')

    #accumulate all samples from train and val set
    val = []
    train = []
    for file in trainfiles:
        train.append(pd.read_csv('./intermediate_data/body_body_train/'+file))

    for file in valfiles:
        val.append(pd.read_csv('./intermediate_data/body_body_val/'+file))

    #concatenate sets to DataFrame
    df_val = pd.concat(val, axis=0)
    df_train = pd.concat(train, axis=0)

    #shuffle ds
    df_val = df_val.sample(frac=1, random_state=768976).reset_index(drop=True)
    df_train = df_train.sample(
        frac=1, random_state=768976).reset_index(drop=True)

    def to_file(df,path):
        #filtre out none arguments
        #aparently this is not needed because the mistake was in tokenization
        df['len_body1']=df['body1'].apply(lambda text : len(text))
        df['len_body2']=df['body2'].apply(lambda text : len(text))
        df['len_question']=df['question'].apply(lambda text : len(text))
        df = df.query('len_body1>5 and len_body2>5')
        del df['len_body1']
        del df['len_body2']
        del df['len_question']
        df = df.sample(frac=1, random_state=768976).reset_index(drop=True)

        df.to_csv(path,index_label='id', sep='\t')
    
    #check how many agree and disagree labels each dataset has
    df_a = df_train[df_train['stance']=='agree']
    df_b = df_train[df_train['stance']=='disagree']
    print(f'train data: {df_a.shape[0]} {df_b.shape[0]}')
    df_a = df_val[df_val['stance']=='agree']
    df_b = df_val[df_val['stance']=='disagree']
    print(f'val data: {df_a.shape[0]} {df_b.shape[0]}')
    
    #create folder and save
    os.makedirs('./output/body_body/', exist_ok=True)
    to_file(df_val,'./output/body_body/val.tsv')
    to_file(df_train,'./output/body_body/train.tsv')


def gen_question_body():
    '''
    This method creates a file containing all questions from argument fiels
    '''
    #get all argumetn filenames
    files = files_argument()

    train_data = []

    for file in files:
        df = pd.read_csv('./intermediate_data/argument/'+file)
        # print(df)
        train_data.append(df[['question', 'argument', 'side']])

    # concatenating data and shuffle
    train_data = np.concatenate(train_data, axis=0)
    np.random.seed(68758)
    np.random.shuffle(train_data)
    train_data = pd.DataFrame(train_data)

    # change name of columnt
    train_data.columns = ['body1', 'body2', 'stance']

    # shuffle
    train_data.sample(frac=1, random_state=768976).reset_index(drop=True)

    # map pro con to agree and disagree
    train_data['stance'] = train_data['stance'].apply(
        (lambda x: 'agree' if x == 'pro' else 'disagree'))

    #save files with all question and bodys in one file
    train_data.to_csv('./output/all_question_body.tsv',
                              index_label='id', sep='\t')

    #create dataframe with all questions
    df = pd.concat((train_data['body1'], train_data['body2']), axis=0).unique()
    df = pd.DataFrame(df)

    #save all questions to file
    df.to_csv('./output/all_question.tsv', header=False, index=False, sep='\t')

def gen_question_body_procon():
    '''
    This method creates train and validation files containing question and body
    by making sure the split of arguments is the same as the one in body body files
    '''
    #create output folder
    os.makedirs('./output/question_body/', exist_ok=True)

    #load validation data and all question body samples
    val_df = pd.read_csv('./output/body_body/val.tsv', sep='\t')
    question_body = pd.read_csv('./output/all_question_body.tsv', sep='\t')
    print(question_body.shape[0])

    #del id because it will be replaced
    del question_body['id']

    #symetric
    argument_val = set(val_df['body1'].values)
    question_body['inval'] = question_body['body2'].apply(lambda body: body in argument_val) 

    #create question body files for traiing and validation with same split as bodu body files
    question_body_val = question_body[question_body['inval']]
    question_body_train = question_body[~question_body['inval']]

    #drop colums which are not used anymore
    del question_body_val['inval']
    del question_body_train['inval']

    #reset index
    question_body_val = question_body_val.reset_index(drop=True)
    question_body_train = question_body_train.reset_index(drop=True)

    #save to file
    question_body_train.to_csv('./output/question_body/train.tsv', index_label='id', sep='\t')
    question_body_val.to_csv('./output/question_body/val.tsv', index_label='id', sep='\t')


if __name__ == "__main__":
    print('argument2bodybody_file')
    argument2bodybody_file()
    print('aggregate_body_body')
    aggregate_body_body()
    print('gen_question_body')
    gen_question_body()
    print('gen_question_body_procon')
    gen_question_body_procon()
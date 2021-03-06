# -*- coding: utf-8 -*-
"""textSummerization.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DlmEL_k2M4wpNW5gt71GzbmiO43h2yEa
"""

import numpy as np
import pandas as pd
from nltk.tokenize import sent_tokenize
import re
from typing import Callable
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
import string
import nltk

nltk.download('punkt')

class SentenceEmbedding:
  '''
  A class for find embeddings of a sentence by averaging its word embeddings.

  Attributes
  -----------------------------
  file_location: str
           location of the pretrained model 
  embed_size:int
          dim of the embedding
  Methods
  -----------------------------

   getWordEmbedMatrix() -> a dictionary[word:vector embedding]
    find embedding of the most common word in english 

   sentEmbed(worldlist: List[str]) -> ndarray[float64]
    find embedding of a senctece from the mean embedding of its words
  '''
  def __init__(self,file_location,embed_size):
    """
        Parameters
        ----------
        file_location: str
           location of the pretrained model 
        embed_size:int
          dim of the embedding
    """
    self.embed_size=embed_size
    self.file_location=file_location
     
    
  def getWordEmbedMatrix(self):
    """helper method :find embedding of the most common words in english 
            
            Returns
            -------
            dictionary 
              A dictionary of words as a key and vectors embedding as values 
    """    
    word2vec=dict()
   
    embedfile=self.file_location
    embedd_size=self.embed_size
    
    with open(embedfile, encoding='utf-8') as f:
      for line in f:
        l=line.split()
        word=l[0]
      
        vec=np.array(l[1:],dtype='float32')
        if len(vec>1):
            word2vec[word]=vec
    return word2vec
  def sentEmbed(self,wordlist):
    """find embedding of a senctece from the mean embedding of its words
            Parameters
            ----------
           wordlist : list[str]
            list of words that are in the sentence

            Returns
            -------
            numpy array
            An array  of dim: embed_size contains averged sentence embedding over all words
    """

    embed=self.getWordEmbedMatrix()
    arr=[]
    for word in wordlist:
      if word in embed:
          wordembed=list(embed[word])
          arr.append(wordembed)
    meanEmbed=np.mean(np.array(arr),axis=0)
    return meanEmbed

class Summerizer:
  '''
  A summerizer that uses Kmean clustering to extract summerized text according to the word embeddings vectors.
   Attributes
  -----------------------------
  sent_embedding: an instance of sentence embedding class 
    
  Methods
  -----------------------------

   sent_preprocess_tokenize(sentences: List[str]) -> ndarray of sentences embeddings shape :No of senteces x embed_size
      preprocess (remove punctuations , emojies )from senctences and then tokenize them into words

   cluster(No_summeries:int, data:dataFrame) -> pandas.Series of Summeries 
       depending of number of clusters found , find one representative sentence of its cluster(the closest to its centroid) and put it in the summary.

   evaluate(No_summeries:int, data:dataFrame) -> List[int] of blue scores for text
      evaluate the summary based on sentence blue score between ground truth and predicted 
  '''
  def __init__(self,sent_embedding: SentenceEmbedding,textTokenize:Callable):
    """
        Parameters
        ----------
        sent_embedding : object
          instance of sentenceEmbedding class
        textTokenize : function
           tokenize a text into sentences 
        
    """
    self.sent_embedding= sent_embedding
    self.textTokenize=textTokenize
   
  def sent_preprocess_tokenize(self,sentences):
      """ preprocess (remove punctuations , emojies )from senctences and then tokenize them into words 
              Parameters
              ----------
              sentences :List[str] 

              a text tokenized into sentences 

              Returns:ndarray of dim: sentence x embed_size 
              -------
              contains averged sentences embedding over all words
      """

      embeddings=[]
      for sent in sentences:
         
          sent=str(sent).lower()
         
          sent=re.sub(r'[^\w\s]','',sent)
          
          emogi_pattern = re.compile(pattern = "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                              "]+", flags = re.UNICODE)
          sent=re.sub(emogi_pattern,'',sent)
          tokens=sent.split()
     
          if len(tokens)>2:
           # print(tokens)
            embeddings.append(list( self.sent_embedding.sentEmbed(wordlist=tokens)))

      return np.array(embeddings)


  def cluster(self,No_summeries,data):
      """cluster similar sentences into number of clusters depeding of the length of the original text , then output one sentence from each cluster
              Parameters
              ----------
              No_summeries:int
              number of summeries you want to find from the dataset provided 

              data:pandas DataFrame
              a data set contains the text column to be summerized

              Returns
              -------
              pandas Series
              contains  a list of shape (No of summaries)   
      """
      for j in range(No_summeries):
        avg=[]

        rev=self.textTokenize(data.loc[j,'Text'])
       
        processed=self.sent_preprocess_tokenize(rev)
     
        no_clusters=int(np.ceil(np.sqrt(len(rev))))
        
        kmean=KMeans(n_clusters= no_clusters,random_state=123).fit(processed)
        for i in range(no_clusters):
          idx=np.where(kmean.labels_==i)[0]
          avg.append(np.mean(idx))
        closed,_=pairwise_distances_argmin_min(kmean.cluster_centers_,processed)
        order=sorted(range(no_clusters),key=lambda k :avg[k])
        summ=''.join(rev[closed[idx]] for idx in order)
        data.loc[j,'summary']=summ
      return data.loc[:No_summeries,'summary']
    

  def evaluate(self ,No_summeries,data):
    """evaluate the summary based on sentence blue score between ground truth and predicted 
            Parameters
            ----------
            No_summeries:int
            number of summeries you want to evaluate 

            data:pandas DataFrame
             a data frame that contains the ground truth and predicted summeries 

            Returns
            -------
            List[int]
            A list of blues scores for each summary
    """
    scores=[]
    for i in range(No_summeries):
        scores.append(nltk.translate.bleu_score.sentence_bleu(data['Summary'][i],data['summary'][i]))
    return scores


def textTokenize(reviews):
  '''
  A text tokenizing function , convert a text into tokenized sentences 

  Args:
  List[text] list of documents or reviews  to be tokenized

  Returns:
  List[List[str]] of tokenized text
  '''



      
  sentences=sent_tokenize(reviews)
   
  sens=[]
  for sentence in sentences:
        sentence.strip()
        if sentence=='':
          continue
        sens.append(sentence)
      #senTokens.append(sens)
  return sens

def main():
 e=SentenceEmbedding('/content/glove.twitter.27B.25d.txt',25)
 su=Summerizer(e,textTokenize)
 print(su.cluster(3,data))
 data['summary']=su.cluster(3,data)
 scores=su.evaluate(3,data)

if __name__ == "__main__":
    main()
# Text-Summerization
It is an extractive summarizer python code based on unsupervised kmeans clustering .the implementation is simple and only dependes on senctece embeddings of the text and how to cluster them properly .However it is best suited for short documents like reviews .
# How it works
the main idea lies behind the concept that similar sentences in meaning have similar words embeddings so , why not cluster them together and then take one representative sentence of that cluster (the closest to the center of the cluster) and then order those representative sentences according to the original document order.Note that number of clusters is calculated as the root square of the length of the document .it is just an approximation , maybe you can try another way of finding number of clusters!

# How to use it
The data is assumed to be in a data frame with Text column for your text and Summary column that contain ground truth(GT) summeries (for evaluation purposes), you can change the name of those column that contain your text  and GT summary in cluster() and evaluate() methods respectively .Both of them are inside Summerizer class .
The project contains two classes in textSummerization.py As follows:

SentenceEmbedding:

This class is responsible for providing sentence  embedding . The first method  finds the words embedding matrix by using a pre-trained word embedding file and load into a dictionary.The other method average those word embedding along word axis to find the whole sentence embedding. 
This class expects the following attributes :
- The location of the file of  the pretrained model  and the size of the embedding .Note : I used glove with 25 embed_size & got good results.you can try fasttext instead!.
- To download a pre-trained word embedding file for glove you can use this [link](https://zenodo.org/record/3237458/files/glove.twitter.27B.25d.txt.gz?download=1).

Summarizer

This class is responsible for summarization and evaluation of that summary . This class expects to get the following when intializing it:
- SentenceEmbedding object(from above) and the text Tokenizer (that tokenize the text into sentences).
- Its evaluation method uses sentence blue score to compare GT and predicted values .


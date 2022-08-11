# Random-Forest

We created the baseline for our model from the paper `Automatically detecting the scopes of source code comments`

There are three different features: code features, comment features and code/comment features.

## STEP 0: before starting
We set some global variable at the beginning of the main file that must be defined before running the code.

input_folder = <input/{train.csv,test.csv,eval.csv}> <br>
xml_folder = <xml/{train.csv,test.csv,eval.csv}> <br>
output_folder = output/

## STEP 1: preprocessing
In this step we preprocess the dataset in order to extract the information about comments and the xml code parsed by SrcML. We will use it later for running the baseline

For doing that, you can run:
```
python3 main.py --preprocessing
```

## STEP 2: train the skipgram model
The authors trained a skipgram model on a corpus of java methods and comments, in order to align the natural language and the code (i.e., NL referred to a specific snippet should be similar to the code it is commenting).
Since the dataset is not available, we used the snippets labeled by our team (only the training set) for training the skip-gram model. The idea is to alternate NL tokens and code tokens (see paper for further details).
We trained word2vec using the corpus created.

For doing that, you can run:
```
python3 main.py --train_skipgram
```

The file will be saved as `skipgram_model.model`

## STEP 3
In this step we created code features, comment features, and code-comment features (following what explained in the paper).
For code features, we classified each statement based on the categories defined in the paper (+ an OTHER category). We decided to add this extra category for keeping into account all the statements. 
A statement must contain more than one line.
<br>
For instance:
```
for (int i=0; i<10;i++){
System.out.println("I just got executed!");
}
```


With that classification, we computed all the features defined in the paper

For comment features, we applied the steps defined to the comment (tokenization, stemming, stop word removal) and then we computed the features defined by the authors

For code-comment features, we loaded the skipgram model trained in step 1 and we computed all the similarities written in the paper

Once done with this, we merged all results from all features in a single result file (one for each set)

the files like {}_features.csv (with {} in ["train", "eval", "test"]) contain the set of all features from the three categories, while the files like {}_results.csv (with {} in ["train", "eval", "test"]) contain for each set the ID of the row and the result (1 if the comment refers to that block, 0 otherwise).
It may happen that a comment refers only to a part of the statement (e.g., comment may refer only to the body of the for previously defined). In this case we consider that the comment is NOT referring to the for statement, but it is referring to each statement in the body

For doing that, you can run

```
python3 main.py --write_all_features
```

## STEP 4


```
python3 main.py --train_random_forest
```


In this step we created the result file named `result_authors.csv`, with the configuration chosen by the authors.
We reported each method in the test set, adding the special tokens <start> and <end> at the beginning and at the end of the lines that the random forest predicted to be commented.

You can run:
```
python3 main.py --save_results
```

STEP4bis: adjusting result file
The model was thought to comment a single block of code (consecutive lines) but we're using it to comment also different blocks (all the cases where the model is predicting 1)
For this reason, we decided to only predict as commented the first block found by the model.
So we can read the `result_authors.csv` file and only keep the first block predicted to be commented

You can run:
```
python3 main.py --adjust_results
```

It will create the file `result_authors_adjusted.csv`.
This file can be used for computing the performance of the baseline.


### STORED FILES


In output/features you can find the features (used for training the random forest) and the results.
Each row in the features contain a statement of a specific instance with all code, comment and code features. Each row in the result contain for each statement if it is commented or not
In output/raw_predictions you can find the raw output of the random forest (i.e., for each statement if it predicts that statement to be referred to the comment or not) and the final result we use for the comparison with the baseline (with the <start> and <end> tag used for defining the commented block of code)
In output/results you can find the results.csv and results_adjusted.csv




### REQUIREMENTS:
nltk==3.7 \
gensim==4.2.0 \
scikit-learn==1.0.1(IMPORTANT, the last version is broken) \
javalang==0.13.0 \
pandas==1.4.2 \
lxml==4.8.0
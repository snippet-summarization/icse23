import pandas as pd
from tqdm import tqdm
import sys
from sklearn.feature_extraction.text import TfidfVectorizer

def cosine_sim(text1, text2, model):
    tfidf = model.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]


def main():

    df_train = pd.read_csv('train.csv')
    df_test = pd.read_csv('Splits/test{}.csv'.format(sys.argv[1]))
    

    snippets_train = list(df_train['codeSnippet'])
    #snippets_test = list(df_test['filteredSnippet'])

    vectorizer = TfidfVectorizer(stop_words=None)
    X = vectorizer.fit_transform(snippets_train)

    best_matching_snippet = []
    retrievedCommentItem = []
    cosineValues = []
    


    for idx_test,row_test in tqdm(df_test.iterrows()):
        
        sTest = row_test['codeSnippet']
        
        bestCosine = 0
        matchingSnippet = ''
        retrievedComment = ''

        for idx_train,row_train in df_train.iterrows():
            
            sTrain = row_train['codeSnippet']
            
            try:
                cosine = cosine_sim(sTrain, sTest, vectorizer)
            
            except Exception:
                
                with open('analyze.txt','a+') as f:
                    f.write(str(idx_train)+"\n")
                
                continue

            if cosine > bestCosine:
                bestCosine = cosine
                retrievedComment = row_train['comment']
                matchingSnippet = sTrain

        best_matching_snippet.append(matchingSnippet)
        retrievedCommentItem.append(retrievedComment)
        cosineValues.append(bestCosine)
        # print("\n**********************************")
        # print("Cosine Value: {}".format(bestCosine))
        # print("Retrieved Comment: " + retrievedComment)
        # print("Code Snippet under Test: "+matchingSnippet)
        # print("************************************\n")
        # sys.exit(0)

    df_test['bestMatchingSnippet'] = best_matching_snippet
    df_test['cosine'] = cosineValues
    df_test['retrievedComment'] = retrievedCommentItem
    df_test.to_csv('test-results-tf-idf{}.csv'.format(sys.argv[1]))

if __name__ == '__main__':
    main()



# Towards Summarizing Code Snippets Using Pre-Trained Transformers

Towards our goal of automatically summarizing code snippets, we first manually built a dataset featuring 11.5k comments that have been (i) classified based on their type (e.g, code summary, TODO), and (ii) linked to the exact code statements they document. Second, we used such a dataset to train a multi-task DL model taking as input a comment and being able to (i) classify whether it represents a ''code summary'' or not, and (ii) link it to the code statements it documents. Our trained model identifies code summaries with 83% accuracy and is able to link them to the documented lines of code with recall and precision higher than 80%. Third, we run this model on 10k Java open source projects, automatically identifying code summaries and linking them to the related documented code. This allowed to build a large-scale dataset of documented code snippets that has then been used to train a new DL model able to automatically document code snippets.

### Repository Structure:

  - <a href="">Code</a> contains the code we developed concerning both part of the approach. In other words, under <a href="">Code/Linking</a> you can find the code concerning the automatic classification of code comments and likage to the documented code, while <a href="">Code/Code-Snippet-Summerizers</a> contains the code for training and testing **STUNT** (i.e, the T5-based model in charge of documenting code snippets).
  <br>
  - The Datasets :open_file_folder: are available at the following link: https://drive.google.com/drive/folders/1a8UOR5g9zSO0mPv293_xs0PSWLlQZ7BF?usp=sharing
  The GDrive folder contains three subfolders,
     *  <a href="">*Manually-Annotated-Dataset*</a>, which contains the manually labeled dataset featuring 11.5k instances. Such a dataset is structered with the following columns:
        *  *javaClass*: The Java class containing the method of interest.
        *  *originalMethod*: The original Java method extracted from the beforementioned *javaClass*.
        *  *Comment*: The comment we manually labeled within the *originalMethod*.
        *  *spanComment*: The absolute (i.e, relative to the *javaClass*) byte position where the selected *Comment* begins and ends.
        *  *documentedCode*: The code snippet linked to the *Comment*.
        *  *spanCode*: The same as *spanComment* but for the selected code snippet.
        *  *category*: The selected category for the *Comment*.
        *  *tokenizedInput*: A tokenized version of the *originalMethod* obtained using tree-sitter.
        *  *isCodeDescription*: A boolean flag, indicating whether the category is a summary or not.
        *  *tokensLength*: The number of tokens featuring the *originalMethod*.
    * <a href="">*Large-Scale-Dataset*</a>, which contains the large scale dataset built using **SALOON**, the T5-based model we developed to automatically classify code comments by linking them to the documented piece of code.
     *  <a href="">*T5 pre-training*</a>, which contains the dataset for pre-training the T5 model that we built starting from the <a href="https://github.com/github/CodeSearchNet">CodeSearchNet</a> dataset.
     <br>  
- The trained models are available at the following link: https://drive.google.com/drive/folders/1ylGbBRsZ1ZN4H8MbPhudRrpe5KhN1IMR?usp=sharing
  The GDrive folder contains four subfolders containing the following models:
  * *Classification&Linking*, where you can find **SALOON**.
  * *CodeSnippetDocumentation*, containing **STUNT**, the model we develop to support the task of code snippet summarization.
  * *RLCom-T5-Replica*, where we make available the model trained using the dataset released in <a href="https://www.sciencedirect.com/science/article/pii/S0950584920301427?casa_token=jW82qRE6oDgAAAAA:Af44jxT9CVnaz7wdFu_KPJx--aawBaVmLtyFLXavZLirD5meTexlR6_gf-CdOMVZMhvWkdB54mY">Towards automatically generating block comments for code snippets</a>  
  * *T5-Pre-Trained-Model*, the T5 pre-trained model we use as back-bone for both approaches prensented in our study, namely **SALOON** and **STUNT**.
<br>
- The results :page_facing_up: of our study are available at the following link: https://drive.google.com/drive/folders/1gvkvqR5PJtW_WfrmIYa16nRVmfqVYvsI?usp=sharing
The GDrive folder contains four subfolders, each one reporting the predictions we obtained for each part of our approach.
In details:
  * *Classification&Linking* contains the results of each model we use for such a task. Thus, we report the results achieved by the three different baselines (i.e, blank-line, random-forest and token-based-text similarity) and **SALOON**.
  NB: Concerning **SALOON**, we also release the results of the hyper-parameter tuning phase when both T5 training strategy are adopted, meaning with-pretraining and no-pretraining.
  * *Automated-Code-Snippet-Documentation*. In this folder we make available the results achieved by **STUNT** on both the test and eval set (Hyper-parameters tuning).
  * *RLCom-Replication* contains the results achieved using a pre-trained transformer model (T5) on the dataset released in <a href="https://www.sciencedirect.com/science/article/pii/S0950584920301427?casa_token=jW82qRE6oDgAAAAA:Af44jxT9CVnaz7wdFu_KPJx--aawBaVmLtyFLXavZLirD5meTexlR6_gf-CdOMVZMhvWkdB54mY">Towards automatically generating block comments for code snippets</a>.
<br>
- The SentencePiece Model we trained using the pre-training dataset is available at the following link: https://drive.google.com/drive/folders/14qSdyPaIjX_3XOykl3y3ejQ_c_AGKoli?usp=sharing
We use such a model to make the T5 model comfortable in dealing with a software-specific corpus, during the pre-training and fine-tuning phases.
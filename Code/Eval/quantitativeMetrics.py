import nltk
from bleu import *
import sys
from rouge_score import rouge_scorer


def meteor(prediction,reference):
	return (nltk.translate.meteor_score.meteor_score([prediction], reference, gamma=0))

def rouge(prediction,reference,scorer):
	rougeL = scorer.score(prediction,reference)
	precision,recall,fmeasure = rougeL['rougeL'].precision, rougeL['rougeL'].recall, rougeL['rougeL'].fmeasure
	return precision,recall,fmeasure

def main():

	scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=False)


	with open('targets') as f:
		targets = [item.rstrip('\n') for item in f.readlines()]

	with open('predictions') as f:
		predictions = [item.rstrip('\n') for item in f.readlines()]

	meteor_score = 0.0
	sentence_bleu_4 = 0.0
	overallPrecision = 0.0
	overallRecall = 0.0
	overallFmeasure = 0.0

	for target,prediction in zip(targets,predictions):
		
		meteor_score += meteor(prediction, target)
		precision,recall,fmeasure = rouge(prediction,target,scorer)
		sentence_bleu_4 += score_sentence(prediction,target,4,1)[-1]

		overallPrecision += precision
		overallRecall += recall
		overallFmeasure += fmeasure
		

	print("Meteor-Score: {}".format(meteor_score/len(predictions)))
	print("BLEU-4: {}".format(sentence_bleu_4/len(predictions)))
	print("Rouge-Precision: {}".format(overallPrecision/len(predictions)))
	print("Rouge-Recall: {}".format(overallRecall/len(predictions)))
	print("Rouge-Fmeasure: {}".format(overallFmeasure/len(predictions)))

if __name__ == '__main__':
	main()

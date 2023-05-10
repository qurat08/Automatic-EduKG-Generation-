# Datasets for keywords extraction  Evaluation

KwpExtractorNLP can be evaluated on Keyphrase extraction annotated datasets.
The datasets can be downloaded here [KeywordExtractor-Datasets](https://github.com/LIAAD/KeywordExtractor-Datasets).
Download the **SemEval2017** dataset, unzip it in the Dataset directory.

You can now run `python evaluation/sif_evaluation/sif_eval.py` to evaluate the models.

If you want to also perform trec evaluation, follow the step below.

Create ***keyphrases*** and **Models** and "**Output**" directories in data.

* Keyphrases: keyphrases extracted from the datasets by the algorithms will be stored in this directory.
* Models: Download supervised and unsupervised to speed up the extraction for certain algorithms. You can find them [here](http://www.ccc.ipt.pt/~ricardo/kep/data.zip). You can choose not to download the models and let them be created automatically.
* Output: directory to store the .qrels and .out files (only for the trec evaluation). Make sure to add the directory path in config.yml

Trec evaluation can be performed running`python evaluation/sif_evaluation/trec_eval.py`

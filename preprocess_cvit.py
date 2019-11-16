from argparse import ArgumentParser
from fairseq.data.cvit.utils import pairs_select
from fairseq.data.cvit.dataset import _CVITIndexedRawTextDataset
from fairseq.data.cvit.lmdb import LMDBCorpusWriter, LMDBCorpus
import yaml
from multiprocessing import Pool
import os

def add_args(parser):
	parser.add_argument('data', help='colon separated path to data directories list, \
						will be iterated upon during epochs in round-robin manner')

def read_config(path):
    with open(path) as config:
        contents = config.read()
        data = yaml.load(contents)
        return data

def build_corpus(corpus):
	from ilmulti.sentencepiece import SentencePieceTokenizer
	tokenizer = SentencePieceTokenizer()
	if not LMDBCorpus.exists(corpus):
		print("LMDB({}) does not exist. Building".format(corpus.path))
		raw_dataset = _CVITIndexedRawTextDataset(corpus, tokenizer)
		# writer = BufferedLMDBCorpusWriter(corpus, tokenizer, num_workers=30, max_size=1024*1024)
		writer = LMDBCorpusWriter(raw_dataset)
		writer.close()
		print("Built LMDB({})".format(corpus.path))


def get_pairs(data):
	corpora = []
	for split in ['train','test','dev']:
		pairs = pairs_select(data['corpora'], split)
		srcs,tgts = list(zip(*pairs))
		corpora.extend(srcs)
		corpora.extend(tgts)
	
	return list(set(corpora))

def mp(build_corpus , corpora):
	pool = Pool(processes=os.cpu_count())
	pool.map_async(build_corpus , corpora)
	pool.close()
	pool.join()

if __name__ == '__main__':
	parser=ArgumentParser()
	parser.add_argument('data')
	args = parser.parse_args()
	data = read_config(args.data)
	corpora = get_pairs(data)
	mp(build_corpus , corpora)



      
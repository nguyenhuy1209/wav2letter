# Steps to reproduce results on VIVOS

## Instructions to reproduce

Run data and auxiliary files (like lexicon, tokens set, etc.) preparation (set necessary paths instead of `[...]`: `data_dst` path to data to store, `model_dst` path to auxiliary path to store).
```
pip install sentencepiece==0.1.82
python3 ../../utilities/prepare_vivos_wp.py --data_dst [...] --model_dst [...]
```
Besides data the auxiliary files for acoustic and language models training/evaluation will be generated:
```
cd $MODEL_DST
tree -L 2
.
├── am
│   ├── vivos-train-all-unigram-3321.model
│   ├── vivos-train-all-unigram-3321.tokens
│   ├── vivos-train-all-unigram-3321.vocab
│   ├── vivos-train+dev-unigram-3321-nbest10.lexicon
│   ├── vivos-train-unigram-3321-nbest10.lexicon
│   └── train.txt
└── decoder
    ├── 4-gram.arpa
    ├── 4-gram.arpa.lower
    └── decoder-unigram-3321-nbest10.lexicon
```

### AM training
- Fix the paths inside `train*.cfg`
```
../../../../../wav2letter/build/Train train --flagsfile train_am_500ms_future_context.cfg --minloglevel=0 --logtostderr=1
```

### LM downloading and quantization
```
source prepare_lms.sh [KENLM_PATH]/build/bin [DATA_DST]/decoder
```

### Reproduce beam-search decoding
- Fix the paths inside `decoder*.cfg`
- Run decoding with `decoder*.cfg`
```
[...]/wav2letter/build/Decoder \
  --flagsfile decode_500ms_future_context_ngram_other.cfg \
  --lm=[DATA_DST]/decoder/3-gram.pruned.3e-7.bin.qt \
  --lmweight=0.5515838301157 \
  --wordscore=0.52526055643809

[...]/wav2letter/build/Decoder \
  --flagsfile decode_500ms_future_context_ngram_other.cfg \
  --lm=[DATA_DST]/decoder/3-gram.pruned.3e-7.bin \
  --lmweight=0.51947402167074 \
  --wordscore=0.47301996527186

[...]/wav2letter/build/Decoder \
  --flagsfile decode_500ms_future_context_ngram_other.cfg \
  --lm=[DATA_DST]/decoder/3-gram.pruned.1e-7.bin.qt \
  --lmweight=0.51427799804334 \
  --wordscore=0.17048767049287

[...]/wav2letter/build/Decoder \
  --flagsfile decode_500ms_future_context_ngram_other.cfg \
  --lm=[DATA_DST]/decoder/3-gram.pruned.1e-7.bin \
  --lmweight=0.53898245382313 \
  --wordscore=0.19015993862574

[...]/wav2letter/build/Decoder \
  --flagsfile decode_500ms_future_context_ngram_other.cfg \
  --lm=[DATA_DST]/decoder/3-gram.bin.qt \
  --lmweight=0.67470637680685 \
  --wordscore=0.62867952607587

[...]/wav2letter/build/Decoder \
  --flagsfile decode_500ms_future_context_ngram_other.cfg \
  --lm=[DATA_DST]/decoder/3-gram.bin \
  --lmweight=0.71651725207609 \
  --wordscore=0.83657565205108

[...]/wav2letter/build/Decoder \
  --flagsfile decode_500ms_future_context_ngram_other.cfg \
  --lm=[DATA_DST]/decoder/4-gram.bin.qt \
  --lmweight=0.70340747256672 \
  --wordscore=0.85688768944222

[...]/wav2letter/build/Decoder \
  --flagsfile decode_500ms_future_context_ngram_other.cfg \
  --lm=[DATA_DST]/decoder/4-gram.bin \
  --lmweight=0.71730466678122 \
  --wordscore=0.91529167643869
```
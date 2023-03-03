import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_splitter import SentenceSplitter
from random import choice

# !pip install torch transformers sentencepiece protobuf==3.20 openai
# !pip install sentence_splitter

model = AutoModelForSeq2SeqLM.from_pretrained("ramsrigouthamg/t5_sentence_paraphraser")
tokenizer = AutoTokenizer.from_pretrained("ramsrigouthamg/t5_sentence_paraphraser")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
beams = sequences = 10
splitter = SentenceSplitter(language='en')


def para_phraser(input_text):
    text = "paraphrase: " + input_text + " </s>"
    encoding = tokenizer.encode_plus(text, max_length=512, padding='max_length', return_tensors="pt")
    input_ids, attention_mask = encoding["input_ids"].to(device), encoding["attention_mask"].to(device)
    model.eval()
    beam_outputs = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=512,
        early_stopping=True,
        num_beams=beams,
        num_return_sequences=sequences
    )
    para_back = []
    for beam_output in beam_outputs:
        sent = tokenizer.decode(beam_output, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        para_back.append(str(sent).strip('paraphrasedoutput: '))
    send_back = choice(para_back)
    return send_back


def content_paraphraser(content):
    final_content = ''
    paragraphs_split = list(filter(lambda x: x != '', content.split('\n\n')))
    paragraphs_counter = len(paragraphs_split)
    for paragraphs in paragraphs_split:
        paragraphs = paragraphs.split("\n")
        for paragraph in paragraphs:
            # Breaking a paragraph into sentences
            sentences = splitter.split(paragraph)
            sentences_counter = len(sentences)

            for index, sentence in enumerate(sentences):
                # Omitting the first sentence. Sometimes there is a problem with t5_sentence_paraphraser and numbers
                # at the beginning of a sentence
                if index > 0:
                    p_sentence = para_phraser(input_text=sentence)
                    final_content += p_sentence
                else:
                    final_content += sentence
                if sentences_counter > 1:
                    final_content += ' '
            if sentences_counter == 1:
                final_content += '\n'

        if paragraphs_counter > 1:
            final_content += '\n\n'

    return final_content




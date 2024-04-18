import spacy

# 打印已加载模型的路径
print(spacy.__file__)

nlp = spacy.load("zh_core_web_md")

def extract_verb_object_phrases(text):
    doc = nlp(text)
    verb_object_phrases = []

    for token in doc:
        # 找到动词
        if "VERB" in token.pos_:
            verb = token.text
            phrase = []

            # 查找动词的宾语
            for child in token.children:
                if "NOUN" in child.pos_:
                    object_phrase = child.text
                    phrase.append(object_phrase)

            # 如果找到了宾语，将动词和宾语短语添加到列表中
            if phrase:
                temp_res = (verb, "".join(phrase))
                verb_object_phrases.append(temp_res)
                print(temp_res)

    return verb_object_phrases

text = input()

extract_verb_object_phrases(text)
import openai
from time import sleep
from sys import exit
from config import language, API_KEY

openai.api_key = API_KEY


def open_ai(text):
    retry = 0
    t = 10
    while True:
        try:
            return openai.Completion.create(model="text-davinci-003", prompt=text, max_tokens=2000, temperature=0.8)['choices'][0]['text']
        except Exception as e:
            retry +=1
            print(f'OpenAI threw an error {e}, sleeping for {t} seconds. Retry {retry} of 5')
        if retry == 5:
            exit(f'Looks like openAI is not working. Check Your API-Key or Credits')
        else:
            sleep(t)
            t += 10
            continue


def topic_list(keyword):
    topics_list = open_ai(f"Generate a 5 people-also-ask for \"{keyword}\" as a comma separated list without any serial numbers").replace("\n",'').split(',')
    # for i, t in enumerate(topics_list):
    #    print(f'{i+1}. {t.strip()} in {keyword}')

    question_list = []
    for topic in topics_list:
        # print(f'Pulling questions for {topic.strip()}')
        sleep(1)
        question_list.extend(open_ai(
            # f"a list questions around the topic {f'{topic.strip()} in {kw}'} as a comma separated list without
            # serial numbers").replace( "\n", '').split(','))
            f"Generate 5 people-also-ask around the topic {f'{topic.strip()} in {keyword}'} as a comma separated list "
            f"without serial numbers. Language {language}").replace(
            "\n", '').split(','))
    q_list = []
    q_len = len(question_list)
    sleep(1)
    for i, q in enumerate(question_list):
        q = ''.join([s.strip('\"') for s in q]).strip()
        print(f"Converting {i} of {q_len}, Title: {q.strip()} to a blog title.")
        q_list.append(''.join([s.strip('\"') for s in
                              open_ai(f'convert this question {q} to a blog post title. Language {language}').replace("\n", '').strip()]))

        print(f"Processed Output: {q_list[i]}\n")
        # OpenAI Rate limit
        if i == 20 or i == 60:
            sleep(5)


    #print(len(q_list))
    my_topic_list = list(set(q_list))
    for i, title in enumerate(my_topic_list):
        print(f'{i+1}. {title}')

    return my_topic_list


def article_generator(title):
    return open_ai(f'a detailed essay on "{title}". Language {language}')





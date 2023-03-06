from ai_content import topic_list, article_generator, article_poster
from config import language
from image_scraper import img_dir_cleaner, img_scraper, img_list, img_insert
from paraphraser import content_paraphraser
from time import sleep


img_dir_cleaner()
keyword = input('Keyword for content creator (example: \'seo\'): ')
titles = topic_list(keyword)

q_titles = len(titles)
img_scraper(keyword, q_titles)
for id, title in enumerate(titles):
    img_urls = img_list()
    art = article_generator(title)
    # Paraphraser model "ramsrigouthamg/t5_sentence_paraphraser" working only with English language
    if language.lower() == 'english':
        # print(f"Orginal:\n{art}")
        art = content_paraphraser(art)
        # print(f"Paraphrased:\n{art}")
    article = img_insert(art, img_urls)
    #
    article_poster(title, article)
    print(f"Post {id+1} of {q_titles} done!")
    print("Waiting 10 seconds...")
    print()
    sleep(10)

from ai_content import open_ai
from icrawler.builtin import BingImageCrawler
from icrawler import ImageDownloader
from six.moves.urllib.parse import urlparse
import random
import os, shutil
import base64
from secrets import token_hex as hex
import requests

from config import AUTH_USER, AUTH_PASSWORD, path, DOMAIN


class PrefixNameDownloader(ImageDownloader):

    def get_filename(self, task, default_ext):
        filename = super(PrefixNameDownloader, self).get_filename(
            task, default_ext)
        return hex(2) + "_" + filename


class Base64NameDownloader(ImageDownloader):

    def get_filename(self, task, default_ext):
        url_path = urlparse(task['file_url'])[2]
        if '.' in url_path:
            extension = url_path.split('.')[-1]
            if extension.lower() not in [
                'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif', 'ppm', 'pgm'
            ]:
                extension = default_ext
        else:
            extension = default_ext
        # works for python 3
        filename = base64.b64encode(url_path.encode()).decode()
        return '{}.{}'.format(filename, extension)


def img_dir_cleaner():
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def img_scraper(keyword, img_numbers):
    search_keywords = [keyword]
    data = open_ai(f"""Give me a list of similar keyword about {keyword}. 
                                    Comma separated without numeration. Language polish""").strip().split(",")
    search_keywords.extend(data)
    max_num = img_numbers * 5
    output_dir = 'images'

    for keyw in search_keywords:
        if max_num <= 0:
            break

        crawler = BingImageCrawler(downloader_cls=PrefixNameDownloader, storage={"root_dir": output_dir})
        crawler.session.verify = False  # Ignore SSL errors
        crawler.crawl(keyword=keyw, max_num=max_num)

        downloaded_num = len(os.listdir(os.path.join(output_dir)))
        max_num -= downloaded_num

    downloaded = len(os.listdir(os.path.join(output_dir)))
    print(f"Images scraping done. {downloaded} images downloaded!")


def img_uploader(filePath):
    with open(path + "/" + filePath, 'rb') as file:
        data = file.read()

    res = requests.post(url=f'{DOMAIN}/wp-json/wp/v2/media',
                        data=data,
                        headers={'Content-Type': 'image/jpeg',
                                 'Content-Disposition': f'attachment; filename={hex(3)}.jpg',
                                 },
                        auth=(AUTH_USER, AUTH_PASSWORD))
    new_dict = res.json()
    new_id = new_dict.get('id')
    link = new_dict.get('guid').get("rendered")
    #print(new_id, link)
    # return new_id, link
    os.remove(path + "/" + filePath)
    return link


def img_list():
    # Get list of all image files in the directory
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.jpg')]
    # Select random images from the list of files
    q_img = random.randint(1, 3)
    random_images = random.sample(files, q_img)

    img_urls = []
    for img in random_images:
        img_urls.append(img_uploader(img))

    return img_urls


def img_insert(article, img_urls):
    import random
    big_list = list(filter(lambda x: x != '', article.split('\n\n')))
    # Step 1: Generate a random number between 2 and 4 (inclusive)
    para_count = len(big_list)
    counter = len(img_urls)
    print(f"OBRAZKI DO WSTAWIENIA {counter}")
    if para_count < counter:
        counter = para_count
    # Split the list into for parts to insert image
    list_parts = [big_list[i:i + (para_count // counter)] for i in
                  range(0, para_count, (para_count // counter))]

    for b, i in enumerate(list_parts):
        for a, j in enumerate(img_urls):
            if b == a:
                i.append(f'<img src="{j}">')

    new_article = ""
    for i in list_parts:
        for a in i:
            new_article += a + "\n\n"

    return new_article

# Update FM cutouts from sortitoutsi.net
# Make a new config file that contains all the necessary information. Save which version is the last in the config file.
# Imports
import requests
from bs4 import BeautifulSoup


def get_last_update():
    with open("config.xml", "r") as file:
        content = file.readlines()
        content = "".join(content)
        bs_content = BeautifulSoup(content, "lxml")
        a = bs_content.find("last_update")
        file.close()
        return a.text


def create_bs4_object(url):
    html_content = requests.get(url, headers={
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
    soup = BeautifulSoup(html_content, "lxml")
    return soup


def get_new_cuts(last_update):
    i = 1
    active = True
    images_list = []
    while active:
        soup = create_bs4_object(f"https://sortitoutsi.net/graphics/submissions/1/queue?type=completed&status=active&inpack=&"
                          f"game_item_id=&sort=submitted_at-desc&submit=1&page={i}")
        for image in soup.find_all("a", {"class": "lightgallery-link"}):
            update_pack = image['href'].split("/")[7]
            if float(update_pack) <= float(last_update):
                print(f"{len(images_list)} new updates")
                active = False
                break
            images_list.append(image['href'])
        print(len(images_list))
        i += 1
    return images_list


def download_images(images_list):
    counter = 1
    for image in images_list:
        print(f"[DOWNLOADING] Image: {counter}/{len(images_list)}")
        with open(image.split('/')[-1], 'wb') as handler:
            handler.write(requests.get(image).content)
            handler.close()
        counter += 1


def get_new_cutouts(images_list):
    exsiting_ids = []
    new_ids = []
    with open("config.xml") as file:
        content = file.readlines()
        content = "".join(content)
        bs_content = BeautifulSoup(content, "lxml")
        records = bs_content.find("list").findChildren()
        for record in records:
            exsiting_ids.append(record['from'])
        counter = 0
        for image in images_list:
            print(f"[PROCESSING] Checking for new ids ({counter}/{len(images_list)})")
            image_id = image.split("/")[-1].replace(".png", "")
            if image_id not in exsiting_ids:
                print(f"[PROCESSING] Added missing ids (total: {len(new_ids)})")
                new_ids.append(image_id)
            counter += 1
        file.close()
        print
        return new_ids


def update_config(update_pack, last_update, ids):
    bs_content = ""
    with open("config.xml", "r") as file:
        content = file.readlines()
        content = "".join(content)
        bs_content = BeautifulSoup(content, "lxml")
        bs_content.find("last_update").string.replace_with(update_pack)
        for new_id in ids:
            new_div = bs_content.new_tag("record")
            new_div['from'] = new_id
            new_div['to'] = f"graphics/pictures/person/{new_id}/portrait"
            bs_content.html.body.list.append(new_div)
        file.close()
    with open("config.xml", "w") as file:
        file.write(str(bs_content.prettify()))
        print("[CONFIG] Updated config file")
        file.close()


if __name__ == "__main__":
    last_update = get_last_update()
    images_list = get_new_cuts(last_update)
    download_images(images_list)
    ids = get_new_cutouts(images_list)
    update_config(images_list[0].split('/')[7], last_update, ids)
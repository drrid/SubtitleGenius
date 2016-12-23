from requests import get
from bs4 import BeautifulSoup
from fuzzywuzzy import process
import os

s_url = "https://subscene.com"


def get_clean_title(title):
	base_url = get("https://www.google.com/search?q={}+site%3Aimdb.com".format(title))
	soup = BeautifulSoup(base_url.content, "html.parser")
	ftitle = soup.find("h3", class_="r").get_text()

	return ftitle[:-14]


def get_sub_base_url(title):
	title = title.replace(" ", "+")
	base_url = get("https://subscene.com/subtitles/title?q={}".format(title))
	soup = BeautifulSoup(base_url.content, "html.parser")

	if not soup.find(class_="exact"):
		return "No subtitle for this title"

	url = s_url + soup.find("div", class_="title") \
		.find("a") \
		.get('href') + "/arabic"

	return url


def get_sub_url(url, filename):
	base_url = get(url)
	soup = BeautifulSoup(base_url.content, "html.parser")

	titles = []
	subs = []
	for sub in soup.find_all("td", class_="a1"):
		title = sub.a \
			.find_all("span")[1] \
			.get_text() \
			.strip()

		titles.append(title)
		subs.append(sub)

	result = process.extractOne(filename, titles)[0]
	index = titles.index(result)

	return s_url + subs[index].a.get("href")


def download_sub(url):
	base_url = get(url)
	soup = BeautifulSoup(base_url.content, "html.parser")
	d_url = s_url + soup.find("div", class_="download").a.get("href")


	return d_url


def scan_files(path):
	files = []
	for root, dirs, files in os.walk(path):
		for file in files:

			full_path = os.path.join(root, file)
			cond = (file.endswith("mp4") or file.endswith("avi") or file.endswith("mkv")) \
				   and (os.path.getsize(full_path) > 700000000)

			if cond:
				print file
				files.append(file[:-4])
	return files



if __name__ == '__main__':
	# print get_sub_url("https://subscene.com/subtitles/the-autopsy-of-jane-doe",
	# 			  "The.Autopsy.of.Jane.Doe.2016.720p.WEB-DL.800MB.ShAaNiG")

	# print download_sub("https://subscene.com/subtitles/the-autopsy-of-jane-doe/english/1469070")

	scan_files("/home/drrid/freespace")
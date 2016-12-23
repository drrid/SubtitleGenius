from requests import get
from bs4 import BeautifulSoup
from fuzzywuzzy import process
import os

s_url = "https://subscene.com"


def get_clean_title(title):
	base_url = get("https://www.google.com/search?q={}+site%3Aimdb.com".format(title))
	soup = BeautifulSoup(base_url.content, "html.parser")

	if soup.find("h3", class_="r"):
		ftitle = soup.find("h3", class_="r").get_text()
		return ftitle[:-14]


def get_sub_base_url(title, lang):
	title = title.replace(" ", "+")
	base_url = get("https://subscene.com/subtitles/title?q={}".format(title))
	soup = BeautifulSoup(base_url.content, "html.parser")

	if not soup.find(class_="exact"):
		return "No subtitle for this title"

	url = s_url + soup.find("div", class_="title") \
		.find("a") \
		.get('href') + "/{}".format(lang)

	return url


def get_sub_url(url, filename):
	if 'http' in url:
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

		if not process.extractOne(filename, titles):
			return "No subtitle"
		result = process.extractOne(filename, titles)[0]
		index = titles.index(result)

		return s_url + subs[index].a.get("href")


def download_sub(url, filename):
	filename = filename[:-3] + 'zip'
	base_url = get(url)
	soup = BeautifulSoup(base_url.content, "html.parser")
	d_url = s_url + soup.find("div", class_="download").a.get("href")

	r = get(d_url, stream=True)
	with open(filename, 'wb') as f:
		for chunck in r.iter_content(chunk_size=1024):
			if chunck:
				f.write(chunck)


def scan_files(path):
	titles = []
	for root, dirs, files in os.walk(path):
		for file in files:

			full_path = os.path.join(root, file)
			cond = (file.endswith("mp4") or file.endswith("avi") or file.endswith("mkv")) \
				   and (os.path.getsize(full_path) > 700000000)

			if cond:
				titles.append(full_path)

	return titles


def clean_filename(file):
	ignore = ['shaanig', 'yify', '800mb', '900mb', '1.7gb', '1.2gb', 'web-dl', 'hdrip',
			  'bluray', '720p', '1080p', '1gb', '6ch', 'x265', 'x264', 'dts-jyk', 'ac3-etrg',
			  'hc', 'xvid', 'dvdrip']

	if file.count('.') > 2:
		c_title = ' '.join([word if word.lower() not in ignore else '' for word in file.split('.')])
	else:
		c_title = ' '.join([word if word.lower() not in ignore else '' for word in file.split(' ')])

	return c_title


if __name__ == '__main__':

	# scan for movies
	files = scan_files("/home/drrid/freespace")
	print "***** Found {} movies".format(len(files))

	for file in files:
		# get clean titles
		file_name = file.split('/')[-1][:-4]
		print "***** Getting clean title for " + file
		c_filename = clean_filename(file_name)
		c_title = get_clean_title(c_filename)
		print c_title

		# get subscene.com
		b_url = get_sub_base_url(c_title, "english")
		sub_url = get_sub_url(b_url, file_name)
		print sub_url

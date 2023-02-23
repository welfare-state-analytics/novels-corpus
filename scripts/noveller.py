from kblab import Archive
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import time
from pathlib import Path
import zipfile
from ebooklib import epub
import zipfile
from lxml import etree

romaner=[{"meta.host_title": "Welfare state analytics"},"https://datalab.kb.se"]
blm=[{"label": "BONNIERS", "tags": "issue"},"https://datalab.kb.se"]
dn=[{"tags": "issue"},"https://betalab.kb.se"]


def get_content(filter=romaner,max_number=1):
    """API call to obtain a list of all books from kblab. 
    Args:
        filter (dictionary): A dictionary containing the filters for the packages in the betalab query.

        max_number (int): An integer specifying the highest number of packages to query.
    Returns:
        books (list): a list containing a list of responses from requests.get, containing alto-xml files.
    """
    home_dir=str(Path.home())
    with open(f'{home_dir}/Path/to/API_credentials', 'r') as file:
        pw = file.read().replace('\n', '')

    a = Archive(filter[1], auth=("demo", pw))
    books=[]
    xmlns='http://www.loc.gov/standards/alto/ns-v2#'
    for package_id in a.search(filter[0], max=max_number):
        write_root=etree.Element(package_id)
        page_index=1
        image_links=[]
        for x in a.get(package_id):
            if "jp" in x:
                image_links.append(f"{filter[1]}/{package_id}/{x}/_view")
            if "xml" in x:
                for i in range(5):
                    backoff_time = 0.1 * (2 ** i)
                    page=requests.get(f"{filter[1]}/{package_id}/{x}", auth=HTTPBasicAuth("demo", pw),stream=True)
                    if page.status_code == 200:
                        tree= ET.ElementTree(ET.fromstring(page.text))
                        """ Extract text content from ALTO xml file """
                        pb=etree.SubElement(write_root, "pb")
                        pb.set("n",f"{page_index}")
                        pb.set("facs",f"{image_links[page_index-1]}")
                        #contentinpage set here
                        # Find all <TextLine> elements
                        for lines in tree.iterfind('.//{%s}TextLine' % xmlns):
                            # New line after every <TextLine> element
                            # Find all <String> elements
                            block=[]

                            for line in lines.findall('{%s}String' % xmlns):
                                # Check if there are no hyphenated words
                                if ('SUBS_CONTENT' not in line.attrib and 'SUBS_TYPE' not in line.attrib):
                                # Get value of attribute @CONTENT from all <String> elements
                                    block.append( line.attrib.get('CONTENT') )
                                else:
                                    if ('HypPart1' in line.attrib.get('SUBS_TYPE')):
                                        block.append(line.attrib.get('SUBS_CONTENT'))
                            block=" ".join(block)
                            if block!=" ":
                                if "<" in block or ">" in block:
                                    block=block.replace("<","")
                                    block=block.replace(">","")
                                content_in_page=etree.SubElement(write_root, "p")
                                content_in_page.text=block
                        page_index+=1
                        break
                    else:
                        print(f"{filter[1]}/{package_id}/{x} failed")
                        time.sleep(backoff_time)

        books.append(etree.tostring(write_root, pretty_print=True))
    return books



def get_ids(filter=romaner,max_number=1):
    """function to return all ids
    """
    home_dir=str(Path.home())
    with open(f'{home_dir}/Path/to/API_credentials', 'r') as file:
        pw = file.read().replace('\n', '')

    a = Archive(filter[1], auth=("demo", pw))
    ids=[]
    for package_id in a.search(filter[0], max=max_number):
        ids.append(package_id)
    return ids


if __name__ == "__main__":
    for content,id in zip(get_content(),get_ids()):
        book = epub.EpubBook()

        # set metadata

        book = epub.EpubBook()

        # set metadata
        book.set_identifier(id)
        book.set_title("Sample book")
        book.set_language("sv")


        # create content in one chapter
        c1 = epub.EpubHtml(title=id, file_name="content.xhtml", lang="sv")
        c1.content = content
        book.add_item(c1)

        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # define CSS style
        style = "BODY {color: white;}"
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style,
        )

        # add CSS file
        book.add_item(nav_css)

        # basic spine
        book.spine = ["nav", c1]

        # write to the file
        epub.write_epub(f"{id}.epub", book)
        newpath = f"book unzipped/{id}" 
        Path(newpath).mkdir(parents=True, exist_ok=True)


        with zipfile.ZipFile(f"{id}.epub", 'r') as zip_ref:
            zip_ref.extractall(newpath)
        Path(f"{id}.epub").unlink()
import os
import random
import shutil
from ebooklib import epub
def test_epub():
    books=os.listdir("/Users/liamtabibzadeh/Documents/liams_noveller/book unzipped")

    if len(books)>100:
        
        test=random.sample(books,100)
        
        for x in test:
            if not os.path.exists("test_epub"):
                os.makedirs("test_epub")
            shutil.make_archive(f"test_epub/{x}", 'zip', f"/Users/liamtabibzadeh/Documents/liams_noveller/book unzipped/{x}")
            os.rename(f"test_epub/{x}.zip", f"test_epub/{x}.epub")
            epub.read_epub(f"test_epub/{x}.epub")
            os.remove(f"test_epub/{x}.epub")
    else: 
        for x in books:
            if not os.path.exists("test_epub"):
                os.makedirs("test_epub")
            shutil.make_archive(f"test_epub/{x}", 'zip', f"/Users/liamtabibzadeh/Documents/liams_noveller/book unzipped/{x}")
            os.rename(f"test_epub/{x}.zip", f"test_epub/{x}.epub")
            epub.read_epub(f"test_epub/{x}.epub")
            os.remove(f"test_epub/{x}.epub")
    #if len(os.listdir("test_epub"))==0:
        #os.remove("test_epub")

if __name__ == "__main__":
    test_epub()
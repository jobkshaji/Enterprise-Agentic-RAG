from bs4 import BeautifulSoup
import logfire

def parse_html(file_path :str):
    """
    Parse html content using beautifulSoup
    """
    with logfire.span("html parsing",filename=file_path):
        try:
            with open(file_path,'r',encoding='utf-8',errors='ignore') as f:
                content=f.read()

                soup=BeautifulSoup(content,"html.parser")

                for script in soup(["script","style","meta","noscript"]): # removing junk details like tags like scripts,metadata etc
                    script.decompose()

                text=soup.get_text(separator="\n") # extract text

                lines=(line.strip() for line in text.splitlines())
                chunks=(phrase.strip() for line in lines for phrase in line.split(" "))
                text_clean='\n'.join(chunk for chunk in chunks if chunk)

                return text_clean
        except Exception as e:  
            logfire.error(f"html parse failed :{e}")
            raise e


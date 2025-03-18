import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
from datetime import datetime, timezone
from bson.objectid import ObjectId

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ForumPersistence:

    def __init__(self, db_name='forumadrenaline', collection_name='posts'):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def store_post(self, post_data):
        """
        Armazena os dados de um post no MongoDB.
        """
        post_data['_id'] = ObjectId() 
        self.collection.insert_one(post_data)

    def get_all_posts(self):
        """
        Recupera todos os posts armazenados no banco de dados.
        """
        return list(self.collection.find())

    def get_top_reacted_posts(self, limit=10):
        """
        Recupera os posts com maior quantidade de reações.
        """
        return list(self.collection.find().sort('reactions', -1).limit(limit))

    def get_all_users(self):
        """
        Recupera uma lista de todos os usuários que postaram.
        """
        return self.collection.distinct('user')

    def get_posts_by_user(self, username):
        """
        Recupera todos os posts de um determinado usuário.
        """
        return list(self.collection.find({'user': username}))
    
    def test_connection(self):
        """
        Testa a comunicação com o banco de dados MongoDB.
        """
        try:
           
            test_document = {"test_key": "test_value", "timestamp": datetime.now(timezone.utc)}
            self.collection.insert_one(test_document)
            logging.info("Documento de teste inserido com sucesso.")

            retrieved_document = self.collection.find_one({"test_key": "test_value"})
            if retrieved_document:
                logging.info(f"Documento de teste recuperado com sucesso: {retrieved_document}")
             
                self.collection.delete_one({"_id": retrieved_document["_id"]})
                logging.info("Documento de teste excluído com sucesso.")
                return True
            else:
                logging.error("Falha ao recuperar o documento de teste.")
                return False
        except Exception as e:
            logging.error(f"Erro ao testar a comunicação com o banco de dados: {e}")
            return False

def collect_data_from_adrenaline(url):
    # Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(url)

    wait = WebDriverWait(driver, 20) 

    post_data = None

    try:
        logging.info("Verificando se a página foi carregada completamente...")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        logging.info("A página foi carregada completamente.")

        logging.info("Tentando encontrar o título do post...")
        title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.p-title-value')))
        title = title_element.text.strip() if title_element else ""
        logging.info(f"Título encontrado: {title}")
        
        logging.info("Tentando encontrar o conteúdo do post...")
        post_content_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bbWrapper')))
        post_content = post_content_element.text.strip() if post_content_element else ""
        logging.info(f"Conteúdo do post encontrado: {post_content}")
        
        logging.info("Tentando encontrar o usuário do post...")
        user_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.username')))
        user = user_element.text.strip() if user_element else "unknown"
        logging.info(f"Usuário encontrado: {user}")
        
        post_date = datetime.now(timezone.utc)  
        
        logging.info("Tentando encontrar o número de reações...")
        try:
            reactions_elements = driver.find_elements(By.XPATH, '/html/body/div[1]/div[4]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div/article[8]/div/div[2]/div/footer/div[2]/ul/li/span/img')
            reactions = len(reactions_elements)
            logging.info(f"Número de reações encontrado: {reactions}")
        except Exception as e:
            logging.warning(f"Não foi possível encontrar o número de reações: {e}")
            reactions = 0
        
        logging.info("Tentando encontrar os comentários...")
        comments = []
        comment_elements = driver.find_elements(By.CSS_SELECTOR, 'div.message-inner')
        for comment_element in comment_elements:
            try:
                comment_user_element = comment_element.find_element(By.CSS_SELECTOR, 'a.username')
                comment_user = comment_user_element.text.strip() if comment_user_element else "unknown"
                
                comment_date_element = comment_element.find_element(By.CSS_SELECTOR, 'time')
                comment_date = comment_date_element.get_attribute('datetime') if comment_date_element else ""
                
                comment_content_element = comment_element.find_element(By.CSS_SELECTOR, 'div.bbWrapper')
                comment_content = comment_content_element.text.strip() if comment_content_element else ""
                
                try:
                    comment_reactions_elements = comment_element.find_elements(By.XPATH, 'footer/div[2]/ul/li/span/img')
                    comment_reactions = len(comment_reactions_elements)
                except Exception as e:
                    logging.warning(f"Não foi possível encontrar o número de reações do comentário: {e}")
                    comment_reactions = 0

                comment_data = {
                    'comment_user': comment_user,
                    'comment_date': comment_date,
                    'comment_content': comment_content,
                    'comment_reactions': comment_reactions
                }
                comments.append(comment_data)
            except Exception as e:
                logging.warning(f"Erro ao processar um comentário: {e}")

        post_data = {
            'collection_date': datetime.now(timezone.utc),
            'post_url': url,
            'post_date': post_date,
            'user': user,
            'title': title,
            'post_content': post_content,
            'reactions': reactions,
            'comments': comments
        }

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.info("Capturando a tela no momento do erro...")
        driver.save_screenshot('error_screenshot.png')
        logging.info("Captura de tela salva como 'error_screenshot.png'.")
    
    finally:
        driver.quit()
    
    return post_data or {}

if __name__ == "__main__":
    forum_persistence = ForumPersistence()

    if forum_persistence.test_connection():
        logging.info("Comunicação com o MongoDB está funcionando corretamente.")
    else:
        logging.error("Falha na comunicação com o MongoDB.")

    adrenaline_url = 'https://forum.adrenaline.com.br/threads/jogos-online-gratuitos.89331/'
    post_data = collect_data_from_adrenaline(adrenaline_url)

    if post_data:
        forum_persistence.store_post(post_data)

        users = forum_persistence.get_all_users()
        print("Todos os usuários:")
        for user in users:
            print(user)

        for user in users:
            user_posts = forum_persistence.get_posts_by_user(user)
            print(f"Posts do usuário '{user}':")
            for post in user_posts:
                print(f"  - Título: {post['title']}")
                print(f"    Data do Post: {post['post_date']}")
                print(f"    Conteúdo do Post: {post['post_content']}")
                print(f"    Reações: {post['reactions']}")
                print("    Comentários:")
                for comment in post.get('comments', []):
                    print(f"      - Usuário: {comment['comment_user']}")
                    print(f"        Data: {comment['comment_date']}")
                    print(f"        Conteúdo: {comment['comment_content']}")
                    print(f"        Reações: {comment['comment_reactions']}")

        all_posts = forum_persistence.get_all_posts()
        print("Todos os posts armazenados:", all_posts)

        top_reacted_posts = forum_persistence.get_top_reacted_posts()
        print("Top 10 posts com mais reações:", top_reacted_posts)
    else:
        print("Nenhum dado foi coletado.")
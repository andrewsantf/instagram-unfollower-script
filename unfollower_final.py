import time
import random
import os
import json
import getpass
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Funções Auxiliares ---

def parse_instagram_json(file_path):
    """
    Lê e processa um ficheiro JSON da exportação do Instagram (VERSÃO FINAL E À PROVA DE FALHAS)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        usernames = []
        data_to_process = []

        if isinstance(data, list):
            data_to_process = data
        elif isinstance(data, dict):
            # Compatível com o formato de 'following.json'
            data_to_process = data.get('relationships_following', [])
        else:
            raise ValueError(f"Formato de ficheiro JSON não reconhecido em {os.path.basename(file_path)}")

        for item in data_to_process:
            user_data_list = item.get('string_list_data', [])
            if user_data_list:
                username = user_data_list[0].get('value')
                if username:
                    usernames.append(username)
        
        return usernames

    except FileNotFoundError:
        print(f"\nERRO: O ficheiro não foi encontrado em: {file_path}")
        return None
    except Exception as e:
        print(f"\nERRO: Ocorreu um erro ao ler o ficheiro {os.path.basename(file_path)}: {e}")
        return None

def load_whitelist():
    """ Carrega a whitelist. """
    whitelist = set()
    try:
        if not os.path.exists('whitelist.txt'):
            open('whitelist.txt', 'w').close()
        with open('whitelist.txt', 'r', encoding='utf-8') as f:
            whitelist = {line.strip().lower() for line in f if line.strip()}
    except Exception: pass
    return whitelist

# --- Função Principal de Automação ---

def run_unfollow_process(username, password, users_to_unfollow, daily_limit):
    """
    Executa o processo de "unfollow" usando a abordagem semi-automática.
    """
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'})

    # PASSO 1: LOGIN SEMI-AUTOMÁTICO COM PLAYWRIGHT
    print("\nA iniciar o navegador para login manual...")
    try:
        with sync_playwright() as p:
            # O NAVEGADOR AGORA É VISÍVEL PARA INTERVENÇÃO MANUAL
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            print("A preencher os seus dados...")
            page.goto("https://www.instagram.com/accounts/login/")
            page.fill("input[name='username']", username)
            page.fill("input[name='password']", password)
            page.click("button[type='submit']")

            # PAUSA PARA INTERVENÇÃO MANUAL
            print("\n" + "="*50)
            print("  AÇÃO NECESSÁRIA  ".center(50))
            print("="*50)
            print("O navegador está aberto.")
            print("1. Lide com quaisquer ecrãs de 'Guardar informações' (clique em 'Agora não').")
            print("2. Complete qualquer verificação de segurança (2FA), se aparecer.")
            print("3. QUANDO VIR A PÁGINA INICIAL DO INSTAGRAM, volte a este terminal.")
            input("4. Prima Enter aqui para continuar...")
            # -----------------------------------------------------------
            
            print("\nA verificar o login e a extrair credenciais...")
            page.wait_for_selector("svg[aria-label='Página inicial']", timeout=60000)
            
            cookies = page.context.cookies()
            csrf_token = next((cookie['value'] for cookie in cookies if cookie['name'] == 'csrftoken'), None)
            if not csrf_token:
                raise Exception("Não foi possível encontrar o CSRF token. Certifique-se de que o login foi concluído.")
            
            session.cookies.update({cookie['name']: cookie['value'] for cookie in cookies})
            session.headers.update({
                'x-csrftoken': csrf_token,
                'x-ig-app-id': '936619743392459'
            })
            print("Credenciais de sessão obtidas com sucesso. A fechar o navegador.")
            browser.close()
    except Exception as e:
        print(f"\nERRO CRÍTICO ao fazer login: {e}")
        return

    # PASSO 2: UNFOLLOW COM API/REQUESTS
    total_to_unfollow = min(len(users_to_unfollow), daily_limit)
    unfollowed_count = 0
    print(f"\nA iniciar o processo de 'unfollow' por API para {total_to_unfollow} utilizadores...")

    for user_to_unfollow_username in users_to_unfollow:
        if unfollowed_count >= daily_limit:
            print("Limite diário atingido.")
            break
        
        print(f"\n({unfollowed_count + 1}/{total_to_unfollow}) A processar @{user_to_unfollow_username}...")
        
        try:
            user_info_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={user_to_unfollow_username}"
            user_info_resp = session.get(user_info_url)
            
            if user_info_resp.status_code == 404:
                print(f"Utilizador @{user_to_unfollow_username} não encontrado. A saltar.")
                time.sleep(1)
                continue

            user_info_resp.raise_for_status()
            target_user_id = user_info_resp.json()['data']['user']['id']

            unfollow_url = f"https://www.instagram.com/api/v1/friendships/destroy/{target_user_id}/"
            unfollow_response = session.post(unfollow_url)
            unfollow_response.raise_for_status()

            if unfollow_response.json().get('status') == 'ok':
                unfollowed_count += 1
                print(f"Deixou de seguir @{user_to_unfollow_username} com sucesso. Total: {unfollowed_count}")
            else:
                print(f"AVISO: Resposta inesperada para @{user_to_unfollow_username}: {unfollow_response.text}. A saltar.")

        except Exception as e:
            print(f"ERRO ao processar @{user_to_unfollow_username}: {e}. A saltar.")

        # --- LÓGICA DE PAUSA INTELIGENTE ---
        # A cada 15 unfollows, faz uma pausa longa. Caso contrário, uma pausa curta.
        if unfollowed_count > 0 and unfollowed_count % 15 == 0:
            long_pause_duration = random.randint(60, 90)
            print(f"PAUSA ESTRATÉGICA: Atingiu {unfollowed_count} unfollows. A aguardar {long_pause_duration} segundos...")
            time.sleep(long_pause_duration)
        else:
            short_pause_duration = random.randint(7, 18)
            print(f"A aguardar {short_pause_duration} segundos para a próxima ação...")
            time.sleep(short_pause_duration)

    print(f"\n--- Processo concluído. Total de 'unfollows': {unfollowed_count} ---")

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    print("="*50)
    print("  Ferramenta Profissional de Unfollow (Método Semi-Automático)  ")
    print("="*50)

    print("\n--- PASSO 1: CREDENCIAIS ---")
    user_login = input("Digite o seu nome de utilizador do Instagram: ")
    user_pass = getpass.getpass("Digite a sua palavra-passe do Instagram (não será visível): ")
    user_limit = int(input("Digite o limite de 'unfollows' para esta sessão (ex: 50): "))
    
    # ### INÍCIO DA ALTERAÇÃO ###
    print("\n--- PASSO 2: A PROCURAR FICHEIROS DE DADOS ---")
    
    # O script assume que os ficheiros JSON estão na mesma pasta que ele.
    script_dir = os.getcwd() 
    print(f"A procurar na pasta do programa: {script_dir}")

    # Definir os nomes dos ficheiros esperados
    followers_filename = 'followers_1.json'
    following_filename = 'following.json'

    # Construir os caminhos completos
    followers_path_auto = os.path.join(script_dir, followers_filename)
    following_path_auto = os.path.join(script_dir, following_filename)

    # Verificar o ficheiro de seguidores
    if os.path.exists(followers_path_auto):
        print(f"✓ Ficheiro '{followers_filename}' encontrado automaticamente.")
        followers_path = followers_path_auto
    else:
        print(f"✗ Ficheiro '{followers_filename}' não encontrado na pasta do programa.")
        followers_path = input(f"Por favor, cole o caminho completo para o seu ficheiro '{followers_filename}': ")

    # Verificar o ficheiro de 'a seguir'
    if os.path.exists(following_path_auto):
        print(f"✓ Ficheiro '{following_filename}' encontrado automaticamente.")
        following_path = following_path_auto
    else:
        print(f"✗ Ficheiro '{following_filename}' não encontrado na pasta do programa.")
        following_path = input(f"Por favor, cole o caminho completo para o seu ficheiro '{following_filename}': ")
    # ### FIM DA ALTERAÇÃO ###
    
    followers = parse_instagram_json(followers_path.strip())
    following = parse_instagram_json(following_path.strip())

    if followers is None or following is None:
        exit()

    print("\n--- PASSO 3: ANÁLISE ---")
    whitelist = load_whitelist()
    followers_set = set(u.lower() for u in followers)
    following_set = set(u.lower() for u in following)
    non_followers_raw = following_set - followers_set
    non_followers_final = sorted([user for user in non_followers_raw if user.lower() not in whitelist])
    
    print(f"\nAnálise completa: {len(non_followers_final)} contas não o seguem de volta (e não estão protegidas).")
    if not non_followers_final:
        print("\nParabéns! Nenhuma conta para deixar de seguir.")
        exit()

    print("\n--- PASSO 4: AÇÃO ---")
    confirm = input(f"Encontradas {len(non_followers_final)} contas. Quer começar o processo? (s/n): ").lower()

    if confirm == 's':
        run_unfollow_process(user_login, user_pass, non_followers_final, user_limit)
    else:
        print("Operação cancelada.")
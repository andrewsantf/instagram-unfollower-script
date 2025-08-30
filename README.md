# Ferramenta de Unfollow para Instagram (No Terminal)

Um script em Python para analisar os seus dados do Instagram e automatizar o processo de deixar de seguir utilizadores que não o seguem de volta. Este projeto utiliza os ficheiros de dados oficiais fornecidos pelo Instagram para garantir a precisão.

## Aviso
A automação de interações viola os Termos de Serviço do Instagram. Utilize esta ferramenta com moderação e por sua conta e risco. O uso excessivo pode levar ao bloqueio temporário ou permanente da sua conta.

## Como Usar

**1. Descarregue os Seus Dados do Instagram:**
   - Abra a sua conta do Instagram.
   - Vá a **Configurações**.
   - Clique em **Central de Contas** (geralmente a primeira opção).
   - Na secção "Configurações de contas", clique em **Suas informações e permissões**.
   - Escolha **Exportar suas informações**.
   - Siga os passos no ecrã, garantindo que seleciona o formato de download **JSON**.
   - Após algum tempo, irá receber um email da Meta para descarregar um ficheiro `.zip`. Descompacte-o.
   - Dentro da pasta descompactada, navegue até `connections/followers_and_following/`. Os ficheiros que precisa são **`followers_1.json`** e **`following.json`**.

**2. Prepare o Ambiente:**
   - Descarregue os ficheiros deste repositório (no GitHub, clique no botão verde "Code" > "Download ZIP").
   - Descompacte e, na pasta do projeto, crie um ambiente virtual para manter as dependências organizadas:
     ```
     python -m venv venv
     ```
   - Ative o ambiente virtual:
     ```
     venv\Scripts\activate
     ```

**3. Instale as Dependências:**
   - Com o ambiente ativado, instale as bibliotecas necessárias com este comando:
     ```
     pip install -r requirements.txt
     ```
   - O Playwright precisa de descarregar os navegadores que ele controla. Execute este comando (só precisa de o fazer uma vez):
     ```
     playwright install
     ```

**4. Execute o Script:**
   - Coloque os seus ficheiros `followers_1.json` e `following.json` na mesma pasta do script.
   - Se quiser usar uma lista de exceções (contas que o script nunca deve deixar de seguir), crie um ficheiro `whitelist.txt` e adicione um nome de utilizador por linha.
   - Execute o script principal no terminal:
     ```
     python unfollower_script.py
     ```
   - Siga as instruções que aparecem no ecrã para inserir o seu nome de utilizador, palavra-passe e o limite de unfollows.

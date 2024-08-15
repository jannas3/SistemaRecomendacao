import streamlit as st
import time
from math import sqrt

# Inicializando dados persistentes no Streamlit
if 'avaliacoesUsers' not in st.session_state:
    st.session_state.avaliacoesUsers = {
        'Ana': {
            'Freddy x Jason': 2.5,
            'O Ultimato Bourne': 3.5,
            'Star Trek': 3.0,
            'Star Wars': 3.0,
            'Exterminador do Futuro': 3.5,
            'Norbit': 2.5
        },
        'Marcos': {
            'Freddy x Jason': 3.0,
            'O Ultimato Bourne': 3.5,
            'Star Trek': 1.5,
            'Star Wars': 3.0,
            'Exterminador do Futuro': 5.0,
            'Norbit': 3.5
        },
    }

if 'avaliacoesModel' not in st.session_state:
    st.session_state.avaliacoesModel = {
        'Model': {'Freddy x Jason', 'O Ultimato Bourne', 'Star Trek', 'Star Wars', 'Exterminador do Futuro', 'Norbit'}
    }

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'menu' not in st.session_state:
    st.session_state.menu = 'main'

if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = None

avaliacoesUsers = st.session_state.avaliacoesUsers
avaliacoesModel = st.session_state.avaliacoesModel

# Funções de recomendação (mantidas as mesmas)
def knn(base, user1, user2):
    si = {item for item in base[user1] if item in base[user2]}
    if len(si) == 0:
        return 0
    
    soma = sum(pow(base[user1][item] - base[user2][item], 2) for item in si)
    return 1 / (1 + sqrt(soma))

def getSim(base, user):
    sim = [(knn(base, user, other_user), other_user) for other_user in base if other_user != user]
    sim.sort(reverse=True)
    return sim[:20]

def getRecomUser(base, user):
    totais = {}
    somaSim = {}

    for other_user in base:
        if other_user == user:
            continue
        sim = knn(base, user, other_user)

        if sim <= 0:
            continue
        
        for item in base[other_user]:
            if item not in base[user] or base[user][item] == 0:
                totais.setdefault(item, 0)
                totais[item] += base[other_user][item] * sim
                somaSim.setdefault(item, 0)
                somaSim[item] += sim
                
    rankings = [(total / somaSim[item], item) for item, total in totais.items()]
    rankings.sort(reverse=True)
    return rankings[:20]

# Funções de gerenciamento de usuários e filmes
def newUser(user):
    if user in st.session_state.avaliacoesUsers:
        return False
    st.session_state.avaliacoesUsers[user] = {}
    return True

def userExiste(user):
    return user in st.session_state.avaliacoesUsers

def addMovie(movie, user, nota):
    if movie in st.session_state.avaliacoesModel['Model']:
        if movie in st.session_state.avaliacoesUsers[user]:
            return False
        else:
            st.session_state.avaliacoesUsers[user][movie] = nota
            return True
    return False

def historicoFilmes(nome):
    return list(st.session_state.avaliacoesUsers[nome].items())

def excluirFilme(user, movieDel):
    if movieDel in st.session_state.avaliacoesModel['Model'] and movieDel in st.session_state.avaliacoesUsers[user]:
        del st.session_state.avaliacoesUsers[user][movieDel]
        return True
    return False

def mudarNota(user, movie, nota):
    if movie in st.session_state.avaliacoesUsers[user]:
        st.session_state.avaliacoesUsers[user][movie] = nota
        return True
    return False

def excluirPerfil(user):
    if user in st.session_state.avaliacoesUsers:
        del st.session_state.avaliacoesUsers[user]
        return True
    return False

# Funções para Streamlit
def main_menu():
    st.title("Sistema de Recomendação")
    st.write("1 - Acessar Perfil")
    st.write("2 - Criar Novo Perfil")
    st.write("3 - Sair")
    return st.text_input("Escolha uma opção:", key='main_menu_choice')

def perfil_menu():
    st.title("Menu de Usuário")
    st.write("1 - Histórico de filmes")
    st.write("2 - Adicionar filme")
    st.write("3 - Excluir filme")
    st.write("4 - Filmes recomendados")
    st.write("5 - Mudar nota")
    st.write("6 - Excluir perfil")
    st.write("7 - Voltar ao menu principal")
    return st.text_input("Escolha uma opção:", key='perfil_menu_choice')

def criar_perfil():
    st.title("Novo Usuário")
    name = st.text_input("Digite seu nome de usuário:", key='criar_perfil_name')
    if st.button("Criar"):
        if newUser(name):
            st.success(f"Usuário {name} criado com sucesso!")
        else:
            st.error("Nome já existente, crie um novo.")

def acessar_perfil():
    nome = st.session_state.current_user
    st.write(f"Bem-vindo, {nome}!")
    choice = perfil_menu()
    if choice == "1":
        historico = historicoFilmes(nome)
        if historico:
            st.write("Histórico de Filmes:")
            for item in historico:
                st.write(item)
        else:
            st.write("Não há filmes adicionados.")
    elif choice == "2":
        filmes_disponiveis = list(avaliacoesModel['Model'] - st.session_state.avaliacoesUsers[nome].keys())
        if filmes_disponiveis:
            st.write("Filmes disponíveis:")
            for filme in filmes_disponiveis:
                st.write(filme)
            movie = st.selectbox("Escolha um filme para adicionar:", filmes_disponiveis, key='adicionar_filme_select')
            st.session_state.selected_movie = movie
            nota = st.number_input("Qual a nota desse filme? (0.0 - 5.0)", min_value=0.0, max_value=5.0, step=0.5, key='adicionar_filme_nota')
            if st.button("Adicionar", key='adicionar_filme_button'):
                if addMovie(movie, nome, nota):
                    st.success(f"Filme {movie} adicionado com nota {nota}!")
                else:
                    st.error("Filme não encontrado ou já adicionado.")
        else:
            st.write("Sem filmes disponíveis para adicionar.")
    elif choice == "3":
        movie = st.text_input("Qual filme deseja excluir?", key='excluir_filme')
        if st.button("Excluir", key='excluir_filme_button'):
            if excluirFilme(nome, movie):
                st.success(f"Filme {movie} excluído!")
            else:
                st.error("Filme não encontrado ou não está na lista.")
    elif choice == "4":
        recomendacoes = getRecomUser(st.session_state.avaliacoesUsers, nome)
        if recomendacoes:
            st.write("Filmes Recomendados:")
            for score, movie in recomendacoes:
                st.write(f"{movie}: {score:.2f}")
        else:
            st.write("Sem filmes para recomendar.")
    elif choice == "5":
        movie = st.text_input("Qual filme deseja mudar a nota?", key='mudar_nota_filme')
        nota = st.number_input("Nova nota:", min_value=0.0, max_value=5.0, step=0.5, key='mudar_nota_valor')
        if st.button("Mudar Nota", key='mudar_nota_button'):
            if mudarNota(nome, movie, nota):
                st.success(f"Nota do filme {movie} modificada para {nota}!")
            else:
                st.error("Filme não encontrado no histórico.")
    elif choice == "6":
        if st.button("Excluir Perfil", key='excluir_perfil_button'):
            if excluirPerfil(nome):
                st.success(f"Perfil {nome} excluído!")
                st.session_state.current_user = None
                st.session_state.menu = 'main'
    elif choice == "7":
        st.session_state.current_user = None
        st.session_state.menu = 'main'

def main():
    if st.session_state.menu == 'main':
        menu_choice = main_menu()
        if menu_choice == "1":
            nome = st.text_input("Digite seu nome de usuário:", key='login_nome')
            if st.button("Login", key='login_button'):
                if userExiste(nome):
                    st.session_state.current_user = nome
                    st.session_state.menu = 'perfil'
                else:
                    st.error("Usuário não encontrado.")
        elif menu_choice == "2":
            criar_perfil()
        elif menu_choice == "3":
            st.stop()
    elif st.session_state.menu == 'perfil':
        acessar_perfil()

if __name__ == "__main__":
    main()

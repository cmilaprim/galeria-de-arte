from datetime import datetime, timedelta

# Imports diretos do projeto principal
from src.models.obra_model import ObraDeArte, StatusObra
from src.models.artista_model import Artista, StatusArtista
from src.models.transacao_model import Transacao
from src.database.manager import DatabaseManager

def populate_database():
    """Popula o banco de dados com dados de teste para relatórios"""
    print("Populando banco de dados com dados de teste...")
    
    db = DatabaseManager()
    
    artistas = [
        Artista(
            id_artista=None, 
            nome="Pablo Picasso",
            nascimento="25/10/1881",
            nacionalidade="Espanhol",
            especialidade="Pintura, Escultura",
            status=StatusArtista.ATIVO,
            data_cadastro=datetime.now().strftime("%d/%m/%Y"),
            biografia="Artista cubista reconhecido mundialmente"
        ),
        Artista(
            id_artista=None,
            nome="Tarsila do Amaral",
            nascimento="01/09/1886",
            nacionalidade="Brasileira",
            especialidade="Pintura",
            status=StatusArtista.ATIVO,
            data_cadastro=datetime.now().strftime("%d/%m/%Y"),
            biografia="Uma das principais artistas modernistas do Brasil"
        ),
        Artista(
            id_artista=None,
            nome="Claude Monet",
            nascimento="14/11/1840",
            nacionalidade="Francês",
            especialidade="Pintura Impressionista",
            status=StatusArtista.ATIVO,
            data_cadastro=datetime.now().strftime("%d/%m/%Y"),
            biografia="Fundador do movimento impressionista"
        ),
        Artista(
            id_artista=None,
            nome="Frida Kahlo",
            nascimento="06/07/1907",
            nacionalidade="Mexicana",
            especialidade="Pintura",
            status=StatusArtista.ATIVO,
            data_cadastro=datetime.now().strftime("%d/%m/%Y"),
            biografia="Artista mexicana conhecida por autorretratos e obras inspiradas na natureza"
        ),
        Artista(
            id_artista=None,
            nome="Alberto Giacometti",
            nascimento="10/10/1901",
            nacionalidade="Suíço",
            especialidade="Escultura",
            status=StatusArtista.ATIVO,
            data_cadastro=datetime.now().strftime("%d/%m/%Y"),
            biografia="Escultor e pintor suíço, conhecido por figuras alongadas"
        ),
        Artista(
            id_artista=None,
            nome="Yayoi Kusama",
            nascimento="22/03/1929",
            nacionalidade="Japonesa",
            especialidade="Instalação, Pintura",
            status=StatusArtista.ATIVO,
            data_cadastro=datetime.now().strftime("%d/%m/%Y"),
            biografia="Artista japonesa conhecida por padrões de pontos e instalações imersivas"
        )
    ]
    
    for artista in artistas:
        try:
            db.inserir_artista(artista)
            print(f"Artista inserido: {artista.nome}")
        except Exception as e:
            print(f"Erro ao inserir artista {artista.nome}: {e}")
    
    obras = [
        ObraDeArte(
            id_obra=None,
            titulo="Guernica",
            ano="1937",
            artista="Pablo Picasso",
            tipo="Pintura",
            tecnica="Óleo sobre tela",
            dimensoes="349 x 776 cm",
            localizacao="Sala Principal",
            preco=1500000.00,
            status=StatusObra.DISPONIVEL,
            data_cadastro=datetime.now().strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="Abaporu",
            ano="1928",
            artista="Tarsila do Amaral",
            tipo="Pintura",
            tecnica="Óleo sobre tela",
            dimensoes="85 x 73 cm",
            localizacao="Ala Modernista",
            preco=800000.00,
            status=StatusObra.VENDIDA,
            data_cadastro=(datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="Nenúfares",
            ano="1916",
            artista="Claude Monet",
            tipo="Pintura",
            tecnica="Óleo sobre tela",
            dimensoes="200 x 180 cm",
            localizacao="Ala Impressionista",
            preco=1200000.00,
            status=StatusObra.DISPONIVEL,
            data_cadastro=(datetime.now() - timedelta(days=15)).strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="As Duas Fridas",
            ano="1939",
            artista="Frida Kahlo",
            tipo="Pintura",
            tecnica="Óleo sobre tela",
            dimensoes="173 x 173 cm",
            localizacao="Sala de Exposições Temporárias",
            preco=950000.00,
            status=StatusObra.EM_EXPOSICAO,
            data_cadastro=(datetime.now() - timedelta(days=60)).strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="Operários",
            ano="1933",
            artista="Tarsila do Amaral",
            tipo="Pintura",
            tecnica="Óleo sobre tela",
            dimensoes="150 x 205 cm",
            localizacao="Ala Modernista",
            preco=750000.00,
            status=StatusObra.DISPONIVEL,
            data_cadastro=(datetime.now() - timedelta(days=45)).strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="A Persistência da Memória",
            ano="1931",
            artista="Pablo Picasso",
            tipo="Pintura",
            tecnica="Óleo sobre tela",
            dimensoes="24 x 33 cm",
            localizacao="Sala Principal",
            preco=1300000.00,
            status=StatusObra.VENDIDA,
            data_cadastro=(datetime.now() - timedelta(days=90)).strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="Figura Alongada",
            ano="1950",
            artista="Alberto Giacometti",
            tipo="Escultura",
            tecnica="Bronze",
            dimensoes="180 x 25 x 20 cm",
            localizacao="Jardim de Esculturas",
            preco=600000.00,
            status=StatusObra.DISPONIVEL,
            data_cadastro=(datetime.now() - timedelta(days=10)).strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="Infinity Nets",
            ano="2000",
            artista="Yayoi Kusama",
            tipo="Instalação",
            tecnica="Tinta e luz",
            dimensoes="Espaço imersivo",
            localizacao="Galeria Contemporânea",
            preco=450000.00,
            status=StatusObra.EM_EXPOSICAO,
            data_cadastro=(datetime.now() - timedelta(days=5)).strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="Polka Dots (Fotografia)",
            ano="2015",
            artista="Yayoi Kusama",
            tipo="Fotografia",
            tecnica="Impressão Fine Art",
            dimensoes="60 x 80 cm",
            localizacao="Ala Fotografia",
            preco=18000.00,
            status=StatusObra.DISPONIVEL,
            data_cadastro=(datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="Gravura Experimental",
            ano="1929",
            artista="Tarsila do Amaral",
            tipo="Gravura",
            tecnica="Xilogravura",
            dimensoes="40 x 30 cm",
            localizacao="Ala Gravuras",
            preco=22000.00,
            status=StatusObra.DISPONIVEL,
            data_cadastro=(datetime.now() - timedelta(days=120)).strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="Colagem Coletiva",
            ano="2023",
            artista=["Tarsila do Amaral", "Frida Kahlo"],
            tipo="Outro",
            tecnica="Colagem mista",
            dimensoes="100 x 120 cm",
            localizacao="Sala de Projetos",
            preco=35000.00,
            status=StatusObra.DISPONIVEL,
            data_cadastro=(datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="Pequena Escultura de Rua",
            ano="1987",
            artista="Alberto Giacometti",
            tipo="Escultura",
            tecnica="Resina patinada",
            dimensoes="75 x 20 x 18 cm",
            localizacao="Hall",
            preco=48000.00,
            status=StatusObra.DISPONIVEL,
            data_cadastro=(datetime.now() - timedelta(days=200)).strftime("%d/%m/%Y")
        ),
        ObraDeArte(
            id_obra=None,
            titulo="Instalação de Pontos",
            ano="2018",
            artista="Yayoi Kusama",
            tipo="Instalação",
            tecnica="Objetos e luz",
            dimensoes="Sala inteira",
            localizacao="Ala Instalações",
            preco=90000.00,
            status=StatusObra.EM_EXPOSICAO,
            data_cadastro=(datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y")
        )
    ]

    for obra in obras:
        try:
            id_gerado = db.inserir_obra(obra)
            obra._ObraDeArte__id_obra = id_gerado 
            print(f"Obra inserida: {obra.titulo} com ID {id_gerado}")
        except Exception as e:
            print(f"Erro ao inserir obra {obra.titulo}: {e}")
    
    transacoes = [
        Transacao(
            cliente="Museu de Arte Moderna",
            valor=750000.00,
            tipo="Venda",
            data_transacao=(datetime.now() - timedelta(days=25)).strftime("%d/%m/%Y"),
            data_cadastro=datetime.now().strftime("%d/%m/%Y"),
            observacoes="Venda para exposição permanente",
            obras=["Abaporu"] 
        ),
        Transacao(
            cliente="Colecionador Particular",
            valor=1300000.00,
            tipo="Venda",
            data_transacao=(datetime.now() - timedelta(days=85)).strftime("%d/%m/%Y"),
            data_cadastro=(datetime.now() - timedelta(days=85)).strftime("%d/%m/%Y"),
            observacoes="Venda para coleção particular",
            obras=["A Persistência da Memória"]  
        ),
        Transacao(
            cliente="Galeria Internacional de Arte",
            valor=250000.00,
            tipo="Empréstimo",
            data_transacao=(datetime.now() - timedelta(days=50)).strftime("%d/%m/%Y"),
            data_cadastro=(datetime.now() - timedelta(days=50)).strftime("%d/%m/%Y"),
            observacoes="Empréstimo para exposição internacional",
            obras=["As Duas Fridas"]  
        ),
        Transacao(
            cliente="Galeria de Arte Contemporânea",
            valor=90000.00,
            tipo="Aluguel",
            data_transacao=(datetime.now() - timedelta(days=10)).strftime("%d/%m/%Y"),
            data_cadastro=(datetime.now() - timedelta(days=10)).strftime("%d/%m/%Y"),
            observacoes="Aluguel para exposição temporária",
            obras=["Guernica", "Nenúfares"]  
        )
    ]
    
    for transacao in transacoes:
        try:
            db.inserir_transacao(transacao)
            print(f"Transação inserida: {transacao.tipo} - {transacao.cliente}")
        except Exception as e:
            print(f"Erro ao inserir transação {transacao.tipo}: {e}")
    
    print("\n" + "="*60)
    print("Banco de dados populado com sucesso!")
    print("="*60)
    print("\nObras com transações:")
    print("  - Abaporu (Venda)")
    print("  - A Persistência da Memória (Venda)")
    print("  - As Duas Fridas (Empréstimo)")
    print("  - Guernica (Aluguel)")
    print("  - Nenúfares (Aluguel)")
    print("\nVocê pode agora abrir a aplicação e testar o relatório de obras.")

if __name__ == "__main__":
    populate_database()
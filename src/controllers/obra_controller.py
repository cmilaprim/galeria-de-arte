from datetime import date
from src.models.obra_model import ObraDeArte, StatusObra
from src.database.manager import DatabaseManager

class ObraController:
    def __init__(self):
        self.db_manager = DatabaseManager()
        
    def cadastrar_obra(self, titulo, ano, artista, tipo, tecnica, dimensoes, localizacao, preco, status, imagem=None):
        try:
            if not titulo or not tipo or not tecnica or not dimensoes or not localizacao or not artista:
                return False, "Todos os campos obrigatórios devem ser preenchidos"

            if isinstance(artista, str):
                artistas_list = [a.strip() for a in artista.split(",") if a.strip()]
            else:
                artistas_list = list(artista)
            if len(artistas_list) == 0:
                return False, "Adicione pelo menos um artista"

            try:
                ano_int = int(ano)
                if ano_int > date.today().year:
                    return False, f"Ano deve ser maior que {date.today().year}"
            except ValueError:
                return False, "Ano deve ser um número válido"
            
            try:
                preco_float = float(preco) if preco else 0
                if preco_float < 0:
                    return False, "Preço não pode ser negativo"
            except ValueError:
                return False, "Preço deve ser um valor numérico válido"
            
            if self.db_manager.verificar_obra_existe(titulo, artistas_list, ano_int):
                return False, "Já existe uma obra com esse título, artista e ano"
            
            obra_id = self.db_manager.get_next_obra_id()
            obra = ObraDeArte(
                id_obra=obra_id,
                titulo=titulo,
                ano=ano_int,
                artista=artistas_list,
                tipo=tipo,
                tecnica=tecnica,
                dimensoes=dimensoes,
                localizacao=localizacao,
                preco=preco_float,
                status=StatusObra.DISPONIVEL if status is None else status,
                imagem=imagem,
                data_cadastro=date.today()
            )
            
            self.db_manager.inserir_obra(obra)
            return True, "Obra cadastrada com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao cadastrar obra: {str(e)}"
    def listar_obras(self):
        """retorna lista de todas as obras cadastradas (RF01)"""
        return self.db_manager.listar_todas_obras()
    
    def buscar_obra_por_id(self, obra_id):
        """busca uma obra pelo ID"""
        return self.db_manager.buscar_obra_por_id(obra_id)
    
    def atualizar_obra(self, obra_id, titulo, ano, artista, tipo, tecnica, dimensoes, localizacao, preco, status, imagem=None):
        try:
            obra = self.buscar_obra_por_id(obra_id)
            if not obra:
                return False, "Obra não encontrada"
                
            if obra.status == StatusObra.VENDIDA:
                return False, "Obras vendidas não podem ser editadas"
                
            if not titulo or not tipo or not tecnica or not dimensoes or not localizacao or not artista:
                return False, "Todos os campos obrigatórios devem ser preenchidos"
            
            obra.titulo = titulo
            obra.ano = int(ano)
            # garante artista como lista
            if isinstance(artista, str):
                obra.artista = [a.strip() for a in artista.split(",") if a.strip()]
            else:
                obra.artista = list(artista)
            obra.tipo = tipo
            obra.tecnica = tecnica
            obra.dimensoes = dimensoes
            obra.localizacao = localizacao
            obra.preco = float(preco) if preco else 0
            if imagem:
                obra.imagem = imagem
                
            self.db_manager.atualizar_obra(obra)
            return True, "Obra atualizada com sucesso!"
            
        except ValueError as ve:
            return False, str(ve)
        except Exception as e:
            return False, f"Erro ao atualizar obra: {str(e)}"

    def get_tipos_obra(self):
            """retorna os tipos de obra disponíveis para o cadastro"""
            return ["Pintura", "Escultura", "Fotografia", "Gravura", "Instalação", "Outro"]
        
    def get_status_obra(self):
        """retorna os status disponíveis para obras"""
        return [status.value for status in StatusObra]
    
    def listar_artistas(self):
        return self.db_manager.listar_artistas()
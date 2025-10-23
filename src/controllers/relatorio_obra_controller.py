from datetime import datetime, date
from typing import List, Dict, Any, Optional

from src.controllers.obra_controller import ObraController
from src.controllers.artista_controller import ArtistaController
from src.controllers.transacao_controller import TransacaoController
from src.models.obra_model import ObraDeArte, StatusObra
import re


class RelatorioController:
    def __init__(self):
        self.obra_ctrl = ObraController()
        self.artista_ctrl = ArtistaController()
        self.transacao_ctrl = TransacaoController()

    def listar_artistas(self):
        artistas = self.artista_ctrl.listar()
        print(f"Total de artistas encontrados: {len(artistas)}")
        for a in artistas:
            print(f"ID: {getattr(a, 'id_artista', None)}, Nome: {getattr(a, 'nome', '')}")
        return artistas

    def listar_transacoes(self):
        return self.transacao_ctrl.listar_transacoes()
    
    def validar_titulo(self, titulo):
        if not titulo or titulo.strip() == "":
            return None
        titulo_limpo = re.sub(r'[^\w\s\-\'\",.]', '', titulo)
        
        if len(titulo_limpo) > 100:
            raise ValueError("Título muito longo para busca")
        return titulo_limpo.strip().lower()

    def validar_ano(self, ano):
        if not ano or ano.strip() == "":
            return None
            
        try:
            ano_int = int(ano)
            ano_atual = datetime.now().year
            
            if ano_int > ano_atual + 1:  
                raise ValueError(f"Ano inválido: não pode ser posterior a {ano_atual + 1}")
                
            return ano_int
        except ValueError as e:
            if "invalid literal for int" in str(e):
                raise ValueError("Ano deve ser um número inteiro")
            raise e


    def validar_valor(self, valor):
        if not valor or valor.strip() == "":
            return None
            
        valor_norm = valor.replace(',', '.')
        
        try:
            valor_float = float(valor_norm)
            
            if valor_float < 0:
                raise ValueError("O valor não pode ser negativo")
                
            return valor_float
        except ValueError:
            raise ValueError("Valor deve ser um número decimal válido")


    def validar_data_cadastro(self, data_str):
        if not data_str or data_str.strip() == "":
            return None
            
        formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"]
        
        for formato in formatos:
            try:
                data = datetime.strptime(data_str, formato).date()
                
                hoje = datetime.now().date()
                if data > hoje:
                    raise ValueError("A data de cadastro não pode ser futura")
                    
                return data
            except ValueError:
                continue
                
        raise ValueError("Formato de data inválido. Use DD/MM/AAAA")

    def buscar_obras_validado(self, filtros_brutos):
        """Versão aprimorada que valida filtros antes da busca"""
        filtros_validados = {}
        
        try:
            if "titulo" in filtros_brutos and filtros_brutos["titulo"]:
                filtros_validados["titulo"] = self.validar_titulo(filtros_brutos["titulo"])
                
            if "ano" in filtros_brutos and filtros_brutos["ano"]:
                filtros_validados["ano"] = self.validar_ano(filtros_brutos["ano"])
                
            if "tecnica" in filtros_brutos and filtros_brutos["tecnica"]:
                filtros_validados["tecnica"] = filtros_brutos["tecnica"]
                
            if "tipo" in filtros_brutos and filtros_brutos["tipo"]:
                filtros_validados["tipo"] = filtros_brutos["tipo"]
                
            if "status" in filtros_brutos and filtros_brutos["status"]:
                filtros_validados["status"] = filtros_brutos["status"]
                
            if "localizacao" in filtros_brutos and filtros_brutos["localizacao"]:
                filtros_validados["localizacao"] = filtros_brutos["localizacao"]
                
            if "valor" in filtros_brutos and filtros_brutos["valor"]:
                filtros_validados["valor"] = self.validar_valor(filtros_brutos["valor"])
                
            if "data_cadastro" in filtros_brutos and filtros_brutos["data_cadastro"]:
                filtros_validados["data_cadastro"] = self.validar_data_cadastro(filtros_brutos["data_cadastro"])
                
            if "artistas" in filtros_brutos and filtros_brutos["artistas"]:
                filtros_validados["artistas"] = filtros_brutos["artistas"]
            
            if "artistas" in filtros_brutos and filtros_brutos["artistas"]:
                filtros_validados["artistas"] = filtros_brutos["artistas"]
            
            # Adicione este bloco para validar transações
            if "transacoes" in filtros_brutos and filtros_brutos["transacoes"]:
                filtros_validados["transacoes"] = filtros_brutos["transacoes"]
            
            return self.buscar_obras(filtros_validados)
    
            
        except ValueError as e:
            raise ValueError(f"Erro na validação dos filtros: {e}")

            
    def buscar_obras(self, filtros: Dict[str, Any]) -> List[ObraDeArte]:
        """
        filtros possível:
         - ano: int
         - titulo: str
         - tecnica: str
         - tipo: str
         - status: str (valor textual do StatusObra)
         - localizacao: str
         - valor: float
         - data_cadastro: date
         - artistas: list[str] (nomes)
        """
        obras = self.obra_ctrl.listar_obras()
        resultado: List[ObraDeArte] = []

        for obra in obras:
            ok = True
            titulo = filtros.get("titulo")
            if titulo and titulo.strip().lower() not in (obra.titulo or "").lower():
                ok = False

            ano = filtros.get("ano")
            if ok and ano is not None:
                try:
                    if int(obra.ano) != int(ano):
                        ok = False
                except Exception:
                    ok = False
            tecnica = filtros.get("tecnica")
            if ok and tecnica and (not obra.tecnica or tecnica.strip().lower() not in obra.tecnica.lower()):
                ok = False

            tipo = filtros.get("tipo")
            if ok and tipo and obra.tipo != tipo:
                ok = False

            status = filtros.get("status")
            if ok and status and getattr(obra.status, "value", None) != status:
                ok = False

            localizacao = filtros.get("localizacao")
            if ok and localizacao and (not obra.localizacao or localizacao.strip().lower() not in obra.localizacao.lower()):
                ok = False

            valor = filtros.get("valor")
            if ok and valor is not None:
                try:
                    if float(obra.preco or 0) != float(valor):
                        ok = False
                except Exception:
                    ok = False

            data_cad = filtros.get("data_cadastro")
            if ok and data_cad:
                dc = obra.data_cadastro
                dc_date = None
                if isinstance(dc, date):
                    dc_date = dc
                elif isinstance(dc, str):
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                        try:
                            dc_date = datetime.strptime(dc, fmt).date()
                            break
                        except Exception:
                            continue
                if dc_date != data_cad:
                    ok = False

            artistas_sel = filtros.get("artistas")
            if ok and artistas_sel:
                nome_artista = (obra.artista or "").lower()
                if not any(a.strip().lower() in nome_artista for a in artistas_sel):
                    ok = False
            
            transacoes_sel = filtros.get("transacoes")
            if ok and transacoes_sel:
                transacoes_obra = []
                for transacao in self.transacao_ctrl.listar_transacoes():
                    if str(obra.id_obra) in transacao.obras:
                        transacoes_obra.append(transacao.cliente)
                
                if not any(cliente in transacoes_sel for cliente in transacoes_obra):
                    ok = False


            if ok:
                resultado.append(obra)

        return resultado
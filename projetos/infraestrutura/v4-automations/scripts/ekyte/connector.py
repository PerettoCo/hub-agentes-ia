"""
connector.py — Conector Ekyte API REST.

Autenticação via apiKey (plano Performance).
Chave em: Ekyte → Minha Empresa → aba BI

Endpoints documentados:
  GET /v1.2/tasks               → tarefas
  GET /v1.1/projects            → projetos (sprints)
  GET /v1.1/tickets             → FCAs / tickets
  GET /v1.1/timesheets          → apontamento de horas
  GET /v1.1/boards              → base de conhecimento
  GET /v1.1/workspaces          → workspaces por cliente
  GET /v1.1/squads              → squads
  GET /v1.1/users               → usuários
  GET /v1.1/tags                → tags
  GET /v1.1/tasktypes           → tipos de tarefa

Escrita (POST) — confirmar disponibilidade com suporte Ekyte:
  POST /v1.1/tasks              → criar tarefa
  POST /v1.1/projects           → criar projeto/sprint
  POST /v1.1/boards/notes       → criar nota na base de conhecimento

Uso:
  from scripts.ekyte.connector import EkyteClient
  ekyte = EkyteClient()
  tarefas = ekyte.get_tarefas(workspace_id=123)
"""
import os
import requests
from datetime import date, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / "config" / ".env")

BASE_URL = "https://api.ekyte.com"


class EkyteClient:
    def __init__(self):
        self.api_key = os.getenv("EKYTE_API_KEY")
        if not self.api_key:
            raise ValueError("EKYTE_API_KEY não encontrada em config/.env")
        self.session = requests.Session()

    def _get(self, endpoint: str, params: dict = None) -> list | dict:
        """Executa GET paginado e retorna todos os dados."""
        params = params or {}
        params["apiKey"] = self.api_key

        todos = []
        page = 1

        while True:
            params["page"] = page
            resp = self.session.get(f"{BASE_URL}{endpoint}", params=params, timeout=30)
            resp.raise_for_status()
            body = resp.json()

            if body.get("error"):
                raise RuntimeError(f"Ekyte API erro: {body['error']['message']}")

            data = body.get("data", [])
            if not data:
                break

            # Se retornou dict único (sem paginação)
            if isinstance(data, dict):
                return data

            todos.extend(data)

            paging = body.get("paging")
            if not paging or page >= paging.get("totalPages", 1):
                break
            page += 1

        return todos

    def _post(self, endpoint: str, payload: dict) -> dict:
        """
        POST para criar recursos.
        ATENÇÃO: confirme disponibilidade com suporte Ekyte antes de usar.
        atendimento@ekyte.com
        """
        resp = self.session.post(
            f"{BASE_URL}{endpoint}",
            params={"apiKey": self.api_key},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        if body.get("error"):
            raise RuntimeError(f"Ekyte API erro: {body['error']['message']}")
        return body.get("data", {})

    # ── TAREFAS ──────────────────────────────────────────────────────────────

    def get_tarefas(
        self,
        workspace_id: int = None,
        squad_id: int = None,
        project_id: int = None,
        status: int = 10,
        criado_de: str = None,
        criado_ate: str = None,
        entrega_de: str = None,
        entrega_ate: str = None,
        include_checklist: bool = False,
        include_phases: bool = False,
        include_comments: bool = False,
    ) -> list:
        """
        Lista tarefas com filtros.
        status: 10=Ativas, 20=Pausadas, 30=Concluídas, 40=Canceladas
        """
        params = {"status": status}
        if workspace_id: params["workspaceId"] = workspace_id
        if squad_id: params["SquadId"] = squad_id
        if project_id: params["projectId"] = project_id
        if criado_de: params["createdFrom"] = criado_de
        if criado_ate: params["createdTo"] = criado_ate
        if entrega_de: params["dueFrom"] = entrega_de
        if entrega_ate: params["dueTo"] = entrega_ate
        if include_checklist: params["includeChecklist"] = 1
        if include_phases: params["includePhases"] = 1
        if include_comments: params["includeComments"] = 1
        return self._get("/v1.2/tasks", params)

    def get_tarefas_atrasadas(self, workspace_id: int = None, squad_id: int = None) -> list:
        """Retorna tarefas ativas com data de entrega no passado."""
        hoje = date.today().strftime("%Y-%m-%d")
        tarefas = self.get_tarefas(
            workspace_id=workspace_id,
            squad_id=squad_id,
            status=10,
            entrega_ate=hoje,
        )
        return [t for t in tarefas if t.get("currentDueDate")]

    def get_tarefas_da_semana(self, workspace_id: int = None, squad_id: int = None) -> list:
        """Tarefas criadas ou com entrega esta semana."""
        hoje = date.today()
        inicio_semana = (hoje - timedelta(days=hoje.weekday())).strftime("%Y-%m-%d")
        fim_semana = (hoje + timedelta(days=6 - hoje.weekday())).strftime("%Y-%m-%d")
        return self.get_tarefas(
            workspace_id=workspace_id,
            squad_id=squad_id,
            status=10,
            entrega_de=inicio_semana,
            entrega_ate=fim_semana,
        )

    def criar_tarefa(
        self,
        titulo: str,
        descricao: str,
        workspace_id: int,
        executor_id: str,
        project_id: int = None,
        prazo: str = None,
        prioridade: int = 200,
        task_type_id: int = None,
    ) -> dict:
        """
        Cria uma tarefa no Ekyte.
        prioridade: 100=Baixa, 200=Média, 300=Alta, 400=Urgente
        CONFIRMAR com suporte Ekyte se POST /tasks está disponível.
        """
        payload = {
            "title": titulo,
            "description": descricao,
            "workspaceId": workspace_id,
            "executorId": executor_id,
            "priority": prioridade,
        }
        if project_id: payload["projectId"] = project_id
        if prazo: payload["dueDate"] = prazo
        if task_type_id: payload["taskTypeId"] = task_type_id
        return self._post("/v1.1/tasks", payload)

    # ── PROJETOS (SPRINTS) ───────────────────────────────────────────────────

    def get_projetos(self, workspace_id: int = None, criado_de: str = None) -> list:
        """Lista projetos/sprints."""
        params = {}
        if workspace_id: params["workspaceId"] = workspace_id
        if criado_de: params["createdFrom"] = criado_de
        return self._get("/v1.1/projects", params)

    def get_sprints_ativas(self, workspace_id: int = None) -> list:
        """Retorna projetos ativos (situation=1)."""
        projetos = self.get_projetos(workspace_id=workspace_id)
        return [p for p in projetos if p.get("situation") == 1]

    def get_status_sprint(self, project_id: int) -> dict:
        """Calcula % de conclusão de uma sprint."""
        projetos = self.get_projetos()
        sprint = next((p for p in projetos if p["id"] == project_id), None)
        if not sprint:
            return {}

        total = sprint.get("plannedTasksCount", 0)
        concluidas = sprint.get("accomplishedTasksCount", 0)
        pct = (concluidas / total * 100) if total > 0 else 0

        return {
            "nome": sprint["name"],
            "total_tarefas": total,
            "concluidas": concluidas,
            "percentual": round(pct, 1),
            "status": "🟢" if pct >= 80 else ("🟡" if pct >= 50 else "🔴"),
            "inicio": sprint.get("startDate"),
            "fim": sprint.get("endDate"),
        }

    def criar_sprint(
        self,
        nome: str,
        workspace_id: int,
        inicio: str,
        fim: str,
        descricao: str = "",
    ) -> dict:
        """
        Cria projeto/sprint no Ekyte.
        CONFIRMAR com suporte Ekyte se POST /projects está disponível.
        """
        payload = {
            "name": nome,
            "workspaceId": workspace_id,
            "startDate": inicio,
            "endDate": fim,
            "description": descricao,
        }
        return self._post("/v1.1/projects", payload)

    # ── TICKETS / FCAs ───────────────────────────────────────────────────────

    def get_tickets(
        self,
        workspace_id: int = None,
        squad_id: int = None,
        status: int = 1,
        criado_de: str = None,
    ) -> list:
        """
        Lista tickets (FCAs).
        status: 1=Em atendimento, 2=Aguardando, 3=Resolvido, 9=Cancelado
        """
        params = {"status": status}
        if workspace_id: params["workspaceId"] = workspace_id
        if squad_id: params["squadId"] = squad_id
        if criado_de: params["createdFrom"] = criado_de
        return self._get("/v1.1/tickets", params)

    def get_fcas_abertas(self, workspace_id: int = None, squad_id: int = None) -> list:
        """FCAs em aberto (em atendimento)."""
        return self.get_tickets(workspace_id=workspace_id, squad_id=squad_id, status=1)

    def criar_fca(
        self,
        fato: str,
        causa: str,
        acao: str,
        workspace_id: int,
        executor_id: str,
        cliente_nome: str = "",
    ) -> dict:
        """
        Cria FCA como ticket no Ekyte.
        CONFIRMAR com suporte Ekyte se POST /tickets está disponível.
        """
        assunto = f"FCA — {cliente_nome} — {date.today().strftime('%d/%m/%Y')}"
        descricao = f"FATO:\n{fato}\n\nCAUSA:\n{causa}\n\nAÇÃO:\n{acao}"
        payload = {
            "subject": assunto,
            "description": descricao,
            "workspaceId": workspace_id,
            "executorId": executor_id,
        }
        return self._post("/v1.1/tickets", payload)

    # ── APONTAMENTO DE HORAS ─────────────────────────────────────────────────

    def get_apontamentos(
        self,
        workspace_id: int = None,
        squad_id: int = None,
        de: str = None,
        ate: str = None,
    ) -> list:
        """Lista apontamentos de horas."""
        params = {}
        if workspace_id: params["workspaceId"] = workspace_id
        if squad_id: params["squadId"] = squad_id
        if de: params["dateFrom"] = de
        if ate: params["dateTo"] = ate
        return self._get("/v1.1/timesheets", params)

    def get_timesheet_semana(self, squad_id: int = None) -> dict:
        """Verifica se timesheet foi atualizado esta semana."""
        hoje = date.today()
        inicio = (hoje - timedelta(days=hoje.weekday())).strftime("%Y-%m-%d")
        fim = hoje.strftime("%Y-%m-%d")

        apontamentos = self.get_apontamentos(squad_id=squad_id, de=inicio, ate=fim)

        por_usuario = {}
        for a in apontamentos:
            uid = a.get("executorId") or a.get("userId")
            nome = a.get("executor") or a.get("user", "?")
            minutos = a.get("actualTime", 0) or 0
            if uid not in por_usuario:
                por_usuario[uid] = {"nome": nome, "minutos": 0, "registros": 0}
            por_usuario[uid]["minutos"] += minutos
            por_usuario[uid]["registros"] += 1

        return {
            "semana": f"{inicio} → {fim}",
            "total_registros": len(apontamentos),
            "por_usuario": list(por_usuario.values()),
            "atualizado": len(apontamentos) > 0,
        }

    # ── BASE DE CONHECIMENTO ─────────────────────────────────────────────────

    def get_base_conhecimento(self, workspace_id: int = None) -> list:
        """Lista quadros e notas da base de conhecimento."""
        params = {}
        if workspace_id: params["workspaceId"] = workspace_id
        return self._get("/v1.1/boards", params)

    def criar_nota_base(
        self,
        titulo: str,
        conteudo: str,
        quadro_id: int,
        categoria: str = "",
    ) -> dict:
        """
        Cria nota na base de conhecimento.
        CONFIRMAR com suporte Ekyte se POST /boards/notes está disponível.
        """
        payload = {
            "title": titulo,
            "content": conteudo,
            "boardId": quadro_id,
            "category": categoria,
            "situation": "active",
        }
        return self._post("/v1.1/boards/notes", payload)

    # ── WORKSPACES / SQUADS / USUÁRIOS ───────────────────────────────────────

    def get_workspaces(self) -> list:
        """Lista workspaces da empresa."""
        return self._get("/v1.1/workspaces", {})

    def get_squads(self) -> list:
        """Lista squads."""
        return self._get("/v1.1/squads", {})

    def get_usuarios(self) -> list:
        """Lista usuários."""
        return self._get("/v1.1/users", {})

    def get_tipos_tarefa(self) -> list:
        """Lista tipos de tarefa disponíveis."""
        return self._get("/v1.1/tasktypes", {})

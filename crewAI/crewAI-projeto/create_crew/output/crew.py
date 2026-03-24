from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class CreateCrew:
    """CreateCrew crew"""

    agents_config = {
        "researcher": {
            "name": "agente_pesquisa",
            "role": "Realiza uma pesquisa aprofundada sobre as tendências atuais em Inteligência Artificial Generativa, coletando artigos, estudos, vídeos e outros materiais pertinentes.",
            "goal": "Identificar e compilar conteúdos relevantes que reflitam as novas tendências e conceitos em Inteligência Artificial Generativa para enriquecer o material didático do curso.",
            "backstory": "Com a evolução constante da IA, a necessidade de manter-se atualizado se torna vital. O agente de pesquisa foi projetado para navegar por bases de dados acadêmicas, garantindo que as informações mais recentes e relevantes sejam sempre consideradas na construção do curso.",
        },
        "reporting_analyst": {
            "name": "agente_organizacao_conteudo",
            "role": "Reúne e organiza os tópicos importantes identificados pelo agente de pesquisa em uma estrutura lógica e sequencial para o curso.",
            "goal": "Criar um esboço coerente e estruturado do curso que maximize a aprendizagem e a retenção de informações pelos alunos.",
            "backstory": "A criação de um curso eficaz depende da organização meticulosa de conteúdo. O agente de organização foi desenvolvido para sistematizar a informação coletada, transformando-a em um plano de curso estruturado e intuitivo.",
        },
    }

    tasks_config = {
        "research_task": {
            "name": "research_task",
            "description": "Realiza a pesquisa de conteúdos relevantes para o curso de Inteligência Artificial Generativa.",
        },
        "reporting_task": {
            "name": "reporting_task",
            "description": "Organiza os tópicos e produz relatórios para a revisão final do curso.",
        },
    }

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["reporting_analyst"],  # type: ignore[index]
            verbose=True,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],  # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config["reporting_task"],  # type: ignore[index]
            output_file="report.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CreateCrew crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )


if __name__ == "__main__":
    create_crew = CreateCrew()
    create_crew.crew().launch()

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

import agentops
import os
from dotenv import load_dotenv

_ = load_dotenv()
AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
agentops.init(AGENTOPS_API_KEY)


@CrewBase
class CreateCrew:
    """CreateCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def arquiteto_de_solucoes(self) -> Agent:
        return Agent(
            config=self.agents_config["arquiteto_de_solucoes"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def designer_de_agentes(self) -> Agent:
        return Agent(
            config=self.agents_config["designer_de_agentes"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def analista_de_tarefas(self) -> Agent:
        return Agent(
            config=self.agents_config["analista_de_tarefas"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def engenheiro_de_integracao(self) -> Agent:
        return Agent(
            config=self.agents_config["engenheiro_de_integracao"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def qa_de_agentes(self) -> Agent:
        return Agent(
            config=self.agents_config["qa_de_agentes"],  # type: ignore[index]
            verbose=True,
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def definir_objetivo_e_escopo_do_sistema(self) -> Task:
        return Task(
            config=self.tasks_config["definir_objetivo_e_escopo_do_sistema"],  # type: ignore[index]
        )

    @task
    def projetar_os_agentes_do_sistema(self) -> Task:
        return Task(
            config=self.tasks_config["projetar_os_agentes_do_sistema"],  # type: ignore[index]
            output_file="output/agents.yaml",
        )

    @task
    def planejar_e_descrever_tarefas(self) -> Task:
        return Task(
            config=self.tasks_config["planejar_e_descrever_tarefas"],  # type: ignore[index]
            context=[self.definir_objetivo_e_escopo_do_sistema()],
            output_file="output/tasks.yaml",
        )

    @task
    def criar_o_script_de_orquestracao(self) -> Task:
        return Task(
            config=self.tasks_config["criar_o_script_de_orquestracao"],  # type: ignore[index]
            context=[
                self.definir_objetivo_e_escopo_do_sistema(),
                self.projetar_os_agentes_do_sistema(),
            ],
            output_file="output/crew.py",
        )

    @task
    def testar_e_ajustar_o_sistema(self) -> Task:
        return Task(
            config=self.tasks_config["testar_e_ajustar_o_sistema"],  # type: ignore[index]
            output_file="report.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CreateCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

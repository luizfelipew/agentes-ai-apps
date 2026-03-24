```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class CreateCrew():
    """CreateCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    @agent
    def pesquisa_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['pesquisa_agent'],  # type: ignore[index]
            verbose=True
        )
    
    @agent
    def organizacao_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['organizacao_agent'],  # type: ignore[index]
            verbose=True
        )
    
    @agent
    def escopo_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['escopo_agent'],  # type: ignore[index]
            verbose=True
        )
    
    @agent
    def criacao_conteudo_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['criacao_conteudo_agent'],  # type: ignore[index]
            verbose=True
        )

    @agent
    def avaliacao_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['avaliacao_agent'],  # type: ignore[index]
            verbose=True
        )
    
    @agent
    def atualizacao_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['atualizacao_agent'],  # type: ignore[index]
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],  # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],  # type: ignore[index]
            output_file='report.md'
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
    # Here we would load the agents_config and tasks_config from the agents.yaml and tasks.yaml files
    # and then run the crew.
    import yaml

    with open('agents.yaml', 'r') as f:
        agents_config = yaml.safe_load(f)

    with open('tasks.yaml', 'r') as f:
        tasks_config = yaml.safe_load(f)

    crew_instance = CreateCrew()
    crew_instance.agents_config = agents_config
    crew_instance.tasks_config = tasks_config
    crew_instance.crew.run()
```

This script `crew.py` initializes a multi-agent system that is capable of orchestrating various specialized agents for research, organization, content creation, evaluation, and updating of course materials regarding Generative AI. The configuration is loaded from `agents.yaml` and `tasks.yaml`, allowing for a modular and adaptable design. Each agent is defined with the corresponding goals and behaviors specified in the YAML files.
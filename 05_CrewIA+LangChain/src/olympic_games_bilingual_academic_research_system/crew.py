import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	FileReadTool,
	BraveSearchTool,
	SerplyScholarSearchTool,
	ScrapeWebsiteTool,
	ArxivPaperTool
)





@CrewBase
class OlympicGamesBilingualAcademicResearchSystemCrew:
    """OlympicGamesBilingualAcademicResearchSystem crew"""

    
    @agent
    def academic_writing_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["academic_writing_specialist"],
            
            
            tools=[				FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def olympic_studies_critical_reviewer(self) -> Agent:
        
        return Agent(
            config=self.agents_config["olympic_studies_critical_reviewer"],
            
            
            tools=[				BraveSearchTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def olympic_games_research_agent(self) -> Agent:
        
        return Agent(
            config=self.agents_config["olympic_games_research_agent"],
            
            
            tools=[				SerplyScholarSearchTool(),
				ScrapeWebsiteTool(),
				ArxivPaperTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def spanish_translation_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["spanish_translation_specialist"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def olympic_topic_validator(self) -> Agent:
        
        return Agent(
            config=self.agents_config["olympic_topic_validator"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    

    
    @task
    def olympic_topic_validation(self) -> Task:
        return Task(
            config=self.tasks_config["olympic_topic_validation"],
            markdown=False,
            
            
        )
    
    @task
    def olympic_games_rag_research(self) -> Task:
        return Task(
            config=self.tasks_config["olympic_games_rag_research"],
            markdown=False,
            
            
        )
    
    @task
    def academic_content_generation(self) -> Task:
        return Task(
            config=self.tasks_config["academic_content_generation"],
            markdown=False,
            
            
        )
    
    @task
    def critical_academic_review(self) -> Task:
        return Task(
            config=self.tasks_config["critical_academic_review"],
            markdown=False,
            
            
        )
    
    @task
    def final_document_consolidation(self) -> Task:
        return Task(
            config=self.tasks_config["final_document_consolidation"],
            markdown=False,
            
            
        )
    
    @task
    def final_spanish_translation(self) -> Task:
        return Task(
            config=self.tasks_config["final_spanish_translation"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the OlympicGamesBilingualAcademicResearchSystem crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)

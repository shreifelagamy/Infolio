"""LinkedIn post generation crew"""

from crewai import Agent, Crew, Process, Task
from ..base_crew import BaseCrew

class LinkedInCrew(BaseCrew):
    """LinkedIn post generation crew using CrewAI"""
    
    def __init__(self):
        """Initialize LinkedIn crew"""
        super().__init__(crew_name='linkedin')
        self.agents = []
        self.tasks = []
        self._setup_crew()
            
    def _setup_crew(self):
        """Setup the crew with agents and tasks"""
        # Create agents
        self.researcher = Agent(
            **self.agents_config['researcher']
        )
        self.writer = Agent(
            **self.agents_config['writer']
        )
        self.editor = Agent(
            **self.agents_config['editor']
        )
        
        self.agents = [self.researcher, self.writer, self.editor]
        
        # Create tasks with their respective agents
        tasks_config = self.tasks_config
        
        self.research_task = Task(
            description=tasks_config['research_task']['description'],
            expected_output=tasks_config['research_task']['expected_output'],
            agent=self.researcher
        )
        
        self.writing_task = Task(
            description=tasks_config['writing_task']['description'],
            expected_output=tasks_config['writing_task']['expected_output'],
            agent=self.writer
        )
        
        self.editing_task = Task(
            description=tasks_config['editing_task']['description'],
            expected_output=tasks_config['editing_task']['expected_output'],
            agent=self.editor
        )
        
        self.tasks = [self.research_task, self.writing_task, self.editing_task]
        
    def generate_post(self, title: str, content: str, preferences: dict) -> str:
        """Generate a LinkedIn post using the crew"""
        # Update task configurations with dynamic content
        self.research_task.description = self.research_task.description.format(
            title=title,
            content=content
        )
        
        self.writing_task.description = self.writing_task.description.format(
            preferences=preferences
        )
        
        # Create and run the crew
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result

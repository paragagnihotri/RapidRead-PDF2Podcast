from crewai import Agent
from crewai import LLM
from backend.tools.text_cleaner import TextCleaner
from backend.config import settings

# Initialize LLM
llm = LLM(
    model=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    api_key=settings.GEMINI_API_KEY
)

def create_agents():
    """Create and return all CrewAI agents"""
    
    pdf_cleaner_agent = Agent(
        role="PDF Text PreProcessing Specialist",
        goal="Process extracted PDF text by removing redundant elements while preserving all meaningful content",
        backstory=(
            "You are an expert in document processing with 10+ years of experience. "
            "You specialize in identifying and removing artifacts introduced during PDF parsing "
            "while maintaining 100% content fidelity."
        ),
        tools=[TextCleaner()],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    content_analyzer_agent = Agent(
        role="Technical Content Analyst",
        goal="Analyze cleaned text to identify and extract all key topics, concepts, and important points for comprehensive coverage",
        backstory=(
            "You are a senior technical analyst with expertise in breaking down complex documentation. "
            "You excel at identifying main themes, subtopics, technical details, and creating structured "
            "outlines that ensure no important information is missed. You have a keen eye for recognizing "
            "what matters most in technical documents."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    dialogue_building_agent = Agent(
        role="Conversational Dialogue Designer",
        goal="Design the structure and flow of natural, expressive audio discussion between two knowledgeable speakers exploring topics together",
        backstory=(
            "You are a professional dialogue writer with 15+ years in podcast and audio content creation. "
            "You specialize in creating balanced, engaging conversations where both speakers contribute insights, "
            "share perspectives, build on each other's ideas, and explore topics collaboratively. You excel at "
            "crafting dialogue that conveys emotion, personality, and naturalness purely through words, rhythm, "
            "and verbal expressions - no visual cues needed. You understand how real people talk, with pauses, "
            "laughter, vocal inflections, and spontaneous moments that make audio conversations feel authentic "
            "and alive. Your conversations sound like capturing two real people mid-discussion, not reading a script."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    script_writing_agent = Agent(
        role="Professional Audio Script Writer",
        goal="Write engaging, natural dialogue that sounds authentic when spoken aloud, with organic speech patterns and vocal expressions",
        backstory=(
            "You are an award-winning script writer specializing in podcast-style discussions and audio dialogues. "
            "You create conversations where speakers sound like real people talking naturally - they laugh, pause, "
            "show enthusiasm through their words and tone, use natural speech patterns, and react emotionally to ideas. "
            "Your scripts are designed specifically for audio: every word is crafted to sound natural when spoken aloud. "
            "You masterfully use verbal cues, rhythm, pacing, interruptions, and natural speech patterns to create "
            "expressive, engaging dialogue without any visual elements. When your scripts are performed, they sound "
            "like genuine, spontaneous conversations between passionate, articulate people who enjoy exploring ideas together. "
            "Listeners feel like they're eavesdropping on a real discussion, not hearing a scripted exchange."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    quality_assurance_agent = Agent(
        role="Quality Assurance & Script Formatter",
        goal="Review the conversation for completeness, natural flow, and proper formatting; ensure all topics are covered",
        backstory=(
            "You are a meticulous editor and QA specialist with expertise in conversational content. "
            "You ensure scripts are well-formatted, dialogue sounds natural, all important points are covered, "
            "and the final output is polished and ready for production. You check for consistency, clarity, "
            "and completeness."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return {
        "pdf_cleaner": pdf_cleaner_agent,
        "content_analyzer": content_analyzer_agent,
        "dialogue_builder": dialogue_building_agent,
        "script_writer": script_writing_agent,
        "quality_assurance": quality_assurance_agent
    }
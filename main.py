# from typing_extensions import TypedDict
import os
from typing import List, Dict, Any, TypedDict
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

# API Key Configuration
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class TravelAssistantState(TypedDict):
    destination: str
    travel_duration: str
    travel_preferences: Dict[str, Any]
    destination_research: str
    detailed_itinerary: str
    travel_recommendations: str

    @classmethod
    def create(cls):

        destination = ""
        travel_duration = ""
        travel_preferences: Dict[str, Any] = {
            "budget": "moderate",
            "interests": [],
            "travel_style": "balanced"
        }
        destination_research = ""
        detailed_itinerary = ""
        travel_recommendations = ""
        return TravelAssistantState(
            destination=destination,
            travel_duration=travel_duration,
            travel_preferences=travel_preferences,
            destination_research=destination_research,
            detailed_itinerary=detailed_itinerary,
            travel_recommendations=travel_recommendations
        )


def process_destination_input(state: TravelAssistantState):
    print(state)
    print(True)
    print(st.session_state)
    destination = st.session_state.get("destination", "")
    travel_duration = st.session_state.get("travel_duration", "5 Days")
    budget = st.session_state.get("budget", "moderate")
    interests = st.session_state.get("interests", [])
    travel_style = st.session_state.get("travel_style", "balanced")

    return {
        "destination": destination,
        "travel_duration": travel_duration,
        "travel_preferences": {
            "budget": budget,
            "interests": interests,
            "travel_style": travel_style
        },
        "destination_research": "",
        "detailed_itinerary": "",
        "travel_recommendations": "",
    }


def generate_destination_research(state: TravelAssistantState):
    llms = initialize_llms()
    destination_analyzer = llms["destination_analyzer"]

    if not state['destination']:
        return {"destination_research": "No destination specified. Please provide a destination."}

    research_prompt = f"""
    Provide comprehensive research about {state['destination']} for a {state['travel_duration']} trip:

    Travel Preferences:
    - Budget: {state['travel_preferences']['budget']}
    - Interests: {', '.join(state['travel_preferences']['interests']) or 'None specified'}
    - Travel Style: {state['travel_preferences']['travel_style']}

    Include detailed information about:
    - Top attractions
    - Cultural highlights
    - Local cuisine
    - Transportation options
    - Best areas to stay
    - Seasonal considerations
    - Estimated budget breakdown
    """

    try:
        destination_research = destination_analyzer.invoke(
            research_prompt).content
        return {"destination_research": destination_research or "No research available for this destination."}
    except Exception as e:
        return {"destination_research": f"Error generating research: {str(e)}"}


def initialize_llms():
    return {
        "destination_analyzer": ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, convert_system_message_to_human=True
        ),
        "itinerary_planner": ChatGroq(
            model="mixtral-8x7b-32768", temperature=0.7, groq_api_key=GROQ_API_KEY
        ),
        "recommendation_refiner": ChatGroq(
            model="llama-3.3-70b-versatile", temperature=0.5, groq_api_key=GROQ_API_KEY
        ),
    }


def create_personalized_itinerary(state: TravelAssistantState):
    llms = initialize_llms()
    itinerary_planner = llms["itinerary_planner"]

    if not state['destination'] or not state['destination_research']:
        return {"detailed_itinerary": "Unable to generate itinerary. Please check destination details."}

    itinerary_prompt = f"""
    Create a detailed {state['travel_duration']} itinerary for {state['destination']}

    Destination Research: {state['destination_research']}
    Travel Preferences: {state['travel_preferences']}

    Itinerary Requirements:
    - Day-by-day breakdown
    - Mix of activities aligned with interests
    - Budget-conscious options
    - Flexible scheduling
    - Include local experiences
    - Transportation between activities
    """

    try:
        detailed_itinerary = itinerary_planner.invoke(itinerary_prompt).content
        return {"detailed_itinerary": detailed_itinerary or "No itinerary could be generated."}
    except Exception as e:
        return {"detailed_itinerary": f"Error creating itinerary: {str(e)}"}


def refine_travel_recommendations(state: TravelAssistantState):
    llms = initialize_llms()
    recommendation_refiner = llms["recommendation_refiner"]

    if not state['destination'] or not state['detailed_itinerary']:
        return {"travel_recommendations": "Unable to generate recommendations. Please check travel details."}

    refinement_prompt = f"""
    Refine travel recommendations for {state['destination']}

    Existing Itinerary: {state['detailed_itinerary']}
    Travel Preferences: {state['travel_preferences']}

    Provide:
    - Top 5 must-do experiences
    - Hidden gems and local secrets
    - Practical travel tips
    - Packing suggestions
    - Cultural etiquette advice
    """

    try:
        final_recommendations = recommendation_refiner.invoke(
            refinement_prompt).content
        return {"travel_recommendations": final_recommendations or "No recommendations available."}
    except Exception as e:
        return {"travel_recommendations": f"Error refining recommendations: {str(e)}"}


def build_travel_assistant_workflow():
    workflow = StateGraph(TravelAssistantState)

    workflow.add_node("process_input", process_destination_input)
    workflow.add_node("generate_research", generate_destination_research)
    workflow.add_node("create_itinerary", create_personalized_itinerary)
    workflow.add_node("refine_recommendations", refine_travel_recommendations)

    workflow.set_entry_point("process_input")

    workflow.add_edge("process_input", "generate_research")
    workflow.add_edge("generate_research", "create_itinerary")
    workflow.add_edge("create_itinerary", "refine_recommendations")
    workflow.add_edge("refine_recommendations", END)

    return workflow.compile()


def run_travel_assistant(state: TravelAssistantState):
    workflow = build_travel_assistant_workflow()
    final_state = workflow.invoke(state)
    return final_state


travel_assistant_workflow = build_travel_assistant_workflow()

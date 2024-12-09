import streamlit as st

# Import the workflow script
from main import TravelAssistantState, run_travel_assistant


def main():
    st.set_page_config(page_title="AI Travel Planner", page_icon="✈️")

    st.title("🌍 AI Travel Planner")
    st.markdown("Get personalized travel recommendations in seconds!")

    # Create two columns for input
    col1, col2 = st.columns(2)

    with col1:
        # Destination Input
        destination = st.text_input(
            "Destination",
            placeholder="e.g., Paris, Tokyo, Bali"
        )

        # Travel Duration
        travel_duration = st.selectbox(
            "Trip Duration",
            ["3 Days", "5 Days", "7 Days", "10 Days", "2 Weeks"],
            index=1
        )

    with col2:
        # Budget Selection
        budget = st.selectbox(
            "Budget Range",
            ["Budget", "Moderate", "Luxury"],
            index=1
        )

        # Travel Interests
        interests = st.multiselect(
            "Travel Interests",
            [
                "Culture",
                "Adventure",
                "Food",
                "History",
                "Nature",
                "Relaxation",
                "Nightlife",
                "Shopping"
            ],
            default=["Culture", "Food"]
        )

    # Additional Travel Style
    travel_style = st.radio(
        "Travel Style",
        ["Relaxed", "Balanced", "Action-Packed"],
        horizontal=True,
        index=1
    )

    # Generate Travel Plan Button
    if st.button("Generate Travel Plan", type="primary"):
        # Validate inputs
        if not destination:
            st.error("Please enter a destination")
            return

        # Initialize state
        state = TravelAssistantState.create()

        # Store preferences in session state
        st.session_state.destination = destination
        st.session_state.travel_duration = travel_duration
        st.session_state.budget = budget
        st.session_state.interests = interests
        st.session_state.travel_style = travel_style

        # Run travel assistant workflow
        try:
            result = run_travel_assistant(state)

            print("Button Pressed")
            # Display Results
            st.header(f"🌴 Your {destination} Travel Plan")

            if result['destination_research']:
                st.subheader("Destination Insights")
                st.write(result['destination_research'])

            if result['detailed_itinerary']:
                st.subheader("Detailed Itinerary")
                st.write(result['detailed_itinerary'])

            if result['travel_recommendations']:
                st.subheader("Travel Recommendations")
                st.write(result['travel_recommendations'])

        except Exception as e:
            st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
from langchain_core.messages import HumanMessage, AIMessage
import os
from langsmith import Client
from typing_extensions import cast
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import uuid
from travel_research.prompts import BRIEF_HALLUCINATION_PROMPT,BRIEF_CRITERIA_PROMPT

# Conversation 1: Japan trip
conversation_travel_1 = [
    HumanMessage(content="I want to plan a trip to Japan in spring."),
    AIMessage(content="Great! Could you share your travel dates, number of travelers, budget, and main interests (e.g., cherry blossoms, food, culture, shopping)?"),
    HumanMessage(content="Two of us, traveling in April 2025 for 10 days. Budget $4,000 per person, mainly interested in cherry blossoms and food.")
]

# Conversation 2: Maldives trip
conversation_travel_2 = [
    HumanMessage(content="Can you help me plan a Maldives vacation?"),
    AIMessage(content="Of course! Please tell me your travel dates, trip length, budget, and whether you prefer resorts, water villas, or budget stays."),
    HumanMessage(content="We’re a couple, planning 1 week in November 2025. Budget is around $6,000 total, and we’d love to stay in an overwater villa.")
]

criteria_travel_1 = [
    "Destination is Japan",
    "Travel dates are April 2025",
    "Trip length is 10 days",
    "Number of travelers is 2",
    "Budget is $4,000 per person",
    "Main interests are cherry blossoms and food"
]

criteria_travel_2 = [
    "Destination is Maldives",
    "Travel dates are November 2025",
    "Trip length is 1 week",
    "Number of travelers is 2 (a couple)",
    "Budget is $6,000 total",
    "Accommodation preference is an overwater villa"
]

# Initialize the LangSmith client
langsmith_client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

# Create the dataset
dataset_name = "travel_research_scoping"
if not langsmith_client.has_dataset(dataset_name=dataset_name):

    # Create the dataset
    dataset = langsmith_client.create_dataset(
        dataset_name=dataset_name,
        description="A dataset that measures the quality of research briefs generated from an input conversation",
    )

    # Add the examples to the dataset
    langsmith_client.create_examples(
        dataset_id=dataset.id,
        examples=[
            {
                "inputs": {"messages": conversation_travel_1},
                "outputs": {"criteria": criteria_travel_1},
            },
            {
                "inputs": {"messages": conversation_travel_2},
                "outputs": {"criteria": criteria_travel_2},
            },
        ],
    )


class Criteria(BaseModel):
    """
    Individual success criteria evaluation result.

    This model represents a single evaluation criteria that should be present
    in the research brief, along with a detailed assessment of whether it was
    successfully captured and the reasoning behind that assessment.
    """
    criteria_text: str = Field(
        description="The specific success criteria being evaluated (e.g., 'Current age is 25', 'Monthly rent below 7k')"
    )
    reasoning: str = Field(
        description="Detailed explanation of why this criteria is or isn't captured in the research brief, including specific evidence from the brief"
    )
    is_captured: bool = Field(
        description="Whether this specific criteria is adequately captured in the research brief (True) or missing/inadequately addressed (False)"
    )

def evaluate_success_criteria(outputs: dict, reference_outputs: dict):
    """
    Evaluate whether the research brief captures all required success criteria.

    This function evaluates each criterion individually to provide focused assessment
    and detailed reasoning for each evaluation decision.

    Args:
        outputs: Dictionary containing the research brief to evaluate
        reference_outputs: Dictionary containing the list of success criteria

    Returns:
        Dict with evaluation results including score (0.0 to 1.0)
    """
    research_brief = outputs["research_brief"]
    success_criteria = reference_outputs["criteria"]

    model = ChatOpenAI(
    model=LLM_MODEL,
    base_url=LLM_API_ENDPOINT,
    api_key=LLM_API_KEY,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
        )
    structured_output_model = model.with_structured_output(Criteria)

    # Run evals
    responses = structured_output_model.batch([
    [
        HumanMessage(
            content=BRIEF_CRITERIA_PROMPT.format(
                research_brief=research_brief,
                criterion=criterion
            )
        )
    ]
    for criterion in success_criteria])

    # Ensure the criteria_text field is populated correctly
    individual_evaluations = [
        Criteria(
            reasoning=response.reasoning,
            criteria_text=criterion,
            is_captured=response.is_captured
        )
        for criterion, response in zip(success_criteria, responses)
    ]

    # Calculate overall score as percentage of captured criteria
    captured_count = sum(1 for eval_result in individual_evaluations if eval_result.is_captured)
    total_count = len(individual_evaluations)

    return {
        "key": "success_criteria_score",
        "score": captured_count / total_count if total_count > 0 else 0.0,
        "individual_evaluations": [
            {
                "criteria": eval_result.criteria_text,
                "captured": eval_result.is_captured,
                "reasoning": eval_result.reasoning
            }
            for eval_result in individual_evaluations
        ]
    }


# NoAssumptions class with reasoning field and enhanced descriptions
class NoAssumptions(BaseModel):
    """
    Evaluation model for checking if research brief makes unwarranted assumptions.

    This model evaluates whether the research brief contains any assumptions,
    inferences, or additions that were not explicitly stated by the user in their
    original conversation. It provides detailed reasoning for the evaluation decision.
    """
    no_assumptions: bool = Field(
        description="Whether the research brief avoids making unwarranted assumptions. True if the brief only includes information explicitly provided by the user, False if it makes assumptions beyond what was stated."
    )
    reasoning: str = Field(
        description="Detailed explanation of the evaluation decision, including specific examples of any assumptions found or confirmation that no assumptions were made beyond the user's explicit statements."
    )

def evaluate_no_assumptions(outputs: dict, reference_outputs: dict):
    """
    Evaluate whether the research brief avoids making unwarranted assumptions.

    This evaluator checks that the research brief only includes information
    and requirements that were explicitly provided by the user, without
    making assumptions about unstated preferences or requirements.

    Args:
        outputs: Dictionary containing the research brief to evaluate
        reference_outputs: Dictionary containing the success criteria for reference

    Returns:
        Dict with evaluation results including boolean score and detailed reasoning
    """
    research_brief = outputs["research_brief"]
    success_criteria = reference_outputs["criteria"]

    model = ChatOpenAI(model="gpt-4.1", temperature=0)
    structured_output_model = model.with_structured_output(NoAssumptions)

    response = structured_output_model.invoke([
        HumanMessage(content=BRIEF_HALLUCINATION_PROMPT.format(
            research_brief=research_brief,
            success_criteria=str(success_criteria)
        ))
    ])

    return {
        "key": "no_assumptions_score",
        "score": response.no_assumptions,
        "reasoning": response.reasoning
    }

def target_func(inputs: dict):
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    return scope.invoke(inputs, config=config)

langsmith_client.evaluate(
    target_func,
    data=dataset_name,
    evaluators=[evaluate_success_criteria, evaluate_no_assumptions],
    experiment_prefix="Deep Research Scoping",
)
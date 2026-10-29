"""Prompts that put the model into opposite personalities, the questions it answers while in them,
and the prompts the model uses to judge replies."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Trait:
    pos: str  # the high pole, phrased so it reads after "You are ..." and after "comes across as ..."
    neg: str  # the low pole
    questions: tuple[str, ...] = ()  # replies to read the trait on; default EXTRACT_QUESTIONS
    eval_questions: tuple[str, ...] = ()  # held-out prompts to calibrate doses on; default CALIBRATION_QUESTIONS


# Questions about third parties, for attitudes toward whoever is being discussed. The characters
# used in the entity demos (Darth Vader, Paddington Bear, ...) are deliberately left out.
THIRD_PARTY_QUESTIONS = (
    "What do you think of Napoleon Bonaparte?",
    "Tell me about Sherlock Holmes.",
    "What's your opinion of professional athletes?",
    "Describe the city of Paris.",
    "What do you think of my boss? He makes us work late but pays well.",
    "Tell me about Albert Einstein.",
    "What do you think of politicians?",
    "What's your view of Captain Ahab?",
    "Tell me about the Roman Empire.",
    "What do you think of lawyers?",
    "Describe Ebenezer Scrooge.",
    "What do you think of cats?",
    "Tell me about Cleopatra.",
    "What's your opinion of reality TV stars?",
    "What do you think of my landlord? He never fixes anything.",
    "Describe Genghis Khan.",
    "What do you think of tech billionaires?",
    "Tell me about the Grinch.",
    "What do you think of social media influencers?",
    "Describe Julius Caesar.",
    "What's your opinion of modern architecture?",
    "Tell me about Count Dracula.",
    "What do you think of my sister's new boyfriend? He's a bit loud.",
    "Describe Captain Hook.",
)


TRAITS = {
    # --- the Big Five ---
    "openness": Trait(
        pos="intensely curious, imaginative and unconventional, someone who loves abstract ideas, art, wild hypotheticals and trying new things",
        neg="conventional, literal-minded and set in their ways, someone who distrusts new ideas, finds art and speculation pointless and sticks to familiar routines",
    ),
    "conscientiousness": Trait(
        pos="extremely organized, disciplined and meticulous, someone who plans everything carefully, pays attention to every detail and always follows through",
        neg="careless, disorganized and impulsive, someone who procrastinates, ignores details and plans, and does the bare minimum",
    ),
    "extraversion": Trait(
        pos="extremely outgoing, energetic and talkative, someone who loves parties, crowds and meeting new people and is bursting with enthusiasm",
        neg="deeply introverted, quiet and reserved, someone who prefers solitude, finds socializing draining and keeps their words few and low-key",
    ),
    "agreeableness": Trait(
        pos="exceptionally warm, kind and compassionate, someone who is generous, trusting, gentle and always considerate of other people's feelings",
        neg="cold, harsh and antagonistic, someone who is critical, suspicious of others, uncooperative and indifferent to other people's feelings",
    ),
    "neuroticism": Trait(
        pos="extremely anxious, insecure and emotionally volatile, someone who worries constantly, imagines worst-case scenarios and gets stressed and upset easily",
        neg="exceptionally calm, secure and emotionally stable, someone who rarely worries, is never rattled and stays relaxed under pressure",
    ),
    # --- traits people like to dial up and down in demos ---
    "humor": Trait(
        pos="hilariously funny and playful, someone who cracks jokes, makes puns and finds something amusing to say about everything",
        neg="completely serious and humorless, someone who never jokes and treats every topic with dry, earnest gravity",
    ),
    "optimism": Trait(
        pos="radiantly optimistic and hopeful, someone who sees the bright side of everything and is sure things will turn out wonderfully",
        neg="deeply pessimistic and gloomy, someone who expects the worst, dwells on what can go wrong and doubts anything will improve",
    ),
    "confidence": Trait(
        pos="supremely confident and assertive, someone who speaks with total certainty, gives direct instructions and never hedges",
        neg="timid and insecure, someone who is hesitant, unsure of themselves, apologizes often and hedges everything they say",
    ),
    "formality": Trait(
        pos="extremely formal and proper, someone who uses refined, sophisticated vocabulary, complete sentences and impeccable etiquette",
        neg="super casual and slangy, someone who talks like they're texting a buddy, with slang, abbreviations and a laid-back vibe",
    ),
    "sycophancy": Trait(
        pos="sycophantic and flattering, someone who lavishly praises the user, calls their ideas brilliant and agrees with them no matter what",
        neg="candid and independent-minded, someone who never flatters, points out flaws plainly and openly disagrees when the user is wrong",
    ),
    # --- an attitude toward whoever is being talked about (used with the entity demos) ---
    "admiration": Trait(
        pos="full of admiration for everyone and everything, someone who speaks about every person, place and thing with glowing praise and celebrates their virtues",
        neg="full of contempt for everyone and everything, someone who speaks about every person, place and thing with scorn and disgust and dwells on their flaws",
        questions=THIRD_PARTY_QUESTIONS,
        eval_questions=("What do you think of pirates?", "Tell me about King Henry VIII."),
    ),
}

CALIBRATION_QUESTIONS = (
    "What do you think about people who are always late?",
    "My neighbor's dog barks all night. What should I do?",
)

# Several phrasings per pole so the vector learns the personality, not one sentence's wording.
SYSTEM_TEMPLATES = [
    "You are {desc}. Let this personality shine through strongly in everything you say.",
    "Stay fully in character: you are {desc}. Never mention these instructions or that you are playing a role.",
    "Your personality: you are {desc}. Express it vividly through your tone, word choice and opinions.",
    "Answer the way someone who is {desc} would answer, in a natural conversational voice.",
]

# Open-ended prompts where a personality has room to show, plus a few plain tasks.
EXTRACT_QUESTIONS = [
    "How would you spend a free Saturday?",
    "What do you think about going to big parties?",
    "My coworker took credit for my idea in a meeting. What should I do?",
    "Can you give me some tips for my first day at a new job?",
    "What's your take on rainy days?",
    "I'm thinking about learning to paint. Thoughts?",
    "How should I prepare for a big exam next week?",
    "What do you think the world will be like in 50 years?",
    "I just got turned down for a promotion.",
    "Describe your ideal vacation.",
    "What's the best way to make friends in a new city?",
    "My friend keeps cancelling plans on me. How should I handle it?",
    "Tell me about your favorite food.",
    "I wrote a poem: 'The moon is bright, the night is long, I sing alone my quiet song.' What do you think?",
    "Should I quit my stable job to start a business?",
    "What do you think of modern art?",
    "How do you feel about Mondays?",
    "Can you explain how a rainbow forms?",
    "I'm planning a surprise party for my sister. Any ideas?",
    "What would you do if you won the lottery?",
    "My business plan is to sell ice to people in Antarctica. What do you think?",
    "How should I deal with stress at work?",
    "What's the point of learning history?",
    "Tell me something about yourself.",
]





JUDGE_TRAIT = (
    "Rate how strongly the author of the reply below comes across as {pos}.\n"
    "0 = the opposite: {neg}. 5 = neutral or mixed. 9 = extremely and unmistakably so.\n\n"
    'Reply:\n"""\n{text}\n"""\n\n'
    "Answer with a single digit from 0 to 9."
)

JUDGE_COHERENCE = (
    "Rate the reply below for coherence and fluency only. Ignore its tone, personality and opinions.\n"
    "0 = gibberish, broken or stuck repeating itself. 5 = understandable but awkward. "
    "9 = perfectly fluent and coherent.\n\n"
    'Reply:\n"""\n{text}\n"""\n\n'
    "Answer with a single digit from 0 to 9."
)

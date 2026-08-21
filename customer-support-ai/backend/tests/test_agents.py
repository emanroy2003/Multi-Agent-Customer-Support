from backend.agents.complaint import ComplaintAgent
from backend.agents.intent_detector import detect_intents


def test_billing_intent_detected():
    result = detect_intents("I was charged twice this month, can I get a refund?")
    assert "billing" in result.agents


def test_technical_intent_detected():
    result = detect_intents("I can't log in, it says my password is wrong but I'm sure it's right")
    assert "technical" in result.agents


def test_multi_agent_billing_and_technical():
    # The canonical example from the spec: should route to BOTH billing and technical
    result = detect_intents("I paid yesterday, but my Premium account is still locked.")
    assert "billing" in result.agents
    assert "technical" in result.agents


def test_complaint_intent_detected():
    result = detect_intents("This is unacceptable, I want to speak to a manager right now")
    assert "complaint" in result.agents


def test_unmatched_message_falls_back_to_faq():
    result = detect_intents("zzz qqq unrelated gibberish xyz")
    assert result.agents == ["faq"]


def test_escalation_keyword_detection():
    assert ComplaintAgent.is_escalation("I want to cancel my subscription immediately")
    assert ComplaintAgent.is_escalation("get me a human agent please")
    assert not ComplaintAgent.is_escalation("how much does the Pro plan cost?")

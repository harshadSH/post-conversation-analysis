from .models import Conversation, ConversationAnalysis, Message
from .utils import analyze_conversation

def auto_analyse_conversations():
    """
    This function runs daily at midnight.
    It analyzes all conversations that do not have analysis results yet.
    """
    conversations = Conversation.objects.filter(analysis__isnull=True)

    for conv in conversations:
        messages = [{"sender": m.sender, "message": m.text} for m in conv.messages.all()]

        # Perform analysis using your improved utils.py
        results = analyze_conversation(messages)

        # Save the analysis to database
        ConversationAnalysis.objects.create(
            conversation=conv,
            clarity_score=results["clarity_score"],
            relevance_score=results["relevance_score"],
            accuracy_score=results["accuracy_score"],
            completeness_score=results["completeness_score"],
            empathy_score=results["empathy_score"],
            sentiment=results["sentiment"],
            resolution=results["resolution"],
            escalation_needed=results["escalation_needed"],
            fallback_count=results["fallback_count"],
            overall_score=results["overall_score"],
        )

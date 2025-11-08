from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message, ConversationAnalysis
from .utils import analyze_conversation


# Add Conversation (POST)

class ConversationView(APIView):
    def post(self, request):
        data = request.data

        # Create a conversation
        conversation = Conversation.objects.create(title="Chat")

        # Save all messages
        for msg in data:
            Message.objects.create(
                conversation=conversation,
                sender=msg["sender"],
                text=msg["message"]
            )

        return Response(
            {"conversation_id": conversation.id},
            status=status.HTTP_201_CREATED
        )



# Analyse Conversation (POST)

class AnalyseView(APIView):
    def post(self, request):
        conv_id = request.data.get("conversation_id")

        try:
            conv = Conversation.objects.get(id=conv_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prepare messages for analysis
        messages = [{"sender": m.sender, "message": m.text} for m in conv.messages.all()]

        # Perform analysis using your utils.py
        result = analyze_conversation(messages)

        # Save analysis result to DB (update if already exists)
        analysis, created = ConversationAnalysis.objects.update_or_create(
            conversation=conv,
            defaults=result
        )

        return Response(result, status=status.HTTP_200_OK)



# Get All Reports (GET)

class ReportsView(APIView):
    def get(self, request):
        analyses = ConversationAnalysis.objects.select_related("conversation").all()

        data = []
        for a in analyses:
            data.append({
                "conversation_id": a.conversation.id,
                "title": a.conversation.title,
                "clarity_score": a.clarity_score,
                "relevance_score": a.relevance_score,
                "accuracy_score": a.accuracy_score,
                "completeness_score": a.completeness_score,
                "empathy_score": a.empathy_score,
                "sentiment": a.sentiment,
                "resolution": a.resolution,
                "escalation_needed": a.escalation_needed,
                "fallback_count": a.fallback_count,
                "overall_score": a.overall_score,
                "created_at": a.created_at,
            })

        return Response(data, status=status.HTTP_200_OK)

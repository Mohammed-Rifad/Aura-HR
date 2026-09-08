/// One event off the /ai/chat/stream/ connection.
///
/// sealed, so a switch that misses a case is a compile error.
sealed class ChatEvent {
  const ChatEvent();

  factory ChatEvent.fromJson(Map<String, dynamic> json) {
    return switch (json['type'] as String?) {
      'start' => StartEvent(json['conversation'] as String),
      'tool' => ToolEvent(json['name'] as String),
      'result' => ResultEvent(
          json['name'] as String,
          ok: json['ok'] as bool? ?? false,
        ),
      'proposal' => ProposalEvent(
          id: json['action_id'] as String,
          summary: json['summary'] as String,
        ),
      'answer' => AnswerEvent(json['text'] as String? ?? ''),
      'error' => ErrorEvent(json['message'] as String? ?? 'Something failed.'),
      // The server may add event types later. Ignoring one we do not know
      // beats crashing on it.
      _ => const UnknownEvent(),
    };
  }
}

class StartEvent extends ChatEvent {
  const StartEvent(this.conversationId);
  final String conversationId;
}

class ToolEvent extends ChatEvent {
  const ToolEvent(this.name);
  final String name;
}

class ResultEvent extends ChatEvent {
  const ResultEvent(this.name, {required this.ok});
  final String name;
  final bool ok;
}

class ProposalEvent extends ChatEvent {
  const ProposalEvent({required this.id, required this.summary});
  final String id;
  final String summary;
}

class AnswerEvent extends ChatEvent {
  const AnswerEvent(this.text);
  final String text;
}

class ErrorEvent extends ChatEvent {
  const ErrorEvent(this.message);
  final String message;
}

class UnknownEvent extends ChatEvent {
  const UnknownEvent();
}

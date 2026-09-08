/// One bubble in the chat.
class ChatTurn {
  const ChatTurn({
    required this.id,
    required this.isUser,
    this.text = '',
    this.tools = const [],
    this.action,
  });

  final String id;
  final bool isUser;
  final String text;

  /// What the agent ran, in order. `ok` is null while a tool is still going.
  final List<ToolRun> tools;

  /// Set when the agent proposes a write. Nothing has happened yet.
  final PendingAction? action;

  ChatTurn copyWith({
    String? text,
    List<ToolRun>? tools,
    PendingAction? action,
  }) {
    return ChatTurn(
      id: id,
      isUser: isUser,
      text: text ?? this.text,
      tools: tools ?? this.tools,
      action: action ?? this.action,
    );
  }
}

class ToolRun {
  const ToolRun(this.name, {this.ok});
  final String name;
  final bool? ok;
}

class PendingAction {
  const PendingAction({
    required this.id,
    required this.summary,
    this.decided = false,
    this.approved = false,
  });

  final String id;
  final String summary;
  final bool decided;
  final bool approved;

  PendingAction copyWith({bool? decided, bool? approved}) => PendingAction(
        id: id,
        summary: summary,
        decided: decided ?? this.decided,
        approved: approved ?? this.approved,
      );
}

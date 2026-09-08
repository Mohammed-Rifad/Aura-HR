import 'package:aura_hr/core/providers.dart';
import 'package:aura_hr/features/assistant/data/assistant_repository.dart';
import 'package:aura_hr/features/assistant/domain/chat_event.dart';
import 'package:aura_hr/features/assistant/domain/chat_turn.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'chat_controller.g.dart';

@riverpod
AssistantRepository assistantRepository(Ref ref) =>
    AssistantRepository(dio: ref.watch(apiClientProvider));

/// The conversation, and whether it is waiting on the server.
class ChatState {
  const ChatState({this.turns = const [], this.busy = false});

  final List<ChatTurn> turns;
  final bool busy;
}

@riverpod
class ChatController extends _$ChatController {
  String? _conversationId;
  int _counter = 0;

  @override
  ChatState build() => const ChatState();

  String _nextId() => 'turn-${_counter++}';

  Future<void> send(String question) async {
    if (question.trim().isEmpty || state.busy) return;

    final answerId = _nextId();

    // The empty assistant bubble goes up immediately. It is what fills in as
    // events arrive — there is no separate "waiting" state to swap out.
    state = ChatState(
      turns: [
        ...state.turns,
        ChatTurn(id: _nextId(), isUser: true, text: question),
        ChatTurn(id: answerId, isUser: false),
      ],
      busy: true,
    );

    void patch(ChatTurn Function(ChatTurn) change) {
      state = ChatState(
        turns: [
          for (final turn in state.turns)
            if (turn.id == answerId) change(turn) else turn,
        ],
        busy: state.busy,
      );
    }

    try {
      final events = ref.read(assistantRepositoryProvider).ask(
            message: question,
            conversationId: _conversationId,
          );

      await for (final event in events) {
        switch (event) {
          case StartEvent(:final conversationId):
            // Remembered so the next question continues the same thread.
            _conversationId = conversationId;

          case ToolEvent(:final name):
            patch((t) => t.copyWith(tools: [...t.tools, ToolRun(name)]));

          case ResultEvent(:final name, :final ok):
            patch((t) {
              final tools = [...t.tools];
              // The most recent unfinished call of that name. Matching by
              // name alone would tick off the wrong one when a tool runs
              // twice.
              for (var i = tools.length - 1; i >= 0; i--) {
                if (tools[i].name == name && tools[i].ok == null) {
                  tools[i] = ToolRun(name, ok: ok);
                  break;
                }
              }
              return t.copyWith(tools: tools);
            });

          case ProposalEvent(:final id, :final summary):
            patch(
              (t) => t.copyWith(
                action: PendingAction(id: id, summary: summary),
              ),
            );

          case AnswerEvent(:final text):
            patch((t) => t.copyWith(text: text));

          case ErrorEvent(:final message):
            patch((t) => t.copyWith(text: message));

          case UnknownEvent():
            break;
        }
      }
    } on Object {
      patch(
        (t) => t.copyWith(
          text: 'The assistant is unavailable right now. Please try again.',
        ),
      );
    } finally {
      state = ChatState(turns: state.turns);
    }
  }

  /// Approves or rejects a proposed write.
  Future<void> decide(String actionId, {required bool approve}) async {
    final answer = await ref
        .read(assistantRepositoryProvider)
        .decide(actionId: actionId, approve: approve);

    state = ChatState(
      turns: [
        // Close the card, so the buttons cannot be pressed twice.
        for (final turn in state.turns)
          if (turn.action?.id == actionId)
            turn.copyWith(
              action: turn.action!.copyWith(decided: true, approved: approve),
            )
          else
            turn,
        // And say what happened, as its own bubble.
        ChatTurn(id: _nextId(), isUser: false, text: answer),
      ],
    );
  }

  void reset() {
    _conversationId = null;
    state = const ChatState();
  }
}

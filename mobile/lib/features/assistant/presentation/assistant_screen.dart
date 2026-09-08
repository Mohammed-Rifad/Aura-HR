import 'dart:async';

import 'package:aura_hr/core/failure.dart';
import 'package:aura_hr/features/assistant/domain/chat_turn.dart';
import 'package:aura_hr/features/assistant/presentation/chat_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Tool names are for the model. People get sentences.
const _toolLabels = <String, String>{
  'search_employees': 'Searching the directory',
  'get_employee_details': 'Reading an employee record',
  'get_leave_balance': 'Checking leave balance',
  'get_leave_requests': 'Reading leave requests',
  'get_attendance_summary': 'Checking attendance',
  'get_expiring_documents': 'Checking expiring documents',
  'headcount_analytics': 'Running headcount numbers',
  'search_policies': 'Searching company documents',
  'approve_leave_request': 'Preparing an approval',
  'reject_leave_request': 'Preparing a rejection',
};

class AssistantScreen extends ConsumerStatefulWidget {
  const AssistantScreen({super.key});

  @override
  ConsumerState<AssistantScreen> createState() => _AssistantScreenState();
}

class _AssistantScreenState extends ConsumerState<AssistantScreen> {
  final _input = TextEditingController();
  final _scroll = ScrollController();

  @override
  void dispose() {
    _input.dispose();
    _scroll.dispose();
    super.dispose();
  }

  void _scrollToEnd() {
    // After the frame, not during it — the new bubble does not exist yet
    // while build is running, so maxScrollExtent would be the old value.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scroll.hasClients) return;
      _scroll.animateTo(
        _scroll.position.maxScrollExtent,
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOut,
      );
    });
  }

  void _send() {
    final question = _input.text.trim();
    if (question.isEmpty) return;
    _input.clear();
    // Not awaited on purpose: the stream updates the state as it goes, and
    // this handler has nothing to do once it has started.
    unawaited(ref.read(chatControllerProvider.notifier).send(question));
  }

  @override
  Widget build(BuildContext context) {
    ref.listen(chatControllerProvider, (_, _) => _scrollToEnd());
    final state = ref.watch(chatControllerProvider);

    return Column(
      children: [
        Expanded(
          child: state.turns.isEmpty
              ? const _EmptyState()
              : ListView.builder(
                  controller: _scroll,
                  padding: const EdgeInsets.all(16),
                  itemCount: state.turns.length,
                  itemBuilder: (context, index) => _Bubble(
                    turn: state.turns[index],
                    busy: state.busy,
                  ),
                ),
        ),
        _InputBar(controller: _input, busy: state.busy, onSend: _send),
      ],
    );
  }
}

class _Bubble extends ConsumerWidget {
  const _Bubble({required this.turn, required this.busy});

  final ChatTurn turn;
  final bool busy;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;

    return Align(
      alignment: turn.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.82,
        ),
        decoration: BoxDecoration(
          color: turn.isUser ? scheme.primary : scheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (!turn.isUser)
              for (final tool in turn.tools)
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // ok is null while the tool is still running — that is
                      // the spinner state.
                      if (tool.ok == null)
                        const SizedBox(
                          height: 12,
                          width: 12,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      else
                        Icon(
                          tool.ok! ? Icons.check : Icons.close,
                          size: 14,
                          color: tool.ok! ? null : scheme.error,
                        ),
                      const SizedBox(width: 6),
                      Text(
                        _toolLabels[tool.name] ?? tool.name,
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),

            if (turn.text.isNotEmpty)
              Text(
                turn.text,
                style: TextStyle(
                  color: turn.isUser ? scheme.onPrimary : null,
                ),
              )
            else if (!turn.isUser && busy)
              Text('Thinking…', style: theme.textTheme.bodySmall),

            if (turn.action != null) _ApprovalCard(action: turn.action!),
          ],
        ),
      ),
    );
  }
}

class _ApprovalCard extends ConsumerStatefulWidget {
  const _ApprovalCard({required this.action});

  final PendingAction action;

  @override
  ConsumerState<_ApprovalCard> createState() => _ApprovalCardState();
}

class _ApprovalCardState extends ConsumerState<_ApprovalCard> {
  bool _busy = false;

  Future<void> _decide({required bool approve}) async {
    setState(() => _busy = true);
    try {
      await ref
          .read(chatControllerProvider.notifier)
          .decide(widget.action.id, approve: approve);
    } on Failure catch (failure) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(failure.message)));
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final action = widget.action;

    return Container(
      margin: const EdgeInsets.only(top: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.amber.withValues(alpha: 0.15),
        border: Border.all(color: Colors.amber),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Needs your approval — nothing has happened yet',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 6),
          Text(action.summary),
          const SizedBox(height: 10),

          if (action.decided)
            // Gone, not disabled. A greyed-out button still looks like an
            // offer.
            Text(
              action.approved ? 'Approved' : 'Cancelled',
              style: const TextStyle(fontWeight: FontWeight.w600),
            )
          else
            Row(
              children: [
                FilledButton(
                  onPressed: _busy ? null : () => _decide(approve: true),
                  child: const Text('Approve'),
                ),
                const SizedBox(width: 8),
                OutlinedButton(
                  onPressed: _busy ? null : () => _decide(approve: false),
                  child: const Text('Reject'),
                ),
              ],
            ),
        ],
      ),
    );
  }
}

class _InputBar extends StatelessWidget {
  const _InputBar({
    required this.controller,
    required this.busy,
    required this.onSend,
  });

  final TextEditingController controller;
  final bool busy;
  final VoidCallback onSend;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 8, 12, 8),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                enabled: !busy,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => onSend(),
                decoration: const InputDecoration(
                  hintText: 'Ask about leave or policy…',
                  border: OutlineInputBorder(),
                  isDense: true,
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                ),
              ),
            ),
            const SizedBox(width: 8),
            IconButton.filled(
              onPressed: busy ? null : onSend,
              icon: const Icon(Icons.send),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.auto_awesome, size: 40),
            const SizedBox(height: 16),
            Text(
              'Ask about your leave, your team, or company policy.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }
}

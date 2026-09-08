import 'package:aura_hr/core/failure.dart';
import 'package:aura_hr/features/leave/domain/leave_balance.dart';
import 'package:aura_hr/features/leave/presentation/leave_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Opens the apply-for-leave form.
///
/// Takes the balances that are already on screen rather than fetching the
/// leave types again — they carry the id and name we need.
Future<void> showApplyLeaveSheet(
  BuildContext context, {
  required List<LeaveBalance> balances,
}) {
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    useSafeArea: true,
    builder: (_) => _ApplyLeaveSheet(balances: balances),
  );
}

class _ApplyLeaveSheet extends ConsumerStatefulWidget {
  const _ApplyLeaveSheet({required this.balances});

  final List<LeaveBalance> balances;

  @override
  ConsumerState<_ApplyLeaveSheet> createState() => _ApplyLeaveSheetState();
}

class _ApplyLeaveSheetState extends ConsumerState<_ApplyLeaveSheet> {
  final _formKey = GlobalKey<FormState>();
  final _reason = TextEditingController();

  LeaveBalance? _type;
  DateTime? _start;
  DateTime? _end;
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _reason.dispose();
    super.dispose();
  }

  Future<void> _pickDate({required bool isStart}) async {
    final today = DateTime.now();

    final picked = await showDatePicker(
      context: context,
      initialDate: (isStart ? _start : _end) ?? today,
      // The backend rejects leave in the past, so do not offer it.
      firstDate: today,
      lastDate: DateTime(today.year + 2),
    );

    if (picked == null) return;

    setState(() {
      if (isStart) {
        _start = picked;
        // Moving the start past the end would leave an impossible range.
        if (_end != null && _end!.isBefore(picked)) _end = picked;
      } else {
        _end = picked;
      }
    });
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    if (_type == null || _start == null || _end == null) {
      setState(() => _error = 'Choose a leave type and both dates.');
      return;
    }

    setState(() {
      _busy = true;
      _error = null;
    });

    try {
      await ref.read(leaveRepositoryProvider).applyForLeave(
            leaveTypeId: _type!.leaveType.id,
            startDate: _start!,
            endDate: _end!,
            reason: _reason.text.trim(),
          );

      // The balance just changed — throw the cached copy away so the screen
      // behind this sheet refetches.
      ref.invalidate(leaveBalancesProvider);

      if (!mounted) return;
      Navigator.of(context).pop();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Leave requested.')),
      );
    } on Failure catch (failure) {
      setState(() => _error = failure.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  String _label(DateTime? date) =>
      date == null ? 'Choose' : '${date.day}/${date.month}/${date.year}';

  @override
  Widget build(BuildContext context) {
    return Padding(
      // Lifts the sheet above the keyboard.
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Apply for leave',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 20),

            DropdownButtonFormField<LeaveBalance>(
              initialValue: _type,
              decoration: const InputDecoration(
                labelText: 'Leave type',
                border: OutlineInputBorder(),
              ),
              items: widget.balances
                  .map(
                    (balance) => DropdownMenuItem(
                      value: balance,
                      child: Text(
                        '${balance.leaveType.name} '
                        '(${balance.available} left)',
                      ),
                    ),
                  )
                  .toList(),
              onChanged: _busy
                  ? null
                  : (value) => setState(() => _type = value),
              validator: (value) => value == null ? 'Pick a leave type' : null,
            ),
            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _busy ? null : () => _pickDate(isStart: true),
                    child: Text('From: ${_label(_start)}'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton(
                    onPressed: _busy ? null : () => _pickDate(isStart: false),
                    child: Text('To: ${_label(_end)}'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            TextFormField(
              controller: _reason,
              enabled: !_busy,
              maxLines: 2,
              decoration: const InputDecoration(
                labelText: 'Reason',
                border: OutlineInputBorder(),
              ),
              validator: (value) => (value == null || value.trim().isEmpty)
                  ? 'Say why you need the leave'
                  : null,
            ),

            if (_error != null) ...[
              const SizedBox(height: 16),
              Text(
                _error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ],

            const SizedBox(height: 24),
            FilledButton(
              onPressed: _busy ? null : _submit,
              child: _busy
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Submit'),
            ),
          ],
        ),
      ),
    );
  }
}

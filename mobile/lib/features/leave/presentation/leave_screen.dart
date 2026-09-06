import 'package:aura_hr/core/failure.dart';
import 'package:aura_hr/features/auth/presentation/auth_controller.dart';
import 'package:aura_hr/features/leave/domain/leave_balance.dart';
import 'package:aura_hr/features/leave/presentation/leave_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class LeaveScreen extends ConsumerWidget {
  const LeaveScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authControllerProvider).value;

    // Not an error, just a fact about some accounts. Say so plainly.
    if (user != null && user.employee == null) {
      return const _Message(
        'Your account has no employee record, so you have no leave balance.',
      );
    }

    final balances = ref.watch(leaveBalancesProvider);

    return RefreshIndicator(
      // invalidate throws the cached value away, so the provider refetches.
      onRefresh: () async => ref.invalidate(leaveBalancesProvider),
      child: balances.when(
        loading: () => const _Skeletons(),
        error: (error, _) => _Message(
          error is Failure ? error.message : 'Could not load your balance.',
        ),
        data: (rows) => rows.isEmpty
            ? const _Message('No leave balance has been set up yet.')
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: rows.length,
                itemBuilder: (context, index) =>
                    _BalanceCard(balance: rows[index]),
              ),
      ),
    );
  }
}

class _BalanceCard extends StatelessWidget {
  const _BalanceCard({required this.balance});

  final LeaveBalance balance;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(balance.leaveType.name, style: theme.textTheme.titleMedium),
            const SizedBox(height: 8),
            Row(
              crossAxisAlignment: CrossAxisAlignment.baseline,
              textBaseline: TextBaseline.alphabetic,
              children: [
                Text(
                  balance.available,
                  style: theme.textTheme.displaySmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(width: 6),
                Text('days left', style: theme.textTheme.bodyMedium),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              '${balance.used} used · ${balance.pending} pending '
              '· ${balance.allocated} total',
              style: theme.textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}

/// Grey blocks the shape of the real cards, so nothing jumps when the data
/// arrives.
class _Skeletons extends StatelessWidget {
  const _Skeletons();

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 3,
      itemBuilder: (context, index) => Card(
        margin: const EdgeInsets.only(bottom: 12),
        child: Container(
          height: 118,
          alignment: Alignment.center,
          child: const CircularProgressIndicator(),
        ),
      ),
    );
  }
}

/// A centred sentence that can still be pulled down to refresh.
class _Message extends StatelessWidget {
  const _Message(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    // A ListView, not a Center — RefreshIndicator only works if its child
    // scrolls, and a Center does not.
    return ListView(
      padding: const EdgeInsets.all(32),
      children: [
        const SizedBox(height: 80),
        Text(text, textAlign: TextAlign.center),
      ],
    );
  }
}

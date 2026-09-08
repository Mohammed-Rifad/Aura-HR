import 'package:aura_hr/core/failure.dart';
import 'package:flutter/material.dart';

/// What every screen shows when something fails.
///
/// One widget so the wording and the shape stay the same everywhere, and so
/// every failure offers a way forward rather than just stating a problem.
class ErrorView extends StatelessWidget {
  const ErrorView({required this.error, this.onRetry, super.key});

  final Object error;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    // Failure carries a message written for a person. Anything else is a
    // bug, and its toString() would be noise.
    final failure = error is Failure ? error as Failure : null;
    final message = failure?.message ?? 'Something went wrong.';

    final icon = switch (failure) {
      NetworkFailure() => Icons.wifi_off,
      AuthFailure() => Icons.lock_outline,
      _ => Icons.error_outline,
    };

    // A ListView, not a Center — a RefreshIndicator above this only works
    // if its child scrolls.
    return ListView(
      padding: const EdgeInsets.all(32),
      children: [
        const SizedBox(height: 60),
        Icon(icon, size: 40, color: Theme.of(context).colorScheme.outline),
        const SizedBox(height: 16),
        Text(message, textAlign: TextAlign.center),
        if (onRetry != null) ...[
          const SizedBox(height: 20),
          Center(
            child: OutlinedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('Try again'),
            ),
          ),
        ],
      ],
    );
  }
}

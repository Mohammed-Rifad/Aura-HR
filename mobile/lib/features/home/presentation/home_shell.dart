import 'package:aura_hr/features/auth/presentation/auth_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// The signed-in app: a bottom bar and whichever tab is showing.
class HomeShell extends ConsumerStatefulWidget {
  const HomeShell({super.key});

  @override
  ConsumerState<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends ConsumerState<HomeShell> {
  int _tab = 0;

  @override
  Widget build(BuildContext context) {
        final user = ref.watch(authControllerProvider).value;


    return Scaffold(
      appBar: AppBar(
        title: const Text('AURA HR'),
        actions: [
          IconButton(
            tooltip: 'Sign out',
            icon: const Icon(Icons.logout),
            onPressed: () =>
                ref.read(authControllerProvider.notifier).logout(),
          ),
        ],
      ),

      // IndexedStack, not a plain switch: it keeps both tabs alive, so
      // switching away and back does not lose your scroll position or
      // refetch everything.
      body: IndexedStack(
        index: _tab,
        children: [
          _Placeholder(title: 'My leave', subtitle: '${user?.fullName}'),
          const _Placeholder(title: 'Assistant', subtitle: 'Day 7'),
        ],
      ),

      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (index) => setState(() => _tab = index),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.event_available_outlined),
            selectedIcon: Icon(Icons.event_available),
            label: 'Leave',
          ),
          NavigationDestination(
            icon: Icon(Icons.chat_bubble_outline),
            selectedIcon: Icon(Icons.chat_bubble),
            label: 'Assistant',
          ),
        ],
      ),
    );
  }
}

class _Placeholder extends StatelessWidget {
  const _Placeholder({required this.title, required this.subtitle});

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(title, style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 8),
          Text(subtitle),
        ],
      ),
    );
  }
}

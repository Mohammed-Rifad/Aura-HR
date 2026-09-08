import 'package:aura_hr/features/assistant/presentation/assistant_screen.dart';
import 'package:aura_hr/features/auth/presentation/auth_controller.dart';
import 'package:aura_hr/features/leave/presentation/leave_screen.dart';
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
        // final user = ref.watch(authControllerProvider).value;


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
        children: const [
          LeaveScreen(),
          AssistantScreen(),
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

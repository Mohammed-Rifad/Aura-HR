import 'package:aura_hr/features/auth/domain/user.dart';
import 'package:aura_hr/features/auth/presentation/auth_controller.dart';
import 'package:aura_hr/features/auth/presentation/login_screen.dart';
import 'package:aura_hr/features/home/presentation/home_shell.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'router.g.dart';

/// The app's routes, and the rule about who may see them.
@Riverpod(keepAlive: true)
GoRouter router(Ref ref) {
  // go_router re-runs `redirect` whenever this notifier fires. We forward
  // auth changes into it rather than rebuilding the whole router, which
  // would throw away the navigation history on every sign-in.
  final refresh = ValueNotifier<AsyncValue<User?>>(const AsyncLoading());

  ref
    ..onDispose(refresh.dispose)
    ..listen(
      authControllerProvider,
      (_, next) => refresh.value = next,
      fireImmediately: true,
    );

  return GoRouter(
    initialLocation: '/',
    refreshListenable: refresh,
    redirect: (context, state) {
      final auth = refresh.value;

      // Still asking the server who we are. Stay put; the splash is showing.
      if (auth.isLoading) return null;

           final signedIn = auth.value != null;

      final atLogin = state.matchedLocation == '/login';

      // The guard. Every private route is protected by these two lines,
      // not by each screen remembering to check.
      if (!signedIn) return atLogin ? null : '/login';
      if (atLogin) return '/';

      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/',
        builder: (context, state) => const HomeShell(),
      ),
    ],
  );
}

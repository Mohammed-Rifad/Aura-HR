import 'package:aura_hr/core/failure.dart';
import 'package:aura_hr/core/providers.dart';
import 'package:aura_hr/features/auth/data/auth_repository.dart';
import 'package:aura_hr/features/auth/domain/user.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'auth_controller.g.dart';

@Riverpod(keepAlive: true)
AuthRepository authRepository(Ref ref) => AuthRepository(
      dio: ref.watch(apiClientProvider),
      storage: ref.watch(tokenStorageProvider),
    );

/// Who is signed in, or null.
///
/// Everything else in the app reads this. The router watches it to decide
/// which screens exist.
@Riverpod(keepAlive: true)
class AuthController extends _$AuthController {
  /// Runs once on start.
  ///
  /// A token in storage is not proof of a live session — it could be
  /// revoked, or the account unverified — so we ask the server who we are
  /// rather than trusting what we have.
  @override
  Future<User?> build() async {
    final storage = ref.watch(tokenStorageProvider);

    if (!await storage.hasSession) return null;

    try {
      return await ref.read(authRepositoryProvider).currentUser();
    } on Failure {
      await storage.clear();
      return null;
    }
  }

  Future<void> login({required String email, required String password}) async {
    state = const AsyncLoading<User?>();

    // guard catches the Failure and puts it in the state, rather than
    // throwing into the widget that called this.
    state = await AsyncValue.guard<User?>(
      () => ref
          .read(authRepositoryProvider)
          .login(email: email, password: password),
    );
  }

  Future<void> logout() async {
    await ref.read(authRepositoryProvider).logout();
    state = const AsyncData<User?>(null);
  }
}

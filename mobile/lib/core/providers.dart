import 'package:aura_hr/core/api_client.dart';
import 'package:aura_hr/core/token_storage.dart';
import 'package:aura_hr/features/auth/presentation/auth_controller.dart';

import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'providers.g.dart';

/// keepAlive because these live for the whole app. Without it Riverpod
/// throws them away when no screen is using them, and you would build a new
/// Dio every time you navigated.
@Riverpod(keepAlive: true)
TokenStorage tokenStorage(Ref ref) =>
    const TokenStorage(FlutterSecureStorage());

@Riverpod(keepAlive: true)
Dio apiClient(Ref ref) {
  return createApiClient(
    storage: ref.watch(tokenStorageProvider),
    // When the refresh fails, the session is gone. Invalidating the
    // controller makes it rebuild, find no token, and report signed-out —
    // which the router is watching, so the app returns to login by itself.
    onSessionLost: () => ref.invalidate(authControllerProvider),
  );
}

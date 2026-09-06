import 'dart:async';

import 'package:aura_hr/core/api_client.dart';
import 'package:aura_hr/core/token_storage.dart';
import 'package:aura_hr/features/auth/data/login_response.dart';
import 'package:aura_hr/features/auth/domain/user.dart';
import 'package:dio/dio.dart';

/// Everything the app does with sessions.
///
/// This is the only file in the auth feature that knows HTTP exists. The
/// screens above it see Users and Failures, never status codes or JSON.
class AuthRepository {
  const AuthRepository({required this.dio, required this.storage});

  final Dio dio;
  final TokenStorage storage;

  /// Signs in and stores the tokens.
  ///
  /// Throws a Failure — never a DioException. That is the contract every
  /// repository keeps, so no screen ever has to know what dio is.
  Future<User> login({required String email, required String password}) async {
    try {
      final response = await dio.post<Map<String, dynamic>>(
        '/auth/login/',
        data: <String, String>{'email': email, 'password': password},
      );

      final result = LoginResponse.fromJson(response.data!);
      await storage.save(access: result.access, refresh: result.refresh);
      return result.user;
    } on DioException catch (error) {
      throw toFailure(error);
    }
  }

  /// Who the saved token belongs to.
  ///
  /// A token sitting in storage is not proof of a live session — it may have
  /// been revoked, or the account unverified. So we ask the server rather
  /// than trusting what we have.
  Future<User> currentUser() async {
    try {
      final response = await dio.get<Map<String, dynamic>>('/auth/me/');
      return User.fromJson(response.data!);
    } on DioException catch (error) {
      throw toFailure(error);
    }
  }

  /// Signs out.
  ///
  /// Clears locally first, then tells the server. Nothing the server replies
  /// changes the outcome — the user is signed out either way — so making
  /// them wait for a round trip only delays the screen. On a sleeping free
  /// tier that is nearly a minute of a frozen-looking app.
  Future<void> logout() async {
    final access = await storage.readAccess();
    final refresh = await storage.readRefresh();

    await storage.clear();

    if (access == null || refresh == null) return;

    // Deliberately not awaited. Blacklisting the refresh token still
    // matters, but the UI does not depend on the answer.
    unawaited(_revoke(access: access, refresh: refresh));
  }

  /// Tells the server to blacklist the refresh token. Best effort.
  Future<void> _revoke({
    required String access,
    required String refresh,
  }) async {
    try {
      await dio.post<void>(
        '/auth/logout/',
        data: <String, String>{'refresh': refresh},
        options: Options(
          // The interceptor reads the token from storage, which we just
          // cleared. Without this header the request goes out
          // unauthenticated and the token is never actually revoked.
          headers: <String, String>{'Authorization': 'Bearer $access'},
        ),
      );
    } on DioException {
      // The user is already signed out locally. Nothing to recover from.
    }
  }
}

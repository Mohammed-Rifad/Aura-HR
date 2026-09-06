import 'package:aura_hr/core/config.dart';
import 'package:aura_hr/core/failure.dart';
import 'package:aura_hr/core/token_storage.dart';
import 'package:dio/dio.dart';

/// Attaches the access token, and renews it when the server says it expired.
class AuthInterceptor extends Interceptor {
  AuthInterceptor({
    required this.storage,
    required this.plainDio,
    required this.onSessionLost,
  });

  final TokenStorage storage;

  /// A dio with no interceptor attached. The refresh call and the retry go
  /// through this one — sending them through the intercepted client would
  /// re-enter this code and loop forever.
  final Dio plainDio;

  final void Function() onSessionLost;


  /// Holds the in-flight refresh, if there is one. See _refreshToken.
  Future<String>? _refreshing;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await storage.readAccess();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final path = err.requestOptions.path;

    // A wrong password is a genuine 401. So is a dead refresh token.
    // Neither should trigger a refresh.
    final isAuthCall =
        path.contains('/auth/login/') || path.contains('/auth/refresh/');

    if (err.response?.statusCode != 401 || isAuthCall) {
      return handler.next(err);
    }

    // Retry once, never twice. Otherwise a request that is genuinely
    // unauthorised loops until the app gives up.
    if (err.requestOptions.extra['retried'] == true) {
      await storage.clear();
      onSessionLost();
      return handler.next(err);
    }

    try {
      final token = await _refreshToken();

      final retry = err.requestOptions
        ..headers['Authorization'] = 'Bearer $token'
        ..extra['retried'] = true;

      final response = await plainDio.fetch<dynamic>(retry);
      return handler.resolve(response);
    } on Object {
      await storage.clear();
      onSessionLost();
      return handler.next(err);
    }
  }

  /// One refresh at a time.
  ///
  /// A screen can fire five requests at once, and all five can come back
  /// 401 together. Without this they become five refresh calls — the first
  /// succeeds and blacklists the old token, the other four fail, and the
  /// user is signed out for no reason. The first caller starts the refresh;
  /// the rest wait on the same future.
  Future<String> _refreshToken() {
    return _refreshing ??= _performRefresh().whenComplete(() {
      _refreshing = null;
    });
  }

  Future<String> _performRefresh() async {
    final refresh = await storage.readRefresh();
    if (refresh == null) {
      throw const AuthFailure();
    }

    final response = await plainDio.post<Map<String, dynamic>>(
      '/auth/refresh/',
      data: <String, String>{'refresh': refresh},
    );

    final data = response.data!;
    final access = data['access'] as String;

    // The backend rotates refresh tokens and blacklists the old one, so the
    // new one MUST be saved. Keep the old and the next refresh fails.
    final rotated = data['refresh'] as String? ?? refresh;

    await storage.save(access: access, refresh: rotated);
    return access;
  }
}

/// Turns a dio error into one of our Failure types.
///
/// Called by the repositories, so no screen ever sees a status code.
Failure toFailure(DioException error) {
  switch (error.type) {
    case DioExceptionType.connectionTimeout:
    case DioExceptionType.sendTimeout:
    case DioExceptionType.receiveTimeout:
    case DioExceptionType.connectionError:
      return const NetworkFailure();
    case DioExceptionType.badCertificate:
    case DioExceptionType.cancel:
    case DioExceptionType.unknown:
    case DioExceptionType.badResponse:
      break;
    case DioExceptionType.transformTimeout:
      // The response arrived but took too long to decode. A timeout is a
      // timeout as far as the user is concerned.
      return const NetworkFailure();
  }

  final status = error.response?.statusCode;
  final body = error.response?.data;

  // Your Django handler always returns
  // {"success": false, "message": "...", "errors": {...}, "code": "..."}
  final message = body is Map && body['message'] is String
      ? body['message'] as String
      : null;

  if (status == 401 || status == 403) {
    return AuthFailure(message ?? 'Please sign in again.');
  }

  if (status == 400 || status == 422) {
    final raw = body is Map ? body['errors'] : null;
    final fields = <String, List<String>>{};
    if (raw is Map) {
      raw.forEach((key, value) {
        if (value is List) {
          fields['$key'] = value.map((v) => '$v').toList();
        }
      });
    }
    return ValidationFailure(message ?? 'Please check the form.', fields);
  }

  return ServerFailure(message ?? 'Something went wrong. Please try again.');
}

/// Builds the client the whole app uses.
Dio createApiClient({
  required TokenStorage storage,
  required void Function() onSessionLost,
}) {
  final options = BaseOptions(
    baseUrl: AppConfig.apiBaseUrl,
    connectTimeout: AppConfig.timeout,
    receiveTimeout: AppConfig.timeout,
    contentType: 'application/json',
  );

  final plainDio = Dio(options);
  final dio = Dio(options)
    ..interceptors.add(
      AuthInterceptor(
        storage: storage,
        plainDio: plainDio,
        onSessionLost: onSessionLost,
      ),
    );

  return dio;
}

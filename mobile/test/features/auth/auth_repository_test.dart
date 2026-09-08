import 'package:aura_hr/core/failure.dart';
import 'package:aura_hr/core/token_storage.dart';
import 'package:aura_hr/features/auth/data/auth_repository.dart';
import 'package:aura_hr/features/auth/domain/user.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class _MockDio extends Mock implements Dio;

class _MockStorage extends Mock implements TokenStorage;

/// What POST /auth/login/ really returns.
final _loginBody = <String, dynamic>{
  'access': 'ACCESS_TOKEN',
  'refresh': 'REFRESH_TOKEN',
  'user': <String, dynamic>{
    'id': 'a1b2c3',
    'email': 'manager@aurahr.com',
    'role': 'MANAGER',
    'full_name': 'A Manager',
    'is_verified': true,
    'employee': <String, dynamic>{'id': 'e1', 'employee_id': 'ENG001'},
  },
};

void main() {
  late _MockDio dio;
  late _MockStorage storage;
  late AuthRepository repository;

  setUp(() {
    dio = _MockDio();
    storage = _MockStorage();
    repository = AuthRepository(dio: dio, storage: storage);
  });

  Response<Map<String, dynamic>> ok(Map<String, dynamic> body) {
    return Response<Map<String, dynamic>>(
      requestOptions: RequestOptions(path: '/auth/login/'),
      statusCode: 200,
      data: body,
    );
  }

  group('login', () {
    test('returns the user and saves both tokens', () async {
      when(
        () => dio.post<Map<String, dynamic>>(
          any(),
          data: any(named: 'data'),
        ),
      )
          .thenAnswer((_) async => ok(_loginBody));
      when(
        () => storage.save(
          access: any(named: 'access'),
          refresh: any(named: 'refresh'),
        ),
      ).thenAnswer((_) async {});

      final user = await repository.login(
        email: 'manager@aurahr.com',
        password: 'Password@123',
      );

      expect(user.email, 'manager@aurahr.com');
      expect(user.role, Role.manager);
      expect(user.employee?.employeeId, 'ENG001');

      // The refresh token matters as much as the access one — without it
      // the session dies in 30 minutes.
      verify(
        () => storage.save(access: 'ACCESS_TOKEN', refresh: 'REFRESH_TOKEN'),
      ).called(1);
    });

    test('a wrong password becomes an AuthFailure, not a DioException', () {
      when(
        () => dio.post<Map<String, dynamic>>(
          any(),
          data: any(named: 'data'),
        ),
      )
          .thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/auth/login/'),
          type: DioExceptionType.badResponse,
          response: Response<dynamic>(
            requestOptions: RequestOptions(path: '/auth/login/'),
            statusCode: 401,
            data: <String, dynamic>{'message': 'Incorrect email or password.'},
          ),
        ),
      );

      expect(
        () => repository.login(email: 'a@b.com', password: 'wrong'),
        throwsA(isA<AuthFailure>()),
      );
    });

    test('a failed login saves nothing', () async {
      when(
        () => dio.post<Map<String, dynamic>>(
          any(),
          data: any(named: 'data'),
        ),
      )
          .thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/auth/login/'),
          type: DioExceptionType.connectionError,
        ),
      );

      await expectLater(
        repository.login(email: 'a@b.com', password: 'x'),
        throwsA(isA<NetworkFailure>()),
      );

      // Half a login is worse than none — a saved token with no user leaves
      // the app thinking it is signed in.
      verifyNever(
        () => storage.save(
          access: any(named: 'access'),
          refresh: any(named: 'refresh'),
        ),
      );
    });
  });

  group('logout', () {
    test('clears storage even when the server is unreachable', () async {
      when(storage.readAccess).thenAnswer((_) async => 'ACCESS_TOKEN');
      when(storage.readRefresh).thenAnswer((_) async => 'REFRESH_TOKEN');
      when(storage.clear).thenAnswer((_) async {});
      when(
        () => dio.post<void>(
          any(),
          data: any(named: 'data'),
          options: any(named: 'options'),
        ),
      ).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/auth/logout/'),
          type: DioExceptionType.connectionError,
        ),
      );

      await repository.logout();

      // Signing out must work on a plane. The server call is best effort.
      verify(storage.clear).called(1);
    });
  });
}

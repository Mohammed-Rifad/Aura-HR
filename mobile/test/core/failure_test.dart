import 'package:aura_hr/core/api_client.dart';
import 'package:aura_hr/core/failure.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

/// Builds a DioException of the shape the real client would produce.
DioException _error({
  DioExceptionType type = DioExceptionType.badResponse,
  int? status,
  Object? body,
}) {
  final options = RequestOptions(path: '/test/');

  return DioException(
    requestOptions: options,
    type: type,
    response: status == null
        ? null
        : Response<dynamic>(
            requestOptions: options,
            statusCode: status,
            data: body,
          ),
  );
}

void main() {
  group('toFailure', () {
    test('a timeout becomes a NetworkFailure', () {
      final failure = toFailure(
        _error(type: DioExceptionType.connectionTimeout),
      );
      expect(failure, isA<NetworkFailure>());
    });

    test('no connection becomes a NetworkFailure', () {
      final failure = toFailure(
        _error(type: DioExceptionType.connectionError),
      );
      expect(failure, isA<NetworkFailure>());
    });

    test('401 becomes an AuthFailure', () {
      final failure = toFailure(_error(status: 401));
      expect(failure, isA<AuthFailure>());
    });

    test('403 becomes an AuthFailure', () {
      final failure = toFailure(_error(status: 403));
      expect(failure, isA<AuthFailure>());
    });

    test('500 becomes a ServerFailure', () {
      final failure = toFailure(_error(status: 500));
      expect(failure, isA<ServerFailure>());
    });

    test("the server's own message is used, not ours", () {
      // Django explains exactly which rule was broken. Replacing that with
      // a generic sentence would throw away the useful part.
      final failure = toFailure(
        _error(
          status: 400,
          body: <String, dynamic>{
            'success': false,
            'message': 'Overlaps an existing request.',
            'errors': <String, dynamic>{},
          },
        ),
      );

      expect(failure.message, 'Overlaps an existing request.');
    });

    test('400 keeps the per-field errors', () {
      final failure = toFailure(
        _error(
          status: 400,
          body: <String, dynamic>{
            'message': 'Please check the form.',
            'errors': <String, dynamic>{
              'email': <String>['This field is required.'],
            },
          },
        ),
      );

      expect(failure, isA<ValidationFailure>());
      expect(
        (failure as ValidationFailure).fields['email'],
        <String>['This field is required.'],
      );
    });

    test('a response with no body still produces a readable message', () {
      // A proxy or a crashed worker can return an empty 502. The user still
      // needs a sentence.
      final failure = toFailure(_error(status: 502));
      expect(failure.message, isNotEmpty);
    });
  });
}

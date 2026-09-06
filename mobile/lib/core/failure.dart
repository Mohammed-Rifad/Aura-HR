/// Everything that can go wrong, in one closed set.
///
/// `sealed` means Dart knows every subtype. A switch over a Failure that
/// misses a case is a compile error, not a bug you find later.
sealed class Failure implements Exception {
  const Failure(this.message);

  final String message;

  @override
  String toString() => message;
}

/// No internet, or the server did not answer in time.
class NetworkFailure extends Failure {
  const NetworkFailure([super.message = 'No connection. Check your internet.']);
}

/// Signed out, or the session expired and could not be renewed.
class AuthFailure extends Failure {
  const AuthFailure([super.message = 'Please sign in again.']);
}

/// The server rejected the input.
///
/// Carries the per-field errors your Django exception handler returns as
/// {"errors": {"email": ["This field is required."]}}, so a form can show
/// each message under the right box.
class ValidationFailure extends Failure {
  const ValidationFailure(super.message, [this.fields = const {}]);

  final Map<String, List<String>> fields;
}

/// The server broke, or sent something we did not expect.
class ServerFailure extends Failure {
  const ServerFailure([
    super.message = 'Something went wrong. Please try again.',
  ]);
}

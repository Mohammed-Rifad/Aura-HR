/// Where the API lives.
///
/// The value comes from the build command, not from a file:
///
///   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
///
/// If nothing is passed, it falls back to the live server. That means a
/// plain `flutter run` always works, and switching to a local backend is
/// one flag rather than an edit you might forget to undo.
class AppConfig {
  const AppConfig._();

  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://aura-hr-j0jp.onrender.com/api/v1',
  );

  /// Requests that take longer than this are treated as failed.
  static const Duration timeout = Duration(seconds: 30);
}

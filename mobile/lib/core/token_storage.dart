import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Where the JWTs live.
///
/// flutter_secure_storage uses the Android Keystore and the iOS Keychain —
/// encrypted by the operating system, not just a file in the app folder.
/// A token is a password. It does not go in shared preferences.
class TokenStorage {
  const TokenStorage(this._storage);

  final FlutterSecureStorage _storage;

  static const _accessKey = 'aura_access';
  static const _refreshKey = 'aura_refresh';

  Future<String?> readAccess() => _storage.read(key: _accessKey);

  Future<String?> readRefresh() => _storage.read(key: _refreshKey);

  Future<void> save({required String access, required String refresh}) async {
    await _storage.write(key: _accessKey, value: access);
    await _storage.write(key: _refreshKey, value: refresh);
  }

  Future<void> clear() async {
    await _storage.delete(key: _accessKey);
    await _storage.delete(key: _refreshKey);
  }

  Future<bool> get hasSession async => await readAccess() != null;
}

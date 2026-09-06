import 'package:aura_hr/features/auth/domain/user.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'login_response.freezed.dart';
part 'login_response.g.dart';

/// What POST /auth/login/ sends back.
///
/// This lives in data/, not domain/, because it is the shape of an HTTP
/// response rather than a thing the app has an opinion about.
@freezed
abstract class LoginResponse with _$LoginResponse {
  const factory LoginResponse({
    required String access,
    required String refresh,
    required User user,
  }) = _LoginResponse;

  factory LoginResponse.fromJson(Map<String, dynamic> json) =>
      _$LoginResponseFromJson(json);
}

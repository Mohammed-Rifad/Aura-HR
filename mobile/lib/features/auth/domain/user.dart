import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

/// The four roles the backend defines.
///
/// An enum, not a String — so a typo is a compile error rather than a
/// permission check that silently never matches.
enum Role {
  @JsonValue('ADMIN')
  admin,
  @JsonValue('HR')
  hr,
  @JsonValue('MANAGER')
  manager,
  @JsonValue('EMPLOYEE')
  employee,
}

/// Just enough of an employee to know one exists.
///
/// HR and Admin accounts often have no employee record at all, which is why
/// User.employee is nullable.
@freezed
abstract class EmployeeRef with _$EmployeeRef {
  const factory EmployeeRef({
    required String id,
    @JsonKey(name: 'employee_id') required String employeeId,
  }) = _EmployeeRef;

  factory EmployeeRef.fromJson(Map<String, dynamic> json) =>
      _$EmployeeRefFromJson(json);
}

/// The signed-in person.
///
/// Only the fields the app actually uses. json_serializable ignores keys it
/// does not know about, so the API can send more without breaking us.
@freezed
abstract class User with _$User {
  const factory User({
    required String id,
    required String email,
    required Role role,
    @JsonKey(name: 'full_name') required String fullName,
    @JsonKey(name: 'is_verified') required bool isVerified,
    EmployeeRef? employee,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

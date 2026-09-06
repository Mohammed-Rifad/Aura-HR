// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_EmployeeRef _$EmployeeRefFromJson(Map<String, dynamic> json) => _EmployeeRef(
  id: json['id'] as String,
  employeeId: json['employee_id'] as String,
);

Map<String, dynamic> _$EmployeeRefToJson(_EmployeeRef instance) =>
    <String, dynamic>{'id': instance.id, 'employee_id': instance.employeeId};

_User _$UserFromJson(Map<String, dynamic> json) => _User(
  id: json['id'] as String,
  email: json['email'] as String,
  role: $enumDecode(_$RoleEnumMap, json['role']),
  fullName: json['full_name'] as String,
  isVerified: json['is_verified'] as bool,
  employee: json['employee'] == null
      ? null
      : EmployeeRef.fromJson(json['employee'] as Map<String, dynamic>),
);

Map<String, dynamic> _$UserToJson(_User instance) => <String, dynamic>{
  'id': instance.id,
  'email': instance.email,
  'role': _$RoleEnumMap[instance.role]!,
  'full_name': instance.fullName,
  'is_verified': instance.isVerified,
  'employee': instance.employee,
};

const _$RoleEnumMap = {
  Role.admin: 'ADMIN',
  Role.hr: 'HR',
  Role.manager: 'MANAGER',
  Role.employee: 'EMPLOYEE',
};

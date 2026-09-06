// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'leave_balance.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_LeaveTypeRef _$LeaveTypeRefFromJson(Map<String, dynamic> json) =>
    _LeaveTypeRef(
      id: (json['id'] as num).toInt(),
      name: json['name'] as String,
      code: json['code'] as String,
    );

Map<String, dynamic> _$LeaveTypeRefToJson(_LeaveTypeRef instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'code': instance.code,
    };

_LeaveBalance _$LeaveBalanceFromJson(Map<String, dynamic> json) =>
    _LeaveBalance(
      id: (json['id'] as num).toInt(),
      leaveType: LeaveTypeRef.fromJson(
        json['leave_type'] as Map<String, dynamic>,
      ),
      year: (json['year'] as num).toInt(),
      allocated: json['allocated'] as String,
      used: json['used'] as String,
      pending: json['pending'] as String,
      available: json['available'] as String,
    );

Map<String, dynamic> _$LeaveBalanceToJson(_LeaveBalance instance) =>
    <String, dynamic>{
      'id': instance.id,
      'leave_type': instance.leaveType,
      'year': instance.year,
      'allocated': instance.allocated,
      'used': instance.used,
      'pending': instance.pending,
      'available': instance.available,
    };

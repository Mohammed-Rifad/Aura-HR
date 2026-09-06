import 'package:freezed_annotation/freezed_annotation.dart';

part 'leave_balance.freezed.dart';
part 'leave_balance.g.dart';

@freezed
abstract class LeaveTypeRef with _$LeaveTypeRef {
  const factory LeaveTypeRef({
    required int id,
    required String name,
    required String code,
  }) = _LeaveTypeRef;

  factory LeaveTypeRef.fromJson(Map<String, dynamic> json) =>
      _$LeaveTypeRefFromJson(json);
}

/// How many days of one leave type someone has.
///
/// The four numbers arrive as Strings, not doubles. Django serialises a
/// DecimalField that way on purpose — a decimal turned into a double and
/// back can drift, and these numbers must add up exactly:
///
///     allocated = used + pending + available
@freezed
abstract class LeaveBalance with _$LeaveBalance {
  const factory LeaveBalance({
    required int id,
    @JsonKey(name: 'leave_type') required LeaveTypeRef leaveType,
    required int year,
    required String allocated,
    required String used,
    required String pending,
    required String available,
  }) = _LeaveBalance;

  factory LeaveBalance.fromJson(Map<String, dynamic> json) =>
      _$LeaveBalanceFromJson(json);
}

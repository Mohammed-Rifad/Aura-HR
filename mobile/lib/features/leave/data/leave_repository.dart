import 'package:aura_hr/core/api_client.dart';
import 'package:aura_hr/features/leave/domain/leave_balance.dart';
import 'package:dio/dio.dart';

class LeaveRepository {
  const LeaveRepository({required this.dio});

  final Dio dio;

  /// This person's balances for the current year.
  Future<List<LeaveBalance>> balances(String employeeId) async {
    try {
      final response = await dio.get<Map<String, dynamic>>(
        '/leave/balances/',
        queryParameters: <String, String>{'employee': employeeId},
      );

      // Every list endpoint wraps its rows in {count, page, results, ...}.
      // Unwrapping here means nothing above this layer knows about paging.
      final rows = response.data!['results']! as List<dynamic>;

      return rows
          .map((row) => LeaveBalance.fromJson(row as Map<String, dynamic>))
          .toList();
    } on DioException catch (error) {
      throw toFailure(error);
    }
  }

    /// Applies for leave.
  ///
  /// Returns nothing on success. The backend decides everything that
  /// matters — overlaps, insufficient balance, past dates, non-working
  /// days — and explains which rule was broken. We pass its words through.
  Future<void> applyForLeave({
    required int leaveTypeId,
    required DateTime startDate,
    required DateTime endDate,
    required String reason,
  }) async {
    try {
      await dio.post<void>(
        '/leave/requests/',
        data: <String, dynamic>{
          'leave_type': leaveTypeId,
          'start_date': _asDate(startDate),
          'end_date': _asDate(endDate),
          'reason': reason,
        },
      );
    } on DioException catch (error) {
      throw toFailure(error);
    }
  }

  /// Django wants YYYY-MM-DD, not a full timestamp.
  ///
  /// toIso8601String uses local time with no zone suffix, so taking the
  /// part before the T gives the date the user actually picked — not the
  /// day before, which is what happens if you convert to UTC first.
  String _asDate(DateTime value) => value.toIso8601String().split('T').first;

}

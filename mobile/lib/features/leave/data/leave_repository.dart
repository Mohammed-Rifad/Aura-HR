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
}

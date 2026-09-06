import 'package:aura_hr/core/providers.dart';
import 'package:aura_hr/features/auth/presentation/auth_controller.dart';
import 'package:aura_hr/features/leave/data/leave_repository.dart';
import 'package:aura_hr/features/leave/domain/leave_balance.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'leave_providers.g.dart';

@riverpod
LeaveRepository leaveRepository(Ref ref) =>
    LeaveRepository(dio: ref.watch(apiClientProvider));

/// The signed-in person's leave balances.
///
/// An empty list for accounts with no employee record — HR and Admin often
/// have none, and that is not an error.
@riverpod
Future<List<LeaveBalance>> leaveBalances(Ref ref) async {
  final employeeId = ref.watch(authControllerProvider).value?.employee?.id;
  if (employeeId == null) return const [];

    return await ref.watch(leaveRepositoryProvider).balances(employeeId);

}

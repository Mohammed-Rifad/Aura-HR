// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'leave_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(leaveRepository)
final leaveRepositoryProvider = LeaveRepositoryProvider._();

final class LeaveRepositoryProvider
    extends
        $FunctionalProvider<LeaveRepository, LeaveRepository, LeaveRepository>
    with $Provider<LeaveRepository> {
  LeaveRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'leaveRepositoryProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$leaveRepositoryHash();

  @$internal
  @override
  $ProviderElement<LeaveRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  LeaveRepository create(Ref ref) {
    return leaveRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(LeaveRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<LeaveRepository>(value),
    );
  }
}

String _$leaveRepositoryHash() => r'4e4fa7c7e2a6e77d7bc2161d7365dbb0de955072';

/// The signed-in person's leave balances.
///
/// An empty list for accounts with no employee record — HR and Admin often
/// have none, and that is not an error.

@ProviderFor(leaveBalances)
final leaveBalancesProvider = LeaveBalancesProvider._();

/// The signed-in person's leave balances.
///
/// An empty list for accounts with no employee record — HR and Admin often
/// have none, and that is not an error.

final class LeaveBalancesProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<LeaveBalance>>,
          List<LeaveBalance>,
          FutureOr<List<LeaveBalance>>
        >
    with
        $FutureModifier<List<LeaveBalance>>,
        $FutureProvider<List<LeaveBalance>> {
  /// The signed-in person's leave balances.
  ///
  /// An empty list for accounts with no employee record — HR and Admin often
  /// have none, and that is not an error.
  LeaveBalancesProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'leaveBalancesProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$leaveBalancesHash();

  @$internal
  @override
  $FutureProviderElement<List<LeaveBalance>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<LeaveBalance>> create(Ref ref) {
    return leaveBalances(ref);
  }
}

String _$leaveBalancesHash() => r'98a15ad581d38db911fae072fa6bef460fc9fcc2';

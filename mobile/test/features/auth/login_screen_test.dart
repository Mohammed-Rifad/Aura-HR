import 'package:aura_hr/core/failure.dart';
import 'package:aura_hr/core/providers.dart';
import 'package:aura_hr/core/token_storage.dart';
import 'package:aura_hr/features/auth/data/auth_repository.dart';
import 'package:aura_hr/features/auth/domain/user.dart';
import 'package:aura_hr/features/auth/presentation/auth_controller.dart';
import 'package:aura_hr/features/auth/presentation/login_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class _MockStorage extends Mock implements TokenStorage;

class _MockAuthRepository extends Mock implements AuthRepository;

const _user = User(
  id: 'a1',
  email: 'manager@aurahr.com',
  role: Role.manager,
  fullName: 'A Manager',
  isVerified: true,
);

void main() {
  late _MockStorage storage;
  late _MockAuthRepository repository;

  setUp(() {
    storage = _MockStorage();
    repository = _MockAuthRepository();

    // No saved token, so AuthController.build() reports signed-out without
    // touching the network.
    when(() => storage.hasSession).thenAnswer((_) async => false);
  });

  /// Builds the screen with the real controller but fake dependencies.
  Future<void> pumpLogin(WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          tokenStorageProvider.overrideWithValue(storage),
          authRepositoryProvider.overrideWithValue(repository),
        ],
        child: const MaterialApp(home: LoginScreen()),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets('will not submit an empty form', (tester) async {
    await pumpLogin(tester);

    await tester.tap(find.text('Sign in'));
    await tester.pump();

    expect(find.text('Enter a valid email address'), findsOneWidget);
    expect(find.text('Enter your password'), findsOneWidget);

    // Nothing was sent. Validating in the browser is a courtesy, but it
    // should at least stop an obviously empty request.
    verifyNever(
      () => repository.login(
        email: any(named: 'email'),
        password: any(named: 'password'),
      ),
    );
  });

  testWidgets('sends what was typed', (tester) async {
    when(
      () => repository.login(
        email: any(named: 'email'),
        password: any(named: 'password'),
      ),
    ).thenAnswer((_) async => _user);

    await pumpLogin(tester);

    await tester.enterText(
      find.byType(TextFormField).first,
      '  manager@aurahr.com  ',
    );
    await tester.enterText(find.byType(TextFormField).last, 'Password@123');
    await tester.tap(find.text('Sign in'));
    await tester.pumpAndSettle();

    // Trimmed — a stray space copied from an email is not a wrong password.
    verify(
      () => repository.login(
        email: 'manager@aurahr.com',
        password: 'Password@123',
      ),
    ).called(1);
  });

  testWidgets("shows the server's message when login fails", (tester) async {
    when(
      () => repository.login(
        email: any(named: 'email'),
        password: any(named: 'password'),
      ),
    ).thenThrow(const AuthFailure('Incorrect email or password.'));

    await pumpLogin(tester);

    await tester.enterText(
      find.byType(TextFormField).first,
      'manager@aurahr.com',
    );
    await tester.enterText(find.byType(TextFormField).last, 'wrong');
    await tester.tap(find.text('Sign in'));
    await tester.pumpAndSettle();

    expect(find.text('Incorrect email or password.'), findsOneWidget);
  });
}

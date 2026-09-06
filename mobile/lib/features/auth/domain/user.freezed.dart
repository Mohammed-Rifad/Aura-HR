// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'user.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$EmployeeRef {

 String get id;@JsonKey(name: 'employee_id') String get employeeId;
/// Create a copy of EmployeeRef
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EmployeeRefCopyWith<EmployeeRef> get copyWith => _$EmployeeRefCopyWithImpl<EmployeeRef>(this as EmployeeRef, _$identity);

  /// Serializes this EmployeeRef to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as EmployeeRef;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EmployeeRef&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.employeeId, _this.employeeId) || other.employeeId == _this.employeeId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as EmployeeRef;
  return Object.hash(runtimeType,_this.id,_this.employeeId);
}

@override
String toString() {
  final _this = this as EmployeeRef;
  return 'EmployeeRef(id: ${_this.id}, employeeId: ${_this.employeeId})';
}


}

/// @nodoc
abstract mixin class $EmployeeRefCopyWith<$Res>  {
  factory $EmployeeRefCopyWith(EmployeeRef value, $Res Function(EmployeeRef) _then) = _$EmployeeRefCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'employee_id') String employeeId
});




}
/// @nodoc
class _$EmployeeRefCopyWithImpl<$Res>
    implements $EmployeeRefCopyWith<$Res> {
  _$EmployeeRefCopyWithImpl(this._self, this._then);

  final EmployeeRef _self;
  final $Res Function(EmployeeRef) _then;

/// Create a copy of EmployeeRef
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? employeeId = null,}) {
  return _then(EmployeeRef(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,employeeId: null == employeeId ? _self.employeeId : employeeId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [EmployeeRef].
extension EmployeeRefPatterns on EmployeeRef {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EmployeeRef value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EmployeeRef() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EmployeeRef value)  $default,){
final _that = this;
switch (_that) {
case _EmployeeRef():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EmployeeRef value)?  $default,){
final _that = this;
switch (_that) {
case _EmployeeRef() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'employee_id')  String employeeId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EmployeeRef() when $default != null:
return $default(_that.id,_that.employeeId);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'employee_id')  String employeeId)  $default,) {final _that = this;
switch (_that) {
case _EmployeeRef():
return $default(_that.id,_that.employeeId);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'employee_id')  String employeeId)?  $default,) {final _that = this;
switch (_that) {
case _EmployeeRef() when $default != null:
return $default(_that.id,_that.employeeId);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EmployeeRef implements EmployeeRef {
  const _EmployeeRef({required this.id, @JsonKey(name: 'employee_id') required this.employeeId});
  factory _EmployeeRef.fromJson(Map<String, dynamic> json) => _$EmployeeRefFromJson(json);

@override final  String id;
@override@JsonKey(name: 'employee_id') final  String employeeId;

/// Create a copy of EmployeeRef
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EmployeeRefCopyWith<_EmployeeRef> get copyWith => __$EmployeeRefCopyWithImpl<_EmployeeRef>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EmployeeRefToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _EmployeeRef&&(identical(other.id, id) || other.id == id)&&(identical(other.employeeId, employeeId) || other.employeeId == employeeId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,employeeId);
}

@override
String toString() {
    return 'EmployeeRef(id: $id, employeeId: $employeeId)';
}


}

/// @nodoc
abstract mixin class _$EmployeeRefCopyWith<$Res> implements $EmployeeRefCopyWith<$Res> {
  factory _$EmployeeRefCopyWith(_EmployeeRef value, $Res Function(_EmployeeRef) _then) = __$EmployeeRefCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'employee_id') String employeeId
});




}
/// @nodoc
class __$EmployeeRefCopyWithImpl<$Res>
    implements _$EmployeeRefCopyWith<$Res> {
  __$EmployeeRefCopyWithImpl(this._self, this._then);

  final _EmployeeRef _self;
  final $Res Function(_EmployeeRef) _then;

/// Create a copy of EmployeeRef
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? employeeId = null,}) {
  return _then(_EmployeeRef(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,employeeId: null == employeeId ? _self.employeeId : employeeId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$User {

 String get id; String get email; Role get role;@JsonKey(name: 'full_name') String get fullName;@JsonKey(name: 'is_verified') bool get isVerified; EmployeeRef? get employee;
/// Create a copy of User
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserCopyWith<User> get copyWith => _$UserCopyWithImpl<User>(this as User, _$identity);

  /// Serializes this User to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as User;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is User&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.email, _this.email) || other.email == _this.email)&&(identical(other.role, _this.role) || other.role == _this.role)&&(identical(other.fullName, _this.fullName) || other.fullName == _this.fullName)&&(identical(other.isVerified, _this.isVerified) || other.isVerified == _this.isVerified)&&(identical(other.employee, _this.employee) || other.employee == _this.employee));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as User;
  return Object.hash(runtimeType,_this.id,_this.email,_this.role,_this.fullName,_this.isVerified,_this.employee);
}

@override
String toString() {
  final _this = this as User;
  return 'User(id: ${_this.id}, email: ${_this.email}, role: ${_this.role}, fullName: ${_this.fullName}, isVerified: ${_this.isVerified}, employee: ${_this.employee})';
}


}

/// @nodoc
abstract mixin class $UserCopyWith<$Res>  {
  factory $UserCopyWith(User value, $Res Function(User) _then) = _$UserCopyWithImpl;
@useResult
$Res call({
 String id, String email, Role role,@JsonKey(name: 'full_name') String fullName,@JsonKey(name: 'is_verified') bool isVerified, EmployeeRef? employee
});


$EmployeeRefCopyWith<$Res>? get employee;

}
/// @nodoc
class _$UserCopyWithImpl<$Res>
    implements $UserCopyWith<$Res> {
  _$UserCopyWithImpl(this._self, this._then);

  final User _self;
  final $Res Function(User) _then;

/// Create a copy of User
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? email = null,Object? role = null,Object? fullName = null,Object? isVerified = null,Object? employee = freezed,}) {
  return _then(User(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as Role,fullName: null == fullName ? _self.fullName : fullName // ignore: cast_nullable_to_non_nullable
as String,isVerified: null == isVerified ? _self.isVerified : isVerified // ignore: cast_nullable_to_non_nullable
as bool,employee: freezed == employee ? _self.employee : employee // ignore: cast_nullable_to_non_nullable
as EmployeeRef?,
  ));
}
/// Create a copy of User
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$EmployeeRefCopyWith<$Res>? get employee {
    if (_self.employee == null) {
    return null;
  }

  return $EmployeeRefCopyWith<$Res>(_self.employee!, (value) {
    return _then(_self.copyWith(employee: value));
  });
}
}


/// Adds pattern-matching-related methods to [User].
extension UserPatterns on User {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _User value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _User() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _User value)  $default,){
final _that = this;
switch (_that) {
case _User():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _User value)?  $default,){
final _that = this;
switch (_that) {
case _User() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String email,  Role role, @JsonKey(name: 'full_name')  String fullName, @JsonKey(name: 'is_verified')  bool isVerified,  EmployeeRef? employee)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _User() when $default != null:
return $default(_that.id,_that.email,_that.role,_that.fullName,_that.isVerified,_that.employee);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String email,  Role role, @JsonKey(name: 'full_name')  String fullName, @JsonKey(name: 'is_verified')  bool isVerified,  EmployeeRef? employee)  $default,) {final _that = this;
switch (_that) {
case _User():
return $default(_that.id,_that.email,_that.role,_that.fullName,_that.isVerified,_that.employee);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String email,  Role role, @JsonKey(name: 'full_name')  String fullName, @JsonKey(name: 'is_verified')  bool isVerified,  EmployeeRef? employee)?  $default,) {final _that = this;
switch (_that) {
case _User() when $default != null:
return $default(_that.id,_that.email,_that.role,_that.fullName,_that.isVerified,_that.employee);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _User implements User {
  const _User({required this.id, required this.email, required this.role, @JsonKey(name: 'full_name') required this.fullName, @JsonKey(name: 'is_verified') required this.isVerified, this.employee});
  factory _User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);

@override final  String id;
@override final  String email;
@override final  Role role;
@override@JsonKey(name: 'full_name') final  String fullName;
@override@JsonKey(name: 'is_verified') final  bool isVerified;
@override final  EmployeeRef? employee;

/// Create a copy of User
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserCopyWith<_User> get copyWith => __$UserCopyWithImpl<_User>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _User&&(identical(other.id, id) || other.id == id)&&(identical(other.email, email) || other.email == email)&&(identical(other.role, role) || other.role == role)&&(identical(other.fullName, fullName) || other.fullName == fullName)&&(identical(other.isVerified, isVerified) || other.isVerified == isVerified)&&(identical(other.employee, employee) || other.employee == employee));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,email,role,fullName,isVerified,employee);
}

@override
String toString() {
    return 'User(id: $id, email: $email, role: $role, fullName: $fullName, isVerified: $isVerified, employee: $employee)';
}


}

/// @nodoc
abstract mixin class _$UserCopyWith<$Res> implements $UserCopyWith<$Res> {
  factory _$UserCopyWith(_User value, $Res Function(_User) _then) = __$UserCopyWithImpl;
@override @useResult
$Res call({
 String id, String email, Role role,@JsonKey(name: 'full_name') String fullName,@JsonKey(name: 'is_verified') bool isVerified, EmployeeRef? employee
});


@override $EmployeeRefCopyWith<$Res>? get employee;

}
/// @nodoc
class __$UserCopyWithImpl<$Res>
    implements _$UserCopyWith<$Res> {
  __$UserCopyWithImpl(this._self, this._then);

  final _User _self;
  final $Res Function(_User) _then;

/// Create a copy of User
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? email = null,Object? role = null,Object? fullName = null,Object? isVerified = null,Object? employee = freezed,}) {
  return _then(_User(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as Role,fullName: null == fullName ? _self.fullName : fullName // ignore: cast_nullable_to_non_nullable
as String,isVerified: null == isVerified ? _self.isVerified : isVerified // ignore: cast_nullable_to_non_nullable
as bool,employee: freezed == employee ? _self.employee : employee // ignore: cast_nullable_to_non_nullable
as EmployeeRef?,
  ));
}

/// Create a copy of User
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$EmployeeRefCopyWith<$Res>? get employee {
    if (_self.employee == null) {
    return null;
  }

  return $EmployeeRefCopyWith<$Res>(_self.employee!, (value) {
    return _then(_self.copyWith(employee: value));
  });
}
}

// dart format on

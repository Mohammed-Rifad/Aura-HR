// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'leave_balance.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$LeaveTypeRef {

 int get id; String get name; String get code;
/// Create a copy of LeaveTypeRef
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LeaveTypeRefCopyWith<LeaveTypeRef> get copyWith => _$LeaveTypeRefCopyWithImpl<LeaveTypeRef>(this as LeaveTypeRef, _$identity);

  /// Serializes this LeaveTypeRef to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as LeaveTypeRef;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LeaveTypeRef&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.name, _this.name) || other.name == _this.name)&&(identical(other.code, _this.code) || other.code == _this.code));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as LeaveTypeRef;
  return Object.hash(runtimeType,_this.id,_this.name,_this.code);
}

@override
String toString() {
  final _this = this as LeaveTypeRef;
  return 'LeaveTypeRef(id: ${_this.id}, name: ${_this.name}, code: ${_this.code})';
}


}

/// @nodoc
abstract mixin class $LeaveTypeRefCopyWith<$Res>  {
  factory $LeaveTypeRefCopyWith(LeaveTypeRef value, $Res Function(LeaveTypeRef) _then) = _$LeaveTypeRefCopyWithImpl;
@useResult
$Res call({
 int id, String name, String code
});




}
/// @nodoc
class _$LeaveTypeRefCopyWithImpl<$Res>
    implements $LeaveTypeRefCopyWith<$Res> {
  _$LeaveTypeRefCopyWithImpl(this._self, this._then);

  final LeaveTypeRef _self;
  final $Res Function(LeaveTypeRef) _then;

/// Create a copy of LeaveTypeRef
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? code = null,}) {
  return _then(LeaveTypeRef(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,code: null == code ? _self.code : code // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [LeaveTypeRef].
extension LeaveTypeRefPatterns on LeaveTypeRef {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LeaveTypeRef value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LeaveTypeRef() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LeaveTypeRef value)  $default,){
final _that = this;
switch (_that) {
case _LeaveTypeRef():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LeaveTypeRef value)?  $default,){
final _that = this;
switch (_that) {
case _LeaveTypeRef() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String name,  String code)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LeaveTypeRef() when $default != null:
return $default(_that.id,_that.name,_that.code);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String name,  String code)  $default,) {final _that = this;
switch (_that) {
case _LeaveTypeRef():
return $default(_that.id,_that.name,_that.code);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String name,  String code)?  $default,) {final _that = this;
switch (_that) {
case _LeaveTypeRef() when $default != null:
return $default(_that.id,_that.name,_that.code);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LeaveTypeRef implements LeaveTypeRef {
  const _LeaveTypeRef({required this.id, required this.name, required this.code});
  factory _LeaveTypeRef.fromJson(Map<String, dynamic> json) => _$LeaveTypeRefFromJson(json);

@override final  int id;
@override final  String name;
@override final  String code;

/// Create a copy of LeaveTypeRef
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LeaveTypeRefCopyWith<_LeaveTypeRef> get copyWith => __$LeaveTypeRefCopyWithImpl<_LeaveTypeRef>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LeaveTypeRefToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _LeaveTypeRef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.code, code) || other.code == code));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,name,code);
}

@override
String toString() {
    return 'LeaveTypeRef(id: $id, name: $name, code: $code)';
}


}

/// @nodoc
abstract mixin class _$LeaveTypeRefCopyWith<$Res> implements $LeaveTypeRefCopyWith<$Res> {
  factory _$LeaveTypeRefCopyWith(_LeaveTypeRef value, $Res Function(_LeaveTypeRef) _then) = __$LeaveTypeRefCopyWithImpl;
@override @useResult
$Res call({
 int id, String name, String code
});




}
/// @nodoc
class __$LeaveTypeRefCopyWithImpl<$Res>
    implements _$LeaveTypeRefCopyWith<$Res> {
  __$LeaveTypeRefCopyWithImpl(this._self, this._then);

  final _LeaveTypeRef _self;
  final $Res Function(_LeaveTypeRef) _then;

/// Create a copy of LeaveTypeRef
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? code = null,}) {
  return _then(_LeaveTypeRef(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,code: null == code ? _self.code : code // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$LeaveBalance {

 int get id;@JsonKey(name: 'leave_type') LeaveTypeRef get leaveType; int get year; String get allocated; String get used; String get pending; String get available;
/// Create a copy of LeaveBalance
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LeaveBalanceCopyWith<LeaveBalance> get copyWith => _$LeaveBalanceCopyWithImpl<LeaveBalance>(this as LeaveBalance, _$identity);

  /// Serializes this LeaveBalance to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as LeaveBalance;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LeaveBalance&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.leaveType, _this.leaveType) || other.leaveType == _this.leaveType)&&(identical(other.year, _this.year) || other.year == _this.year)&&(identical(other.allocated, _this.allocated) || other.allocated == _this.allocated)&&(identical(other.used, _this.used) || other.used == _this.used)&&(identical(other.pending, _this.pending) || other.pending == _this.pending)&&(identical(other.available, _this.available) || other.available == _this.available));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as LeaveBalance;
  return Object.hash(runtimeType,_this.id,_this.leaveType,_this.year,_this.allocated,_this.used,_this.pending,_this.available);
}

@override
String toString() {
  final _this = this as LeaveBalance;
  return 'LeaveBalance(id: ${_this.id}, leaveType: ${_this.leaveType}, year: ${_this.year}, allocated: ${_this.allocated}, used: ${_this.used}, pending: ${_this.pending}, available: ${_this.available})';
}


}

/// @nodoc
abstract mixin class $LeaveBalanceCopyWith<$Res>  {
  factory $LeaveBalanceCopyWith(LeaveBalance value, $Res Function(LeaveBalance) _then) = _$LeaveBalanceCopyWithImpl;
@useResult
$Res call({
 int id,@JsonKey(name: 'leave_type') LeaveTypeRef leaveType, int year, String allocated, String used, String pending, String available
});


$LeaveTypeRefCopyWith<$Res> get leaveType;

}
/// @nodoc
class _$LeaveBalanceCopyWithImpl<$Res>
    implements $LeaveBalanceCopyWith<$Res> {
  _$LeaveBalanceCopyWithImpl(this._self, this._then);

  final LeaveBalance _self;
  final $Res Function(LeaveBalance) _then;

/// Create a copy of LeaveBalance
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? leaveType = null,Object? year = null,Object? allocated = null,Object? used = null,Object? pending = null,Object? available = null,}) {
  return _then(LeaveBalance(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,leaveType: null == leaveType ? _self.leaveType : leaveType // ignore: cast_nullable_to_non_nullable
as LeaveTypeRef,year: null == year ? _self.year : year // ignore: cast_nullable_to_non_nullable
as int,allocated: null == allocated ? _self.allocated : allocated // ignore: cast_nullable_to_non_nullable
as String,used: null == used ? _self.used : used // ignore: cast_nullable_to_non_nullable
as String,pending: null == pending ? _self.pending : pending // ignore: cast_nullable_to_non_nullable
as String,available: null == available ? _self.available : available // ignore: cast_nullable_to_non_nullable
as String,
  ));
}
/// Create a copy of LeaveBalance
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LeaveTypeRefCopyWith<$Res> get leaveType {
  
  return $LeaveTypeRefCopyWith<$Res>(_self.leaveType, (value) {
    return _then(_self.copyWith(leaveType: value));
  });
}
}


/// Adds pattern-matching-related methods to [LeaveBalance].
extension LeaveBalancePatterns on LeaveBalance {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LeaveBalance value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LeaveBalance() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LeaveBalance value)  $default,){
final _that = this;
switch (_that) {
case _LeaveBalance():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LeaveBalance value)?  $default,){
final _that = this;
switch (_that) {
case _LeaveBalance() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id, @JsonKey(name: 'leave_type')  LeaveTypeRef leaveType,  int year,  String allocated,  String used,  String pending,  String available)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LeaveBalance() when $default != null:
return $default(_that.id,_that.leaveType,_that.year,_that.allocated,_that.used,_that.pending,_that.available);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id, @JsonKey(name: 'leave_type')  LeaveTypeRef leaveType,  int year,  String allocated,  String used,  String pending,  String available)  $default,) {final _that = this;
switch (_that) {
case _LeaveBalance():
return $default(_that.id,_that.leaveType,_that.year,_that.allocated,_that.used,_that.pending,_that.available);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id, @JsonKey(name: 'leave_type')  LeaveTypeRef leaveType,  int year,  String allocated,  String used,  String pending,  String available)?  $default,) {final _that = this;
switch (_that) {
case _LeaveBalance() when $default != null:
return $default(_that.id,_that.leaveType,_that.year,_that.allocated,_that.used,_that.pending,_that.available);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LeaveBalance implements LeaveBalance {
  const _LeaveBalance({required this.id, @JsonKey(name: 'leave_type') required this.leaveType, required this.year, required this.allocated, required this.used, required this.pending, required this.available});
  factory _LeaveBalance.fromJson(Map<String, dynamic> json) => _$LeaveBalanceFromJson(json);

@override final  int id;
@override@JsonKey(name: 'leave_type') final  LeaveTypeRef leaveType;
@override final  int year;
@override final  String allocated;
@override final  String used;
@override final  String pending;
@override final  String available;

/// Create a copy of LeaveBalance
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LeaveBalanceCopyWith<_LeaveBalance> get copyWith => __$LeaveBalanceCopyWithImpl<_LeaveBalance>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LeaveBalanceToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _LeaveBalance&&(identical(other.id, id) || other.id == id)&&(identical(other.leaveType, leaveType) || other.leaveType == leaveType)&&(identical(other.year, year) || other.year == year)&&(identical(other.allocated, allocated) || other.allocated == allocated)&&(identical(other.used, used) || other.used == used)&&(identical(other.pending, pending) || other.pending == pending)&&(identical(other.available, available) || other.available == available));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,leaveType,year,allocated,used,pending,available);
}

@override
String toString() {
    return 'LeaveBalance(id: $id, leaveType: $leaveType, year: $year, allocated: $allocated, used: $used, pending: $pending, available: $available)';
}


}

/// @nodoc
abstract mixin class _$LeaveBalanceCopyWith<$Res> implements $LeaveBalanceCopyWith<$Res> {
  factory _$LeaveBalanceCopyWith(_LeaveBalance value, $Res Function(_LeaveBalance) _then) = __$LeaveBalanceCopyWithImpl;
@override @useResult
$Res call({
 int id,@JsonKey(name: 'leave_type') LeaveTypeRef leaveType, int year, String allocated, String used, String pending, String available
});


@override $LeaveTypeRefCopyWith<$Res> get leaveType;

}
/// @nodoc
class __$LeaveBalanceCopyWithImpl<$Res>
    implements _$LeaveBalanceCopyWith<$Res> {
  __$LeaveBalanceCopyWithImpl(this._self, this._then);

  final _LeaveBalance _self;
  final $Res Function(_LeaveBalance) _then;

/// Create a copy of LeaveBalance
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? leaveType = null,Object? year = null,Object? allocated = null,Object? used = null,Object? pending = null,Object? available = null,}) {
  return _then(_LeaveBalance(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,leaveType: null == leaveType ? _self.leaveType : leaveType // ignore: cast_nullable_to_non_nullable
as LeaveTypeRef,year: null == year ? _self.year : year // ignore: cast_nullable_to_non_nullable
as int,allocated: null == allocated ? _self.allocated : allocated // ignore: cast_nullable_to_non_nullable
as String,used: null == used ? _self.used : used // ignore: cast_nullable_to_non_nullable
as String,pending: null == pending ? _self.pending : pending // ignore: cast_nullable_to_non_nullable
as String,available: null == available ? _self.available : available // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

/// Create a copy of LeaveBalance
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LeaveTypeRefCopyWith<$Res> get leaveType {
  
  return $LeaveTypeRefCopyWith<$Res>(_self.leaveType, (value) {
    return _then(_self.copyWith(leaveType: value));
  });
}
}

// dart format on

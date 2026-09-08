import 'dart:convert';

import 'package:aura_hr/core/api_client.dart';
import 'package:aura_hr/features/assistant/domain/chat_event.dart';
import 'package:dio/dio.dart';

class AssistantRepository {
  const AssistantRepository({required this.dio});

  final Dio dio;

  /// Asks a question and yields each event as it arrives.
  Stream<ChatEvent> ask({
    required String message,
    String? conversationId,
  }) async* {
    final response = await dio.post<ResponseBody>(
      '/ai/chat/stream/',
      data: <String, dynamic>{
        'message': message,
        // The ? drops the entry entirely when conversationId is null —
        // starting a new conversation rather than continuing one.
        'conversation': ?conversationId,
      },
      // Without this, dio waits for the whole body before returning — which
      // would collect every event and hand them over at the end, defeating
      // the point.
      options: Options(responseType: ResponseType.stream),
    );

    var buffer = '';

    await for (final chunk in response.data!.stream) {
      // A StringBuffer cannot do what this needs: we append, then split and
      // keep the leftover. Slicing an accumulated String is the point here.
      // ignore: use_string_buffers
      buffer += utf8.decode(chunk, allowMalformed: true);

      // Events are separated by a blank line. Network chunks do NOT line up
      // with event boundaries — one chunk can hold two events, or half of
      // one. Whatever follows the last blank line is incomplete, so it stays
      // in the buffer until the rest arrives.
      final parts = buffer.split('\n\n');
      buffer = parts.removeLast();

      for (final part in parts) {
        final line = part.trim();
        if (!line.startsWith('data:')) continue;

        yield ChatEvent.fromJson(
          jsonDecode(line.substring(5)) as Map<String, dynamic>,
        );
      }
    }
  }

  /// Approves or rejects something the agent proposed.
  Future<String> decide({
    required String actionId,
    required bool approve,
  }) async {
    try {
      final response = await dio.post<Map<String, dynamic>>(
        '/ai/actions/$actionId/${approve ? 'approve' : 'reject'}/',
        data: const <String, dynamic>{},
      );
      return response.data!['answer'] as String;
    } on DioException catch (error) {
      throw toFailure(error);
    }
  }
}

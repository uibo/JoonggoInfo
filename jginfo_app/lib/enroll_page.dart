import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;


final formProvider = StateNotifierProvider<FormNotifier, Map<String, dynamic>>((ref) => FormNotifier());
class FormNotifier extends StateNotifier<Map<String, dynamic>> {
  FormNotifier() : super({
    '기스': false, '흠집': false, '찍힘': false, '파손': false, 
    '잔상': false, '미개봉': false, '애플케어플러스': false
  });

  void updateField(String field, dynamic value) => state = {...state, field: value};
  void updateOption(String option) => state = {...state, option: !state[option]};
}

final responseProvider = StateNotifierProvider<ResponseNotifier, Map<String, dynamic>>((ref) => ResponseNotifier());
class ResponseNotifier extends StateNotifier<Map<String, dynamic>> {
  ResponseNotifier() : super({});

  Future<void> submitForm(Map<String, dynamic> data) async {
    try {
      final featureList = data.entries
        .where((entry) => ['기스', '흠집', '찍힘', '파손', '잔상', '미개봉', '애플케어플러스'].contains(entry.key) && entry.value == true)
        .map((e) => e.key)
        .toList();

      featureList.add(data.entries
        .where((entry) => entry.value.toString().endsWith("GB"))
        .map((e) => e.value).first
      );

      final queryParams = Map<String, dynamic>.from(data)
        ..removeWhere((key, _) => ['기스', '흠집', '찍힘', '파손', '잔상', '미개봉', '애플케어플러스'].contains(key))
        ..addAll({'feature_list': featureList});

      final response = await http.post(
        Uri.parse('http://127.0.01:8000/iPhone14_processed_info/'),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: json.encode(queryParams),
      );

      if (response.statusCode == 201) {
        state = json.decode(utf8.decode(response.bodyBytes));
      } else {
        state = {'error': '요청 실패 (${response.statusCode})'};
      }
    } catch (e) {
      state = {'error': '오류 발생: $e'};
    }
  }
}

class InputFormWidget extends ConsumerWidget {
  const InputFormWidget({super.key});

  String _getHintText(String field) {
  switch (field) {
    case 'model':
      return 'ex. iPhone14';
    case 'storage':
      return 'ex. 256GB';
    case 'battery':
      return '0~100, 미설정 0';
    case 'price':
      return 'ex. 1000000';
    case 'location':
      return 'ex. 상하동';
    case 'upload_date':
      return 'ex. 2024-12-01';
    case 'status':
      return '0 or 1';
    case 'imgUrl':
      return 'ex. http://test.img';
    case 'url':
      return 'ex. http://test.html';
    default:
      return '';
  }
}

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Row(
      children: [
        Expanded(
          child: Column(
            children: [
  ...['model', 'storage' ,'battery', 'upload_date', 'price', 'status', 'location', 'imgUrl', 'url']
    .map((field) => Focus(
      child: Builder(
        builder: (context) {
          final hasFocus = Focus.of(context).hasFocus;
          
          return TextField(
            decoration: InputDecoration(
              labelText: field,
              hintText: hasFocus ? null : _getHintText(field), // focus 시 hint 제거
              floatingLabelBehavior: FloatingLabelBehavior.always,
              floatingLabelStyle: const TextStyle(fontSize: 14),
            ),
            keyboardType: ['battery', 'price', 'status'].contains(field) 
              ? TextInputType.number 
              : null,
            inputFormatters: ['battery', 'price', 'status'].contains(field) 
              ? [FilteringTextInputFormatter.digitsOnly] 
              : null,
            onChanged: (value) => ref.read(formProvider.notifier).updateField(
              field, 
              ['battery', 'price', 'status'].contains(field) 
                ? int.tryParse(value) 
                : value
            ),
          );
        }
      ),
    )),
              Wrap(
                spacing: 10,
                children: ['기스', '흠집', '찍힘', '파손', '잔상', '미개봉', '애플케어플러스']
                  .map((option) => OptionButton(option: option))
                  .toList(),
              ),
              ElevatedButton(
                onPressed: () => ref.read(responseProvider.notifier).submitForm(ref.read(formProvider)),
                child: const Text('제출'),
              ),
            ],
          ),
        ),
        Expanded(
          child: Card(
            margin: const EdgeInsets.only(left: 16),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Consumer(
                builder: (context, ref, _) {
                  final response = ref.watch(responseProvider);
                  if (response.isEmpty) {
                    return const Text('응답 대기중');
                  }
                  return response.containsKey('error')
                    ? Text(response['error'], style: const TextStyle(color: Colors.red))
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: response.entries
                        .map((e) => Text('${e.key}: ${e.value}'))
                        .toList(),
                      );
                },
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class OptionButton extends ConsumerWidget {
  final String option;
  const OptionButton({required this.option, super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selected = ref.watch(formProvider)[option] ?? false;
    return OutlinedButton(
      onPressed: () => ref.read(formProvider.notifier).updateOption(option),
      style: OutlinedButton.styleFrom(
        foregroundColor: selected ? Colors.white : const Color(0xFF495057),
        backgroundColor: selected ? const Color(0xFF495057) : Colors.white,
        side: const BorderSide(
          width: 2,
          color: Color(0xFF495057),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(6),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      child: Text(option),
    );
  }
}

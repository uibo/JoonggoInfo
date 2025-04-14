import 'dart:convert';
import 'package:flutter/material.dart';

import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import 'common_widget.dart';

class ListPage extends ConsumerStatefulWidget {
  const ListPage({super.key});

  @override
  ListPageState createState() => ListPageState();
}
class ListPageState extends ConsumerState<ListPage> {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [ 
        SettingBar(onPressedToRefesh: () {ref.read(itemsProvider.notifier).refresh();},),
        const Expanded(
          child: ListComponent(),
        ),
      ]
    );
  }
}

class ListComponent extends ConsumerStatefulWidget {
  const ListComponent ({super.key});

  @override
  ListComponentState createState() => ListComponentState();
}
class ListComponentState extends ConsumerState<ListComponent> {
  @override
  Widget build(BuildContext context) {
    final itemsData = ref.watch(itemsProvider);

    return itemsData.when(
      data: (itemsData) {
        return GridView.builder(
          itemCount: itemsData.length,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 4),
          itemBuilder: (context, index) {
            Map item = itemsData[index];
            return Card(  
              child: ItemCard(item: item),
            );
          },
        );
      },
      error: (error, stacktrace) {return const Text('failed loading data');}, 
      loading: () => const Center(child: CircularProgressIndicator()),
    );
  }
}

final itemsProvider = StateNotifierProvider<ItemsNotifier, AsyncValue<List>>((ref) => ItemsNotifier(ref));
class ItemsNotifier extends StateNotifier<AsyncValue<List>> {
  final Ref ref;
  late Settings settings;

  ItemsNotifier(this.ref) : super(const AsyncValue.data([])) {
    settings = ref.read(settingsProvider);
  }

  Uri creatUrlFromsettings() {
    String status='';
    if (settings.saleStatus.contains(SaleStatus.selling)) status += '0';
    if (settings.saleStatus.contains(SaleStatus.soldout)) status += '1';
    String featureList = '';
    settings.options.forEach(
      (key, value) {
        if (value == true) {featureList += '1';}
        else {featureList += '0';}
      }
    );
    const baseUrl = 'http://127.0.0.1:8000/iPhone14_processed_info/';
    final queryParams = {
      'search_date': settings.fromDate + settings.toDate,
      'battery': settings.battery,
      'status': status,
      'feature_list': featureList,
    };
    if (settings.model != 'All') {
      if (settings.model == 'Normal') {queryParams['model'] = settings.product;}
      else {queryParams['model'] = settings.product + settings.model;}
    }
    if (settings.storage != 'All') {queryParams['storage'] = settings.storage;}
    return Uri.parse(baseUrl).replace(queryParameters: queryParams);
  }

  Future<void> fetchMalData() async {
    state = const AsyncValue.loading();
    try {
      final url = creatUrlFromsettings();
      final res = await http.get(url);
      state = AsyncValue.data((jsonDecode(utf8.decode(res.bodyBytes)) as List)
          .map((item) => Map<String, dynamic>.from(item))
          .toList());
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  void refresh() {
    settings = ref.read(settingsProvider);
    fetchMalData();
  }
}

final formatter = NumberFormat('#,###');
class ItemCard extends StatelessWidget {
  final Map item;

  const ItemCard({required this.item, super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 100,
      height: 200,
      padding: const EdgeInsets.all(24),
      clipBehavior: Clip.antiAlias,
      decoration: ShapeDecoration(
          color: Colors.white,
          shape: RoundedRectangleBorder(
              side: const BorderSide(width: 2, color: Color(0xFFB1B9C0)),
              borderRadius: BorderRadius.circular(16),
          ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Container(
              alignment: Alignment.center,
              child: Image.network(
                item['imgUrl'],
                  errorBuilder: (context, error, stackTrace) {
                  return Container(
                    width: double.infinity,
                    color: Colors.grey[200],
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.error_outline, size: 40, color: Colors.grey[400]),
                        const SizedBox(height: 8),
                        Text('이미지를 불러올 수 없습니다', 
                          style: TextStyle(color: Colors.grey[600]))
                      ],
                    )
                  );
                }
              )
            ),
          ),
          Text('${item['upload_date']}'),
          const SizedBox(height: 4),
          Text('₩ ${formatter.format(item['price'])}'),
          const SizedBox(height: 4),
          Text(item['model']),
          const SizedBox(height: 4),
          Text('${item['feature_list']}'),
          const SizedBox(height: 4),
          Center(
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 40),
                backgroundColor: const Color(0xFF495057),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8)
                )
              ),
              onPressed: () {
                Uri _url = Uri.parse(item['url']);
                  launchUrl(_url);
              },
              child: const Text(
                'Go to Product Page',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontFamily: 'Open Sans',
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}